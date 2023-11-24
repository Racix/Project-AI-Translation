import asyncio
from pyaudiowpatch import PyAudio, paWASAPI, paInt16
from librosa import resample
import wave # will get removed after we are done debugging
import numpy as np
from vocie_activity import voice_activity, is_talking
# from cli import get_arguments
from send_audio import WebSocket
from yaml import safe_load
from datetime import datetime

def main():
    config = safe_load(open("config.yaml"))
    room_id = input("Choose a room id: ")
    asyncio.run(sound_driver(room_id, config["ip-address"], config["speaker-id"], config["mic-id"]))

async def sound_driver(room_id, ip_address, speaker_id, mic_id):

    audio = PyAudio()

    default_speakers, default_mic = get_default_speaker_and_mic(audio, speaker_id, mic_id)
    
    # print("default_speakers:", default_speakers)
    # print("default_mic:", default_mic)

    # print("default_speakers:", default_speakers["index"], default_speakers["defaultSampleRate"], default_speakers["maxInputChannels"], default_speakers["name"])
    # print("default_mic:     ", default_mic["index"], default_mic["defaultSampleRate"], default_mic["maxInputChannels"], default_mic["name"])

    # number of channels to be higher or equalt to the max amount of channels or else weird stuff happend to the audio quality
    # sample_rate = default_speakers["defaultSampleRate"] if default_speakers["defaultSampleRate"] >= default_mic["defaultSampleRate"] else default_mic["defaultSampleRate"]
    # sample_rate = int(min(default_speakers["defaultSampleRate"], default_mic["defaultSampleRate"]))
    # n_channels = default_speakers["maxInputChannels"] if default_speakers["maxInputChannels"] >= default_mic["maxInputChannels"] else default_mic["maxInputChannels"]
    # print("samle_rate", SAMPLE_RATE, "n_channels", n_channels)
    
    # Set the audio parameters
    FORMAT = paInt16
    SAMPLE_SIZE = audio.get_sample_size(FORMAT)
    SAMPLE_RATE = 16000
    NUMBER_CHANNELS = 1
    SPEAKER_RATIO = default_speakers["defaultSampleRate"] / SAMPLE_RATE
    MIC_RATIO = default_mic["defaultSampleRate"] / SAMPLE_RATE
    CHUCK_DURATION = 30 # ms
    SPEAKER_CHUNK = int(CHUCK_DURATION * SAMPLE_RATE * SPEAKER_RATIO / 1000) * 2 # I do not know why * 2 is needed but it does not work without ¯\_(ツ)_/¯
    MIC_CHUNK = int(CHUCK_DURATION * SAMPLE_RATE * MIC_RATIO / 1000) * 2
    
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

    ws = WebSocket(ip_address, room_id)
    await ws.connect()

    # voice_activity_last_loop = False
    send_data = np.empty(0, dtype=np.int16)
    loop_num = 0
    # test_file_counter = 0
    last_quiet_chunk = []

    started_talking = False
    try:
        print("Recording...")
        while True:
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

            speaker_data = np.mean(speaker_data.reshape(-1, default_speakers["maxInputChannels"]), axis=1).astype(np.int16)
            mic_data = np.mean(mic_data.reshape(-1, default_mic["maxInputChannels"]), axis=1).astype(np.int16)
            # print("Mono     speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Mono     mic stats:    ", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))

            max_length = max(len(speaker_data), len(mic_data))

            # Pad the arrays to the same size
            speaker_data = np.pad(speaker_data, (0, max_length - len(speaker_data)), mode='constant').astype(np.int16)
            mic_data = np.pad(mic_data, (0, max_length - len(mic_data)), mode='constant').astype(np.int16)
            # print("Pad      speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Pad      mic stats:    ", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))

            combined_data = speaker_data + mic_data
            # print("Combined stats:", combined_data.shape, np.min(combined_data), np.max(combined_data), np.mean(combined_data))

            # await asyncio.sleep(10)

            record_file.writeframes(combined_data) # write to file for debug

            if is_talking(combined_data, SAMPLE_RATE):
                print("!", end="")
                loop_num = 0
                send_data = np.append(send_data, combined_data)
                started_talking  = True
                continue
            
            if started_talking:
                # the small silence between talking
                send_data = np.append(send_data, combined_data).astype(np.int16)
            else:
                # Save the last quiet chunk before someone talked to improve the start of segments
                last_quiet_chunk = combined_data

            loop_num+= 1
            if loop_num >= 3 and started_talking:
                send_data = np.insert(send_data, 0, last_quiet_chunk)
                send_file.writeframes(send_data) # write to debug file 

                asyncio.create_task(ws.send_audio(audio=send_data.tobytes()))
                # print("send audio")
                started_talking = False
                send_data = np.empty(0, dtype=np.int16)
                loop_num = 0
                await asyncio.sleep(0.01)

            if started_talking:
                print(".", end="") 
            else: 
                print(",", end="")

    except KeyboardInterrupt:
        # Graceful exit on keyboard interrupt
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
        print("Done!")

def get_default_speaker_and_mic(audio, speaker_id, mic_id):

    wasapi_info = audio.get_host_api_info_by_type(paWASAPI)

    default_speakers = audio.get_device_info_by_index(wasapi_info["defaultOutputDevice"] if speaker_id is None else speaker_id)
    default_mic = audio.get_device_info_by_index(wasapi_info["defaultInputDevice"] if mic_id is None else mic_id)

    print("default_speakers:", default_speakers)
    print("default_mic:", default_mic)

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

    return default_speakers, default_mic


if __name__ == "__main__":
    main()