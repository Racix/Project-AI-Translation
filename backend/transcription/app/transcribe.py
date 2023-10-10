from faster_whisper import WhisperModel
import time

model_size = "tiny"
model = WhisperModel(model_size, compute_type="int8")

def transcribe(file_path: str) -> dict:
    start_time = time.time() # TODO only for time print, remove later
    segments, info = model.transcribe(file_path, beam_size=5)
    transcription_segments = []
    for segment in segments:
        transcription_segments.append({
            "text": segment.text,
            "start": segment.start,
            "duration": segment.end - segment.start
        })
    result_dict = {
        "Detected language": info.language,
        "Language probability": info.language_probability * 100,
        "segments": transcription_segments
    }
    # TODO only for time print, remove later
    end_time = time.time() 
    total_time = end_time - start_time
    print("Transcribe time: " + str(total_time) + " seconds")

    return result_dict