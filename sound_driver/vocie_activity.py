import pyaudiowpatch as pyaudio
import numpy as np

energy_treshold = 1

def voice_activity(sound):
    energy = np.sum(sound ** 2) / len(sound)
    if (energy > energy_treshold): 
        # print("Voce")
        return True
    else:
        # print(".")
        return False
    
import webrtcvad

# Initialize the VAD (Voice Activity Detection) with the desired sensitivity level (1 to 3).
vad = webrtcvad.Vad(3)

def is_talking(audio_data, sample_rate):
    """
    Determine if the user is talking based on audio data.

    Args:
    - audio_data: The audio data as a byte string or bytearray.
    - sample_rate: The sample rate of the audio data.

    Returns:
    - True if talking, False if not talking.
    """
    # Convert the audio data to a format that webrtcvad expects (16-bit PCM).
    # audio_data_int16 = np.frombuffer(audio_data, dtype=np.int16)

    # Check if the VAD detects speech in the audio data.
    is_speech = vad.is_speech(audio_data, sample_rate)

    return is_speech
        