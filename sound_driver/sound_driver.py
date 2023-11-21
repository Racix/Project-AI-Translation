import pyaudiowpatch as pyaudio
import librosa
import time
import wave
import numpy as np
# from scipy.signal import resample
from vocie_activity import voice_activity, is_talking
import asyncio
from send_audio import WebSocket
import io

# https://github.com/s0d3s/PyAudioWPatch/blob/master/examples/pawp_record_wasapi_loopback.py
async def sound_driver():
    audio = pyaudio.PyAudio()

    wasapi_info = audio.get_host_api_info_by_type(pyaudio.paWASAPI)
    print(wasapi_info)

    default_speakers = audio.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
    # default_speakers = audio.get_device_info_by_index(22)
    default_mic = audio.get_device_info_by_index(wasapi_info["defaultInputDevice"])
    print("default_speakers:", default_speakers["name"])
    print("default_mic:", default_mic["name"])

    if not default_speakers["isLoopbackDevice"]:
        for loopback in audio.get_loopback_device_info_generator():
            """
            Try to find loopback device with same name(and [Loopback suffix]).
            Unfortunately, this is the most adequate way at the moment.
            """
            if default_speakers["name"] in loopback["name"]:
                default_speakers = loopback
                break
            else:
                print("Default loopback output device not found.\n\nRun `python -m pyaudiowpatch` to check available devices.\nExiting...\n")
                exit()

    print(default_speakers["maxInputChannels"], default_speakers["defaultSampleRate"])
    print(default_mic["maxInputChannels"], default_mic["defaultSampleRate"])

    # number of channels to be higher or equalt to the max amount of channels or else weird stuff happend to the audio quality
    # sample_rate = default_speakers["defaultSampleRate"] if default_speakers["defaultSampleRate"] >= default_mic["defaultSampleRate"] else default_mic["defaultSampleRate"]
    sample_rate = int(min(default_speakers["defaultSampleRate"], default_mic["defaultSampleRate"]))
    n_channels = default_speakers["maxInputChannels"] if default_speakers["maxInputChannels"] >= default_mic["maxInputChannels"] else default_mic["maxInputChannels"]
    # print("samle_rate", SAMPLE_RATE, "n_channels", n_channels)
    
    # Set the audio parameters
    FORMAT = pyaudio.paInt16
    SAMPLE_SIZE = audio.get_sample_size(FORMAT)
    SAMPLE_RATE = 16000
    NUMBER_CHANNELS = 1
    SPEAKER_RATIO = default_speakers["defaultSampleRate"] / SAMPLE_RATE
    MIC_RATIO = default_mic["defaultSampleRate"] / SAMPLE_RATE
    CHUCK_DURATION = 30 # ms
    SPEAKER_CHUNK = int(CHUCK_DURATION * SAMPLE_RATE * SPEAKER_RATIO / 1000) * default_speakers["maxInputChannels"]
    MIC_CHUNK = int(CHUCK_DURATION * SAMPLE_RATE * MIC_RATIO / 1000) * default_mic["maxInputChannels"]
    
    print(f"SAMPLE_RATE: {SAMPLE_RATE}, NUMBER_CHANNELS: {NUMBER_CHANNELS}, SPEAKER_RATIO: {SPEAKER_RATIO}, MIC_RATIO: {MIC_RATIO}, CHUNK_DURATION: {CHUCK_DURATION}, SPEAKER_CHUNK: {SPEAKER_CHUNK}, MIC_CHUNK: {MIC_CHUNK}")

    # Test file for debug
    all_file = wave.open("all_test.wav", 'wb')
    all_file.setnchannels(NUMBER_CHANNELS)
    all_file.setsampwidth(SAMPLE_SIZE)
    all_file.setframerate(SAMPLE_RATE)   

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

    ws = WebSocket()
    await ws.connect()

    voice_activity_last_loop = False
    send_data = np.empty(0, dtype=np.int16)
    loop_num = 0
    test_file_counter = 0
    last_quiet_chunk = []

    started_talking = False
    try:
        print("Recording...")
        while 1== 1:
            # Read data from speaker and mic
            speaker_data = speaker_stream.read(SPEAKER_CHUNK)
            mic_data = mic_stream.read(MIC_CHUNK, exception_on_overflow=False)
            # print(speaker_data)

            speaker_data = np.fromstring(speaker_data, dtype=np.int16).astype(np.float32)
            mic_data = np.fromstring(mic_data, dtype=np.int16).astype(np.float32)
            # print("Original speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Original mic stats:", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))


            speaker_data = np.reshape(speaker_data, (default_speakers["maxInputChannels"], SPEAKER_CHUNK))
            mic_data = np.reshape(mic_data, (default_mic["maxInputChannels"], MIC_CHUNK))
            # print("Reshaped speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Reshaped mic stats:", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))


            speaker_data = librosa.resample(speaker_data, orig_sr=default_speakers["defaultSampleRate"], target_sr=SAMPLE_RATE)
            mic_data = librosa.resample(mic_data, orig_sr=default_mic["defaultSampleRate"], target_sr=SAMPLE_RATE)
            # print("Resample speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Resample mic stats:", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))

            speaker_data = np.mean(speaker_data.reshape(-1, default_speakers["maxInputChannels"]), axis=1).astype(np.int16)
            mic_data = np.mean(mic_data.reshape(-1, default_mic["maxInputChannels"]), axis=1).astype(np.int16)
            # print("Mono speaker stats:", speaker_data.shape, np.min(speaker_data), np.max(speaker_data), np.mean(speaker_data))
            # print("Mono mic stats:", mic_data.shape, np.min(mic_data), np.max(mic_data), np.mean(mic_data))

            # await asyncio.sleep(10)

            max_length = max(len(speaker_data), len(mic_data))

            # Pad the arrays to the same size
            speaker_data = np.pad(speaker_data, (0, max_length - len(speaker_data)), mode='constant').astype(np.int16)
            mic_data = np.pad(mic_data, (0, max_length - len(mic_data)), mode='constant').astype(np.int16)

            combined_data = speaker_data + mic_data
            # print("Combined stats:", combined_data.shape, np.min(combined_data), np.max(combined_data), np.mean(combined_data))

            all_file.writeframes(combined_data)

            if is_talking(combined_data, SAMPLE_RATE):
                
                print("!", end="")
                # voice_activity_last_loop = True
                # print("Audio!")
                loop_num = 0
                send_data = np.append(send_data, combined_data)
                started_talking  = True
                continue

            
            if started_talking:
                # the small silence between talking
                send_data = np.append(send_data, combined_data).astype(np.int16)
            else:
                last_quiet_chunk = combined_data

            # if voice_activity_last_loop:
            loop_num+= 1
            if loop_num >= 10 and started_talking:
                # send_data = np.insert(send_data, 0, int(SAMPLE_RATE/100)).astype(np.int16)
                # send_data = np.insert(send_data, 0, NUMBER_CHANNELS).astype(np.int16)
                # np.savetxt(f"test/test_{test_file_counter}.txt", send_data)

                # write each sent audio
                test_file = wave.open(f"test/test_{test_file_counter}.wav", 'wb')
                test_file.setnchannels(NUMBER_CHANNELS)
                test_file.setsampwidth(SAMPLE_SIZE)
                test_file.setframerate(SAMPLE_RATE)
                test_file.writeframes(send_data)
                test_file.close()
                test_file_counter += 1 

                send_file.writeframes(send_data)
                            
                # print(last_quiet_chunk)
                send_data = np.insert(send_data, 0, last_quiet_chunk)
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

        all_file.close()
        send_file.close()
        await ws.close()
        print("Done!")






