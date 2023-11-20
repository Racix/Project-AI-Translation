from transformers import pipeline
from langdetect import detect
import time 
import traceback
import os

MODEL_NAME = "openai/whisper-small"
model_size = "tiny"


def transcribe(file_path: str) -> dict:
    try:        
        whisper_pipeline = pipeline(
            "automatic-speech-recognition",
            model=MODEL_NAME,
            chunk_length_s=30,
            device="cpu",
        )
        #Used to detect the original language of the file
        transcription_result = whisper_pipeline(file_path, return_timestamps=True, chunk_length_s=30, batch_size=32, generate_kwargs={"task": "transcribe"})
        transcribed_text = ' '.join([chunk['text'] for chunk in transcription_result['chunks']])
        detected_language = detect(transcribed_text)
                
        #Transcribe to english
        transcription = whisper_pipeline(file_path, return_timestamps=True, chunk_length_s=30, batch_size=32, generate_kwargs={ "language": "en", "task": "transcribe"})        
        chunks = transcription['chunks']
        transcription_data = []        
        transcribed_text = ' '.join([chunk['text'] for chunk in chunks])
    
        for chunk in chunks:
            start_timestamp, end_timestamp = chunk['timestamp']
            text = chunk['text']
            duration = end_timestamp - start_timestamp

            sentence = {
                'text': text,
                'start': start_timestamp,
                'duration': duration,
                'Speaker': "Speaker0"
            }
            transcription_data.append(sentence)      
        result_dict = {
            "segments": transcription_data,
            "detected_language": detected_language,
        }
        return result_dict
    except Exception as e:
        print(traceback.format_exc())