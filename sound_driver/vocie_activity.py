import pyaudiowpatch as pyaudio
import numpy as np

energy_treshold = 1

def voice_activity(sound):
    energy = np.sum(sound ** 2) / len(sound)
    if (energy > energy_treshold): 
        print("Voce")
        return True
    else:
        print(".")
        return False
        