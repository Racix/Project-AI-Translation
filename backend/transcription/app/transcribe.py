from transformers import pipeline
from langdetect import detect
import time 
import traceback
from loadModel import whisper_pipeline


def transcribe(file_path: str) -> dict:
    try:                        
        #Transcribe the video to the original language
        transcription = whisper_pipeline(file_path, return_timestamps=True, chunk_length_s=30, batch_size=32, generate_kwargs={"task": "transcribe"})        
        chunks = transcription['chunks']
        transcription_data = []        
        transcribed_text = ' '.join([chunk['text'] for chunk in chunks])
        detected_language = detect(transcribed_text)
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
            "detected_language": detected_language,
            "segments": transcription_data,            
        }
        print(result_dict)
        return result_dict
    except Exception as e:
        print(traceback.format_exc())