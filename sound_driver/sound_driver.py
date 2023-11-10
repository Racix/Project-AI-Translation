import pyaudiowpatch as pyaudio
import time
import wave
import numpy as np
from scipy.signal import resample
from vocie_activity import voice_activity, is_talking
import asyncio
from send_audio import send_audio
import io

# https://github.com/s0d3s/PyAudioWPatch/blob/master/examples/pawp_record_wasapi_loopback.py

# Set the audio parameters
FORMAT = pyaudio.paInt16
CHUNK = 512
RECORD_SECONDS = 10 # You can adjust the recording duration as needed
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

print(default_speakers["maxInputChannels"], default_speakers["defaultSampleRate"])
print(default_mic["maxInputChannels"], default_mic["defaultSampleRate"])

# number of channels to be higher or equalt to the max amount of channels or else weird stuff happend to the audio quality
n_channels = default_speakers["maxInputChannels"] if default_speakers["maxInputChannels"] >= default_mic["maxInputChannels"] else default_mic["maxInputChannels"]

speaker_file = wave.open(OUTPUT_FILENAME, 'wb')
speaker_file.setnchannels(n_channels)
speaker_file.setsampwidth(SAMPLE_SIZE)
speaker_file.setframerate(int(default_speakers["defaultSampleRate"]))   
   
speaker_stream = audio.open(format=FORMAT,
    channels=n_channels,
    rate=int(default_speakers["defaultSampleRate"]),
    frames_per_buffer=CHUNK,
    input=True,
    input_device_index=default_speakers["index"],
 )

mic_stream = audio.open(format=FORMAT, channels=n_channels,
                       rate=int(default_mic["defaultSampleRate"]), input=True,
                       frames_per_buffer=CHUNK)

print("Recording...")

CHUNK = int(default_speakers["defaultSampleRate"] / 100)
mic_data = None

for i in range(0, int(default_speakers["defaultSampleRate"] / CHUNK * RECORD_SECONDS)):
    """Record audio step-by-step"""
    speaker_data = speaker_stream.read(CHUNK)
    mic_data = mic_stream.read(CHUNK)

    speaker_data = np.frombuffer(speaker_data, dtype=np.int16)
    mic_data = np.frombuffer(mic_data, dtype=np.int16)

    # if not voice_activity(speaker_data) and not voice_activity(mic_data):
    #     print("No audio!")
    #     continue

    combined_data = speaker_data + mic_data
    speaker_file.writeframes(combined_data)
    # if not is_talking(mic_data, int(default_mic["defaultSampleRate"])):
    #     print("No audio!")
    #     continue
    print("Sound!")
    # speaker_file.writeframes(mic_data)


with open(OUTPUT_FILENAME, "rb") as fi:
    data = fi.read()

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(send_audio(audio=data))



speaker_file.close()
print("Done!")





