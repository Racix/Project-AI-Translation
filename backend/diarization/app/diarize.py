from nemo.collections.asr.parts.utils.speaker_utils import rttm_to_labels, labels_to_pyannote_object
from nemo.collections.asr.models.msdd_models import NeuralDiarizer
from nemo.collections.asr.models import ClusteringDiarizer
from omegaconf import OmegaConf
from pydub import AudioSegment 
import matplotlib.pyplot as plt
import soundfile as sf
import numpy as np
import subprocess
import librosa
import IPython
import shutil
# import torch
import json
import wget
import sys
import os

CONFIG_DIR = "/diarization/config"
TMP_DIR = "/diarization/tmp"

os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(TMP_DIR, exist_ok=True)

input_manifest_path = CONFIG_DIR + "/input_manifest.json"

def convert_to_wav(file_path, name):
    #Convert audio file to .wav format.
    output_path = os.path.join(TMP_DIR, name) +'.wav'
    subprocess.call(['ffmpeg', '-i', file_path, output_path])
    return output_path
    # print(file_path)
    # wav = AudioSegment.from_mp3(file_path) 
    # print(wav)
    # return wav 

def to_mono(file_path):
    #Convert audio file to mono and 16000hz subsample
    y, sr = librosa.load(file_path, sr=16000, mono=True)
    sf.write(file_path, y, sr)


def preprocess(file_path):
    name = file_path.split("/")[-1].split(".")[0]
    if file_path.lower().endswith((".mp3", ".mp4")):
        wav_path = convert_to_wav(file_path, name)
        to_mono(wav_path)
        return wav_path
    elif file_path.lower().endswith(".wav"):
        to_mono(file_path)
        return file_path
    print("wrong file format")
    return None
    # audio_path = data_dir + name + '.wav'
    # return audio_path

def configurations(wav_path, domain, rttm, speakers):
    # Configuration yaml file
    DOMAIN_TYPE = domain # Can be meeting or telephonic based on domain type of the audio file
    CONFIG_FILE_NAME = f"diar_infer_{DOMAIN_TYPE}.yaml"
    CONFIG_URL = f"https://raw.githubusercontent.com/NVIDIA/NeMo/main/examples/speaker_tasks/diarization/conf/inference/{CONFIG_FILE_NAME}"
    if not os.path.exists(os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)):
        CONFIG = wget.download(CONFIG_URL, CONFIG_DIR)
    else:
        CONFIG = os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)
    config = OmegaConf.load(CONFIG)
    
    meta = {
        'audio_filepath': wav_path,
        'offset': 0,
        'duration': None,
        'label': 'infer',
        'text': '-',  
        'num_speakers': speakers,
        'rttm_filepath': None, # Sätt till None om vi inte vill ha RTTM!!!!
        'uem_filepath': None
    }

    with open(input_manifest_path,'w') as fp:
        json.dump(meta, fp)
        fp.write('\n')
    output_dir = os.path.join(CONFIG_DIR, 'oracle_vad')
    os.makedirs(output_dir, exist_ok=True)

    #Configure yaml file
    pretrained_speaker_model = "models/titanet-l.nemo"
    pretrained_vad = "models/vad_multilingual_marblenet.nemo"
    pretrained_msdd = "models/diar_msdd_telephonic.nemo"
    config.diarizer.manifest_filepath = input_manifest_path
    # config.device = device
    config.device = "default"
    config.batch_size = 1
    config.diarizer.out_dir = output_dir # Directory to store intermediate files and prediction outputs
    config.diarizer.speaker_embeddings.model_path = pretrained_speaker_model
    config.diarizer.msdd_model.model_path = pretrained_msdd  
    config.diarizer.msdd_model.parameters.sigmoid_threshold = [0.7,1] 
    config.diarizer.msdd_model.parameters.diar_window = 50
    config.diarizer.speaker_embeddings.parameters.window_length_in_sec = [1.5,1.25,1.0,0.75,0.5]
    config.diarizer.speaker_embeddings.parameters.shift_length_in_sec = [0.75,0.625,0.5,0.375,0.1]
    config.diarizer.speaker_embeddings.parameters.multiscale_weights= [1,1,1,1,1]
    config.diarizer.oracle_vad = False # ----> ORACLE VAD Sätt till false om vi inte vill ha RTTM!!!
    config.diarizer.vad.model_path = pretrained_vad
    config.diarizer.clustering.parameters.oracle_num_speakers = False
    return config

def msdd_diarization(config):
    #Multi-scale model
    oracle_vad_msdd_model = NeuralDiarizer(cfg=config)
    oracle_vad_msdd_model.diarize()
    
def cluster_diarization(config):
    #Clustering model
    oracle_vad_clusdiar_model = ClusteringDiarizer(cfg=config)
    oracle_vad_clusdiar_model.diarize()

def create_diarization(file_path, rttm, speakers):
    wav_path = preprocess(file_path)
    config = configurations(wav_path, "telephonic", rttm, speakers)
    #cluster_diarization(config)
    msdd_diarization(config)