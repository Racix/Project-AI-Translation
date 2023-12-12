import app.util as ut
from nemo.collections.asr.models.msdd_models import NeuralDiarizer
from omegaconf import OmegaConf
import json
import wget
import os
import torch

def configurations(wav_path: str, domain: str, rttm: str | None, speakers: int = None) -> OmegaConf:
    # Configuration yaml file
    DOMAIN_TYPE = domain # Can be meeting or telephonic based on domain type of the audio file, meeting 3-6 ppl, telephonic better suited for 1 on 1 conversation.
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
        'rttm_filepath': rttm,
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
    config.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    config.batch_size = 16
    config.diarizer.out_dir = ut.OUTPUT_DIR # Directory to store intermediate files and prediction outputs
    config.diarizer.speaker_embeddings.model_path = pretrained_speaker_model
    config.diarizer.msdd_model.model_path = pretrained_msdd  
    config.diarizer.msdd_model.parameters.sigmoid_threshold = [0.7,1] 
    config.diarizer.msdd_model.parameters.diar_window = 50
    config.diarizer.oracle_vad = False # ----> ORACLE VAD Sätt till false om vi inte vill ha RTTM!!!
    config.diarizer.vad.model_path = pretrained_vad
    config.diarizer.clustering.parameters.oracle_num_speakers = False if speakers is None else True #False if speakers is nonec
    config.diarizer.clustering.parameters.embeddings_per_chunk: 150000 # Number of embeddings in each chunk for long-form audio clustering. Adjust based on GPU memory capacity. (default: 10000, approximately 40 mins of audio)
    return config


def msdd_diarization(config: OmegaConf):
    #Multi-scale model
    oracle_vad_msdd_model = NeuralDiarizer(cfg=config).to(config.device)
    oracle_vad_msdd_model.diarize()


# def cluster_diarization(config: OmegaConf):
#     #Clustering model
#     oracle_vad_clusdiar_model = ClusteringDiarizer(cfg=config)
#     oracle_vad_clusdiar_model.diarize()


def create_diarization(file_path: str, rttm: str | None, speakers: int = None):
    domain = ""
    if speakers is not None:
        if speakers > 2:
            domain = "meeting"
        else:
            domain = "telephonic"
    else:
        domain = "telephonic"

    config = configurations(file_path, domain, rttm, speakers)
    #cluster_diarization(config)
    msdd_diarization(config)