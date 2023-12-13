from transformers import pipeline
import torch
import gc   

MODEL_NAME = "openai/whisper-large-v2"
device = "cuda" if torch.cuda.is_available() else "cpu"

whisper_pipeline = pipeline(
    "automatic-speech-recognition",
    model=MODEL_NAME,
    chunk_length_s=30,
    device=device,        
)

del whisper_pipeline
torch.cuda.empty_cache()
gc.collect()