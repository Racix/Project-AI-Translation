from faster_whisper import WhisperModel
import time

model_size = "base"
model = WhisperModel(model_size, compute_type="float32")

def transcribe(file_path: str) -> dict:
    print(f"Transcription of {file_path} started...")
    start_time = time.time()
    segments, info = model.transcribe(file_path, beam_size=5)
    transcription_segments = []
    for segment in segments:
        transcription_segments.append({
            "text": segment.text,
            "start": segment.start,
            "duration": segment.end - segment.start
        })
    result_dict = {
        "detected_language": info.language,
        "Language probability": info.language_probability * 100,
        "segments": transcription_segments
    }
    print(f"Transcription of {file_path} finished. Total time: {str(time.time() - start_time)}")
    return result_dict