from transformers import pipeline
import torch

MODEL_NAME = "openai/whisper-tiny"
model_size = "tiny"
device = "cuda" if torch.cuda.is_available() else "cpu"

whisper_pipeline = pipeline(
    "automatic-speech-recognition",
    model=MODEL_NAME,
    chunk_length_s=30,
    device=device,        
)