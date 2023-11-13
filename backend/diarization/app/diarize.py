import app.util as ut
from nemo.collections.asr.parts.utils.speaker_utils import rttm_to_labels, labels_to_pyannote_object
from nemo.collections.asr.models.msdd_models import NeuralDiarizer
from omegaconf import OmegaConf
import json
import wget
import os


def configurations(wav_path: str, domain: str, rttm: str | None, speakers: int) -> OmegaConf:
    # Configuration yaml file
    DOMAIN_TYPE = domain # Can be meeting or telephonic based on domain type of the audio file
    CONFIG_FILE_NAME = f"diar_infer_{DOMAIN_TYPE}.yaml"
    CONFIG_URL = f"https://raw.githubusercontent.com/NVIDIA/NeMo/main/examples/speaker_tasks/diarization/conf/inference/{CONFIG_FILE_NAME}"
    if not os.path.exists(os.path.join(ut.CONFIG_DIR, CONFIG_FILE_NAME)):
        CONFIG = wget.download(CONFIG_URL, ut.CONFIG_DIR)
    else:
        CONFIG = os.path.join(ut.CONFIG_DIR, CONFIG_FILE_NAME)
    config = OmegaConf.load(CONFIG)
    
    meta = {
        'audio_filepath': wav_path,
        'offset': 0,
        'duration': None,
        'label': 'infer',
        'text': '-',  
        'num_speakers': speakers,
        'rttm_filepath': rttm
        'uem_filepath': None
    }

    input_manifest_path = ut.CONFIG_DIR + "/input_manifest.json"
    with open(input_manifest_path,'w') as fp:
        json.dump(meta, fp)
        fp.write('\n')

    #Configure yaml file
    pretrained_speaker_model = "models/titanet-l.nemo"
    pretrained_vad = "models/vad_multilingual_marblenet.nemo"
    pretrained_msdd = "models/diar_msdd_telephonic.nemo"
    config.diarizer.manifest_filepath = input_manifest_path
    # config.device = device
    config.batch_size = 1
    config.diarizer.out_dir = ut.OUTPUT_DIR # Directory to store intermediate files and prediction outputs
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


def msdd_diarization(config: OmegaConf):
    #Multi-scale model
    oracle_vad_msdd_model = NeuralDiarizer(cfg=config)
    oracle_vad_msdd_model.diarize()


# def cluster_diarization(config: OmegaConf):
#     #Clustering model
#     oracle_vad_clusdiar_model = ClusteringDiarizer(cfg=config)
#     oracle_vad_clusdiar_model.diarize()


def create_diarization(file_path: str, rttm: str | None, speakers: int):
    config = configurations(file_path, "telephonic", rttm, speakers)
    #cluster_diarization(config)
    msdd_diarization(config)