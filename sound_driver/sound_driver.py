import asyncio
from pyaudiowpatch import PyAudio, paWASAPI, paInt16
from librosa import resample
from wave import open as waveOpen
import numpy as np
from send_audio import WebSocket
from vocie_activity import is_talking
from yaml import safe_load
from datetime import datetime
from pyperclip import copy as pyperclipCopy
from os import makedirs

def main():
    config = safe_load(open("config.yaml"))
    room_id = input("Choose a room id: ")
    pyperclipCopy(room_id) # Copy the room id to the clipboard
    print(f"Choosen room id \"{room_id}\" has been copied to the clipboard")
    try:
        asyncio.run(sound_driver(room_id, config["ip-address"], bool(config['record-speakers']), config["speaker-id"], config["mic-id"]))
    except Exception as e:
        print("Asyncio unknown exception:", e)

async def sound_driver(room_id, ip_address, record_speakers, speaker_id, mic_id):

    # "MAGIC" PARAMETER NUMBERS
    SILENT_CHUNKS_CUTOFF_WINDOW = 5 #nr (how many chunks of audio must be quitet in a row to send)
    MAX_SILENCE_TIME_BEFORE_VOICE = 3000 #ms (the silence before talking saved to improve start of sentences)
    MAX_SEND_LEN = 5 #sec (max time record before sending)

    audio = PyAudio()
    default_speakers, default_mic = get_default_speaker_and_mic(audio, speaker_id, mic_id)

    if record_speakers:
        print(f"Using mic: {default_mic['name']}, speakers: {default_speakers['name']}")
    else:
        print(f"Using mic: {default_mic['name']}")

    # AUDIO PARAMETERS
    FORMAT = paInt16
    SAMPLE_SIZE = audio.get_sample_size(FORMAT)
    SAMPLE_RATE = 16000
    NUMBER_CHANNELS = 1
    MAX_SEND_SIZE = MAX_SEND_LEN * SAMPLE_RATE
    SPEAKER_RATIO = default_speakers["defaultSampleRate"] / SAMPLE_RATE
    MIC_RATIO = default_mic["defaultSampleRate"] / SAMPLE_RATE
    CHUNK_DURATION = 30 #ms (must be 10, 20 or 30ms because of the VAD restrictions: https://github.com/wiseman/py-webrtcvad)
    SPEAKER_CHUNK = int(CHUNK_DURATION * SAMPLE_RATE * SPEAKER_RATIO / 1000) * 2 # I do not know why * 2 is needed but it does not work without ¯\_(ツ)_/¯
    MIC_CHUNK = int(CHUNK_DURATION * SAMPLE_RATE * MIC_RATIO / 1000) * 2
    
    recording_dir = "recording"
    makedirs(recording_dir, exist_ok=True)

    now_str = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    record_file = waveOpen(f"{recording_dir}/{now_str}_{room_id}.wav", 'wb')
    record_file.setnchannels(NUMBER_CHANNELS)
    record_file.setsampwidth(SAMPLE_SIZE)
    record_file.setframerate(SAMPLE_RATE)   

    send_file = waveOpen(f"{recording_dir}/{now_str}_{room_id}_less_silence.wav", 'wb')
    send_file.setnchannels(NUMBER_CHANNELS)
    send_file.setsampwidth(SAMPLE_SIZE)
    send_file.setframerate(SAMPLE_RATE)   

    speaker_stream = None
    if record_speakers:
        speaker_stream = audio.open(format=FORMAT,
            channels=default_speakers["maxInputChannels"],
            rate=int(default_speakers["defaultSampleRate"]),
            frames_per_buffer=SPEAKER_CHUNK,
            input=True,
            input_device_index=default_speakers["index"],
        )

    mic_stream = audio.open(format=FORMAT, 
        channels=default_mic["maxInputChannels"],
        rate=int(default_mic["defaultSampleRate"]), 
        frames_per_buffer=MIC_CHUNK,
        input=True
    )

    try:
        print("Connecting websocket to room...")
        ws = WebSocket(ip_address, room_id)
        await ws.connect()
        print("Websocket connected")
        
        input("Press ENTER to start the recording:")

        # Loop state variables
        send_data = np.empty(0, dtype=np.int16)
        started_talking = False
        quite_chunk_count = 0
        i = 0
        while True:
            # Nice recording printout
            i = i + 1 if i < 49 else 0
            j = (i // 10) + 1
            print("Recording", j * ".", (5 - j) * " ", sep="", end="\r")

            # Read data from speaker and mic
            if record_speakers: 
                speaker_data = speaker_stream.read(SPEAKER_CHUNK)
                speaker_data = np.frombuffer(speaker_data, dtype=np.int16).astype(np.float32)
                speaker_data = np.reshape(speaker_data, (default_speakers["maxInputChannels"], SPEAKER_CHUNK))
                speaker_data = resample(speaker_data, orig_sr=default_speakers["defaultSampleRate"], target_sr=SAMPLE_RATE)
                speaker_data = np.mean(speaker_data.reshape(-1, default_speakers["maxInputChannels"]), axis=1).astype(np.int16) #mono
            
            mic_data = mic_stream.read(MIC_CHUNK, exception_on_overflow=False)
            mic_data = np.frombuffer(mic_data, dtype=np.int16).astype(np.float32)
            mic_data = np.reshape(mic_data, (default_mic["maxInputChannels"], MIC_CHUNK))
            mic_data = resample(mic_data, orig_sr=default_mic["defaultSampleRate"], target_sr=SAMPLE_RATE)
            mic_data = np.mean(mic_data.reshape(-1, default_mic["maxInputChannels"]), axis=1).astype(np.int16) #mono

            if record_speakers: 
                # Fallback to ensusre to pad the arrays to the same size
                max_length = max(speaker_data.size, mic_data.size)
                speaker_data = np.pad(speaker_data, (0, max_length - speaker_data.size), mode='constant').astype(np.int16)
                mic_data = np.pad(mic_data, (0, max_length - mic_data.size), mode='constant').astype(np.int16)

            combined_data = speaker_data + mic_data if record_speakers else mic_data

            record_file.writeframes(combined_data)

            send_data = np.append(send_data, combined_data).astype(np.int16)
            if is_talking(combined_data, SAMPLE_RATE) and not send_data.size > MAX_SEND_SIZE:
                quite_chunk_count = 0
                started_talking = True
                continue

            if not started_talking:
                # Save the last silent chunks before someone talked to improve the start of segments
                if send_data.size >= combined_data.size*(MAX_SILENCE_TIME_BEFORE_VOICE/CHUNK_DURATION)/2:
                    send_data = send_data[combined_data.size:]

            quite_chunk_count+= 1
            if (quite_chunk_count >= SILENT_CHUNKS_CUTOFF_WINDOW and started_talking) or send_data.size > MAX_SEND_SIZE:
                send_file.writeframes(send_data)
                await ws.send_audio(audio=send_data.tobytes())
                
                # Reset state after sending
                send_data = np.empty(0, dtype=np.int16)
                started_talking = False
                quite_chunk_count = 0

    except KeyboardInterrupt:
        # Graceful exit on keyboard interrupt
        print("\nKeyboard interupt recieved by user. Recording stopped!")
    except Exception as e:
        print(f"\nUnkown exception: {e}.\n\nRecording interupted and stopped!")
    finally:
        # Stop and close
        if record_speakers: 
            speaker_stream.stop_stream()
            speaker_stream.close()
        mic_stream.stop_stream()
        mic_stream.close()
        audio.terminate()

        record_file.close()
        send_file.close()
        await ws.close()

def get_default_speaker_and_mic(audio, speaker_id, mic_id):

    wasapi_info = audio.get_host_api_info_by_type(paWASAPI)

    default_speakers = audio.get_device_info_by_index(wasapi_info["defaultOutputDevice"] if speaker_id is None else speaker_id)
    default_mic = audio.get_device_info_by_index(wasapi_info["defaultInputDevice"] if mic_id is None else mic_id)

    # Try to find loopback device with same name(and [Loopback suffix]).
    if not default_speakers["isLoopbackDevice"]:
        found = False
        for loopback in audio.get_loopback_device_info_generator():
            if default_speakers["name"] in loopback["name"]:
                default_speakers = loopback
                found = True
                break

        # User input fallback if above did not work
        if not found:
            audio.print_detailed_system_info()
            print("\nDefault loopback output device not automatically found!\nAbove is the list of devices and id's.\n")
            while True:
                try:
                    speaker_id = input("Please enter the speaker loopback device id: ")
                    default_speakers = audio.get_device_info_by_index(int(speaker_id))
                    break
                except KeyboardInterrupt:
                    exit()
                except:
                    print("Invalid input. Retry.")

    return default_speakers, default_mic


if __name__ == "__main__":
    main()