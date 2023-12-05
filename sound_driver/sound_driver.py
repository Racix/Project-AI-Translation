import asyncio
from pyaudiowpatch import PyAudio, paWASAPI, paInt16
from librosa import resample
import wave # will get removed after we are done debugging
import numpy as np
from send_audio import WebSocket
from yaml import safe_load
from datetime import datetime
from webrtcvad import Vad
from pyperclip import copy as pyperclipCopy

def main():
    config = safe_load(open("config.yaml"))
    room_id = input("Choose a room id: ")
    pyperclipCopy(room_id) # Copy the room id to the clipboard
    print(f"Choosen room id \"{room_id}\" has been copied to the clipboard")
    asyncio.run(sound_driver(room_id, config["ip-address"], config["speaker-id"], config["mic-id"]))

async def sound_driver(room_id, ip_address, speaker_id, mic_id):
    import logging
    logger = logging.getLogger('websockets')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())

    # "MAGIC" PARAMETER NUMBERS
    QUIET_CHUNKS_CUTOFF_WINDOW = 5
    VOICE_SENSITIVITY = 3 # VAD (Voice Activity Detection) sensitivity level (1 to 3, higher is more sensitive)
    QUIET_TIME_BEFORE_VOICE_MAX = 1200 #ms
    MAX_SEND_LEN = 5 #sec

    audio = PyAudio()
    default_speakers, default_mic = get_default_speaker_and_mic(audio, speaker_id, mic_id)
    vad = Vad(VOICE_SENSITIVITY)
    
    # AUDIO PARAMETERS
    FORMAT = paInt16
    SAMPLE_SIZE = audio.get_sample_size(FORMAT)
    SAMPLE_RATE = 16000
    MAX_SEND_SIZE = MAX_SEND_LEN * SAMPLE_RATE
    NUMBER_CHANNELS = 1
    SPEAKER_RATIO = default_speakers["defaultSampleRate"] / SAMPLE_RATE
    MIC_RATIO = default_mic["defaultSampleRate"] / SAMPLE_RATE
    CHUNK_DURATION = 30 # ms
    SPEAKER_CHUNK = int(CHUNK_DURATION * SAMPLE_RATE * SPEAKER_RATIO / 1000) * 2 # I do not know why * 2 is needed but it does not work without ¯\_(ツ)_/¯
    MIC_CHUNK = int(CHUNK_DURATION * SAMPLE_RATE * MIC_RATIO / 1000) * 2
    
    # print(f"SAMPLE_RATE: {SAMPLE_RATE}, NUMBER_CHANNELS: {NUMBER_CHANNELS}, SPEAKER_RATIO: {SPEAKER_RATIO}, MIC_RATIO: {MIC_RATIO}, CHUNK_DURATION: {CHUCK_DURATION}, SPEAKER_CHUNK: {SPEAKER_CHUNK}, MIC_CHUNK: {MIC_CHUNK}")

    record_file_name = datetime.now().strftime("%d_%m_%Y_%H_%M_%S_inspelning.wav")
    # record_file = wave.open(record_file_name, 'wb') # TODO uncomment when done
    record_file = wave.open("all_test.wav", 'wb') # remove when done
    record_file.setnchannels(NUMBER_CHANNELS)
    record_file.setsampwidth(SAMPLE_SIZE)
    record_file.setframerate(SAMPLE_RATE)   

    # Test file for debug
    send_file = wave.open("send_test.wav", 'wb')
    send_file.setnchannels(NUMBER_CHANNELS)
    send_file.setsampwidth(SAMPLE_SIZE)
    send_file.setframerate(SAMPLE_RATE)   

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

    websocket_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(websocket_loop)

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
    try:
        while True:
            # Nice recording printout
            i = i + 1 if i < 49 else 0
            j = (i // 10) + 1
            print("Recording", j * ".", (5 - j) * " ", sep="", end="\r")

            # Read data from speaker and mic
            speaker_data = speaker_stream.read(SPEAKER_CHUNK)
            mic_data = mic_stream.read(MIC_CHUNK, exception_on_overflow=False)
            # print(speaker_data)

            speaker_data = np.frombuffer(speaker_data, dtype=np.int16).astype(np.float32)
            mic_data = np.frombuffer(mic_data, dtype=np.int16).astype(np.float32)
            # print("Original speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Original mic stats:    ", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))

            speaker_data = np.reshape(speaker_data, (default_speakers["maxInputChannels"], SPEAKER_CHUNK))
            mic_data = np.reshape(mic_data, (default_mic["maxInputChannels"], MIC_CHUNK))
            # print("Reshaped speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Reshaped mic stats:    ", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))

            speaker_data = resample(speaker_data, orig_sr=default_speakers["defaultSampleRate"], target_sr=SAMPLE_RATE)
            mic_data = resample(mic_data, orig_sr=default_mic["defaultSampleRate"], target_sr=SAMPLE_RATE)
            # print("Resample speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Resample mic stats:    ", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))

            # To mono
            speaker_data = np.mean(speaker_data.reshape(-1, default_speakers["maxInputChannels"]), axis=1).astype(np.int16)
            mic_data = np.mean(mic_data.reshape(-1, default_mic["maxInputChannels"]), axis=1).astype(np.int16)
            # print("Mono     speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Mono     mic stats:    ", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))

            # Fallback to ensusre to pad the arrays to the same size
            max_length = max(speaker_data.size, mic_data.size)
            speaker_data = np.pad(speaker_data, (0, max_length - speaker_data.size), mode='constant').astype(np.int16)
            mic_data = np.pad(mic_data, (0, max_length - mic_data.size), mode='constant').astype(np.int16)
            # print("Pad      speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Pad      mic stats:    ", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))

            combined_data = speaker_data + mic_data
            # print("Combined stats:", combined_data.shape, np.min(combined_data), np.max(combined_data), np.mean(combined_data))

            record_file.writeframes(combined_data) # write to file for debug

            send_data = np.append(send_data, combined_data).astype(np.int16)
            if vad.is_speech(combined_data, SAMPLE_RATE) and not send_data.size > MAX_SEND_SIZE:
                # print("!", end="")
                quite_chunk_count = 0
                started_talking  = True
                continue

            if not started_talking:
                # Save the last quiet chunks before someone talked to improve the start of segments
                if send_data.size >= combined_data.size*QUIET_TIME_BEFORE_VOICE_MAX/CHUNK_DURATION:
                    send_data = send_data[combined_data.size:]

            quite_chunk_count+= 1
            if (quite_chunk_count >= QUIET_CHUNKS_CUTOFF_WINDOW and started_talking) or send_data.size > MAX_SEND_SIZE:
                send_file.writeframes(send_data) # write to debug file 

                # asyncio.create_task(ws.send_audio(audio=send_data.tobytes()))
                await ws.send_audio(audio=send_data.tobytes())
                # print("send audio", send_data.size)

                # Reset state after sending
                send_data = np.empty(0, dtype=np.int16)
                started_talking = False
                quite_chunk_count = 0
                # await asyncio.sleep(0.001) # Needed for reasons

            # if started_talking:
            #     print(".", end="") 
            # else: 
            #     print(",", end="")

    except KeyboardInterrupt:
        # Graceful exit on keyboard interrupt
        print("\nKeyboard interupt recieved.\nRecoding done!")
        pass
    except Exception as e:
        print(f"\nUnkown exception: {e}.\nRecoding interupted!")
        pass
    finally:
        # Stop and close
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

    # print("default_speakers:", default_speakers)
    # print("default_mic:", default_mic)

    # Try to find loopback device with same name(and [Loopback suffix]).
    if not default_speakers["isLoopbackDevice"]:
        found = False
        for loopback in audio.get_loopback_device_info_generator():
            # print("loopback:   ", loopback)
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

    # print("default_speakers:", default_speakers)
    # print("default_mic:", default_mic)
    return default_speakers, default_mic


if __name__ == "__main__":
    main()