import app.diarize as di
import app.combine as co
import app.util as ut
import json
import os
from fastapi import FastAPI, HTTPException, status, UploadFile, Form

app = FastAPI()

@app.post("/diarize", status_code=status.HTTP_201_CREATED)
async def diarize_media_file(json_data: str = Form(...), file: UploadFile = Form(...)):
    transcription = json.loads(json_data)["transcription"]
    if transcription is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transcription data not in request body") # TODO should this be a error?

    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Media file must be of type .wav")
    
    # Initiate temporary dictionaries for Nemo output
    ut.initialize_dirs()
    file_path = os.path.join(ut.TMP_DIR, file.filename)

    # Temporary save the uploaded media locally
    with open(file_path, "wb") as media_file:
        media_file.write(file.file.read())

    try:
        di.create_diarization(file_path, None, 1) # TODO fix later
        diarization_segments = co.parse_rttm_from_file(file_path)
        transcription['segments'] = co.align_segments_with_overlap_info(transcription['segments'], diarization_segments)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Diarization error.")
    finally:
        ut.delete_dirs()

    return {"diarization": transcription}
    