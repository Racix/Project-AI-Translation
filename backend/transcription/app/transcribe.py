from langdetect import detect
import time 
import traceback
from loadModel import whisper_pipeline


def transcribe(file_path: str) -> dict:
    try:         
        print(f"Transcription of {file_path} started...")               
        start_time = time.time()
        # Transcribe the video to the original language
        transcription = whisper_pipeline(file_path, return_timestamps=True, chunk_length_s=30, batch_size=32, generate_kwargs={"task": "transcribe"})        
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
                }
                transcription_data.append(sentence)      
            
        result_dict = {
            "detected_language": detected_language,
            "segments": transcription_data,            
        }
        print(f"Transcription of {file_path} finished. Total time: {str(time.time() - start_time)}")
        return result_dict
    except Exception as e:
        print(traceback.format_exc())