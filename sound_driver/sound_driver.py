import pyaudiowpatch as pyaudio
import time
import wave
import numpy as np
from scipy.signal import resample
from vocie_activity import voice_activity
import asyncio
from send_audio import send_audio

# https://github.com/s0d3s/PyAudioWPatch/blob/master/examples/pawp_record_wasapi_loopback.py
def combineStreamData(data1, data2):
    return np.frombuffer(data1, dtype=FORMAT) + np.frombuffer(data2, dtype=FORMAT)
# Set the audio parameters
FORMAT = pyaudio.paInt16
CHANNELS = 1
SPEAKER_RATE = 48000
CHUNK = 512
RECORD_SECONDS = 5  # You can adjust the recording duration as needed
OUTPUT_FILENAME = "test.wav"

audio = pyaudio.PyAudio()

SAMPLE_SIZE = audio.get_sample_size(FORMAT)

wasapi_info = audio.get_host_api_info_by_type(pyaudio.paWASAPI)
print(wasapi_info)
default_speakers = audio.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
default_mic = audio.get_device_info_by_index(wasapi_info["defaultInputDevice"])
# print(default_speakers, default_mic)

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

speaker_file = wave.open(OUTPUT_FILENAME, 'wb')
speaker_file.setnchannels(default_speakers["maxInputChannels"])
speaker_file.setsampwidth(SAMPLE_SIZE)
speaker_file.setframerate(int(default_speakers["defaultSampleRate"]))   
            
print("Recording...")

speaker_stream = audio.open(format=FORMAT,
    channels=default_speakers["maxInputChannels"],
    rate=int(default_speakers["defaultSampleRate"]),
    frames_per_buffer=CHUNK,
    input=True,
    input_device_index=default_speakers["index"],
 )

# mic_stream = audio.open(format=FORMAT, channels=CHANNELS,
#                        rate=SPEAKER_RATE, input=True,
#                        frames_per_buffer=CHUNK)


for i in range(0, int(SPEAKER_RATE / CHUNK * RECORD_SECONDS)):
    """Record audio step-by-step"""
    speaker_data = speaker_stream.read(CHUNK)
    # mic_data = mic_stream.read(CHUNK)

    speaker_data = np.frombuffer(speaker_data, dtype=np.int16)
    # mic_data = np.frombuffer(mic_data, dtype=np.int16)
    if voice_activity(speaker_data):
        speaker_file.writeframes(speaker_data)

    # if len(speaker_data) != len(mic_data):
    #     max_len = max(len(speaker_data), len(mic_data))
    #     speaker_data = np.pad(speaker_data, (0, max_len - len(speaker_data)))
    #     mic_data = np.pad(mic_data, (0, max_len - len(mic_data)))

    # mic_data = resample(mic_data, len(speaker_data))

    # combined_data = speaker_data + mic_data
    # speaker_file.writeframes(combined_data.tobytes())
    
# asyncio.get_event_loop().run_until_complete(send_audio())


speaker_file.close()
print("Done!")





