import pyaudiowpatch as pyaudio
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

    # Set the audio parameters
    FORMAT = pyaudio.paInt16
    CHUNK = 512
    RECORD_SECONDS = 10 # You can adjust the recording duration as needed
    OUTPUT_FILENAME = "test.wav"

    audio = pyaudio.PyAudio()

    SAMPLE_SIZE = audio.get_sample_size(FORMAT)
    print(SAMPLE_SIZE)

    wasapi_info = audio.get_host_api_info_by_type(pyaudio.paWASAPI)
    print(wasapi_info)
    default_speakers = audio.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
    default_speakers = audio.get_device_info_by_index(22)
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
    # sample_rate = 
    n_channels = default_speakers["maxInputChannels"] if default_speakers["maxInputChannels"] >= default_mic["maxInputChannels"] else default_mic["maxInputChannels"]
    print("samle_rate", sample_rate, "n_channels", n_channels)

    speaker_file = wave.open(OUTPUT_FILENAME, 'wb')
    speaker_file.setnchannels(n_channels)
    speaker_file.setsampwidth(SAMPLE_SIZE)
    speaker_file.setframerate(sample_rate)   
    
    CHUNK = int(sample_rate / 100) * 2
    # 48000 / 100 = 480   1s = 480000   0.01s =  480  
    # 44100 / 100 = 441   

    speaker_stream = audio.open(format=FORMAT,
        channels=n_channels,
        rate=sample_rate,
        frames_per_buffer=CHUNK,
        input=True,
        input_device_index=default_speakers["index"],
    )

    mic_stream = audio.open(format=FORMAT, 
        channels=n_channels,
        rate=sample_rate, 
        frames_per_buffer=CHUNK,
        input=True
    )

    print("Recording...")

    websocket_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(websocket_loop)

    ws = WebSocket()
    await ws.connect()

    voice_activity_last_loop = False
    send_data = np.empty(0, dtype=np.int16)
    loop_num = 0
    test_file_counter = 0

    started_talking = False
    while 1== 1:
        # Read data from speaker and mic
        # speaker_data = speaker_stream.read(CHUNK)
        mic_data = mic_stream.read(CHUNK, exception_on_overflow=False)

        # speaker_data = np.frombuffer(speaker_data, dtype=np.int16)
        # print("speaker", speaker_data.size)
        mic_data = np.frombuffer(mic_data, dtype=np.int16)
        # print("mic", mic_data.size)
        # combined_data = speaker_data + mic_data
        combined_data = mic_data

        speaker_file.writeframes(combined_data)

        if not is_talking(combined_data, sample_rate):

            if started_talking:
                send_data = np.append(send_data, combined_data)

            # if voice_activity_last_loop:
            loop_num+= 1
            if loop_num >= 50 and send_data.size >= 50000:
                send_data = np.insert(send_data, 0, int(sample_rate/100))
                send_data = np.insert(send_data, 0, n_channels)

                # write each sent audio
                test_file = wave.open(f"test/test_{test_file_counter}.wav", 'wb')
                test_file.setnchannels(n_channels)
                test_file.setsampwidth(SAMPLE_SIZE)
                test_file.setframerate(sample_rate)  
                test_file.writeframes(send_data[2:])
                test_file.close()
                test_file_counter += 1 
                            
                asyncio.create_task(ws.send_audio(audio=send_data.tobytes()))
                # print("send audio")
                started_talking = False
                send_data = np.empty(0, dtype=np.int16)
                await asyncio.sleep(0.01)

            print(".", end="")
            # voice_activity_last_loop = False

            continue
        
        print("!", end="")
        # voice_activity_last_loop = True
        # print("Audio!")
        loop_num = 0
        send_data = np.append(send_data, combined_data)
        started_talking  = True

    ws.close()
    speaker_file.close()
    print("Done!")





