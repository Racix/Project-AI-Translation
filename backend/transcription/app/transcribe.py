from transformers import pipeline
from langdetect import detect
import time 
import traceback

MODEL_NAME3 = "openai/whisper-small"
model_size = "tiny"


def transcribe(file_path: str) -> dict:
    try:

        
        whisper_pipeline = pipeline(
            "automatic-speech-recognition",
            model=MODEL_NAME3,
            chunk_length_s=30,
            device="cpu",
        )
        #Used to detect the original language of the file
        To_detect_language = whisper_pipeline(file_path, return_timestamps=True, chunk_length_s=30, batch_size=32, generate_kwargs={"task": "transcribe"})
        elements = To_detect_language['chunks']
        Text_To_be_detect = ' '.join([chunk['text'] for chunk in elements])
        detected_language = detect(Text_To_be_detect)
        
        #Transcribe to english
        transcription = whisper_pipeline(file_path, return_timestamps=True, chunk_length_s=30, batch_size=32, generate_kwargs={ "language": "en", "task": "transcribe"})        
        chunks = transcription['chunks']
        transcription_data = []
        
        # Extract transcribed text for language detection
        transcribed_text = ' '.join([chunk['text'] for chunk in chunks])
    
        for chunk in chunks:
            start_timestamp, end_timestamp = chunk.get('timestamp', (None, None))
            
            if start_timestamp is not None and end_timestamp is not None:
                duration = end_timestamp - start_timestamp

                sentence = {
                    "text": chunk['text'],
                    "start": start_timestamp,
                    "duration": duration,
                }
                transcription_data.append(sentence)
            
        result_dict = {
            "segments": transcription_data,
            "detected_language": detected_language,
        }
        return result_dict
    except Exception as e:
        print(traceback.format_exc())