from faster_whisper import WhisperModel
import time

model_size = "large-v2"
model = WhisperModel(model_size, compute_type="int8")

def transcribe(input_file, speaker_name="Speaker0"):
    start_time = time.time() # TODO only for time print, remove later
    segments, info = model.transcribe(input_file, beam_size=5)
    transcription_data = []
    for segment in segments:
        transcription_data.append({
            "text": segment.text,
            "start": segment.start,
            "duration": segment.end - segment.start,
            "Speaker": speaker_name
        })
    result_dict = {
        "Detected language": info.language,
        "Language probability": info.language_probability * 100,
        "segments": transcription_data
    }
    # TODO only for time print, remove later
    end_time = time.time() 
    total_time = end_time - start_time
    print("Transcribe time: " + str(total_time) + " seconds")

    return result_dict