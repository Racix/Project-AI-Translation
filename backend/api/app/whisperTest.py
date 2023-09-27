import json
from faster_whisper import WhisperModel

import time
import logging
logging.basicConfig()
logging.getLogger("faster_whisper").setLevel(logging.DEBUG)
model_size = "large-v2"


def main(input_file): 
    start_time = time.time()
    if input_file.lower().endswith(".mp3"):
        audio_output_file = input_file.replace(".mp3", "_output.json")
        res = transcribe_and_save(input_file, audio_output_file, speaker_name="Speaker0")
        print(f"Audio transcription saved to {audio_output_file}")
    elif input_file.lower().endswith(".mp4"):
        video_output_file = input_file.replace(".mp4", "_output.json")
        res = transcribe_and_save(input_file, video_output_file, speaker_name="Speaker0") 
        print(f"Video transcription saved to {video_output_file}")
    else:
        print("Wrong file format")
        return None
    end_time = time.time()
    total_time = end_time - start_time
    print("Det tog: " + str(total_time) + " sekunder")
    return res


def transcribe_and_save(input_file, output_file, speaker_name="Speaker0"):
    import_time = time.time()
    model = WhisperModel(model_size, device="cpu", compute_type="int8")
    import2_time = time.time()
    how_long = import2_time - import_time
    print("Import model tog" + str(how_long) + "sekunder")
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

    return result_dict
    # with open(output_file, "w", encoding="utf-8") as json_file:
    #     json.dump(result_dict, json_file, indent=4)


main("testfil3.mp4")