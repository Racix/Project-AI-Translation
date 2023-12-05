import webrtcvad

# Initialize the VAD (Voice Activity Detection) with the desired sensitivity level (1 to 3 and higher is more sensitive).
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
    return vad.is_speech(audio_data, sample_rate)
        