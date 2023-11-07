import os

CONFIG_DIR = "/diarization/config"
DIARIZE_TMP_DIR = "/diarization/tmp"
OUTPUT_DIR = os.path.join(CONFIG_DIR, 'oracle_vad')

def get_file_name(file_path):
    file_name, _ = os.path.splitext(os.path.basename(file_path))
    return file_name

def get_rttm_path(file_name):
    return f"{CONFIG_DIR}/oracle_vad/pred_rttms/{file_name}.rttm" # TODO make this nicer

def get_wav_path(file_name):
    file = file_name + ".wav"
    return os.path.join(DIARIZE_TMP_DIR, file)