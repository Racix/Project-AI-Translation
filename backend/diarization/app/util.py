import os
import time
import shutil

MAIN_DIR = os.path.join('diarization') 
TMP_DIR = os.path.join(MAIN_DIR, 'tmp')

timestamp = None

CONFIG_DIR = None
DIARIZE_TMP_DIR = None
OUTPUT_DIR = None

def initialize_dirs():
    """
    initialize all directories 
    """ 
    global timestamp, CONFIG_DIR, DIARIZE_TMP_DIR, OUTPUT_DIR

    if timestamp is not None:
        raise Exception("already initialized")
    timestamp = time.time_ns()
    CONFIG_DIR = os.path.join(MAIN_DIR, str(timestamp), 'config')
    DIARIZE_TMP_DIR = os.path.join(MAIN_DIR, str(timestamp), 'tmp')
    OUTPUT_DIR = os.path.join(CONFIG_DIR, 'oracle_vad')

    os.makedirs(TMP_DIR, exist_ok=True)
    os.makedirs(CONFIG_DIR, exist_ok=True)
    os.makedirs(DIARIZE_TMP_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

def delete_dirs():
    """
    this will delete ALL folders created in the MAIN_DIR and all of its content.
    """ 
    global timestamp, CONFIG_DIR, DIARIZE_TMP_DIR, OUTPUT_DIR
    if timestamp is None:
        raise Exception("nothing is initialized")
    timestamp = None
    shutil.rmtree(MAIN_DIR)

def get_file_name(file_path):
    file_name, _ = os.path.splitext(os.path.basename(file_path))
    return file_name

def get_rttm_path(file_name):
    return os.path.join(CONFIG_DIR, 'oracle_vad', 'pred_rttms', f"{file_name}.rttm")

def get_wav_path(file_name):
    return os.path.join(DIARIZE_TMP_DIR, f"{file_name}.wav")