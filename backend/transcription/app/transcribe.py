from transformers import pipeline
from langdetect import detect
import time 
import traceback



def transcribe(file_path: str) -> dict:
    try:         
        MODEL_NAME = "openai/whisper-large-v2"
        #device = "cuda" if torch.cuda.is_available() else "cpu"
        whisper_pipeline = pipeline(
        "automatic-speech-recognition",
        model=MODEL_NAME,
        chunk_length_s=30,
        device= 'cuda',        
        )
        print(f"Transcription of {file_path} started...")               
        # Transcribe the video to the original language
        transcription = whisper_pipeline(file_path, return_timestamps=True, batch_size = 4, chunk_length_s=30, generate_kwargs={"task": "transcribe"})        
        chunks = transcription['chunks']
        transcription_data = []        
        transcribed_text = ' '.join([chunk['text'] for chunk in chunks])
        detected_language = detect(transcribed_text)
        for chunk in chunks:
            start_timestamp, end_timestamp = chunk['timestamp']
            
            # Check if end_timestamp is None
            if end_timestamp is not None:
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
        return result_dict
    except Exception as e:
        print(traceback.format_exc())
    finally:
        del whisper_pipeline
