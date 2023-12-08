import app.diarize as di
import app.combine as co
import app.util as ut
import json
import os
from fastapi import FastAPI, HTTPException, status, UploadFile, Form
import torch
import gc

app = FastAPI()

@app.post("/diarize", status_code=status.HTTP_201_CREATED)
async def diarize_media_file(json_data: str = Form(...), file: UploadFile = Form(...), speakers: str = Form(...)):
    transcription = json.loads(json_data)["transcription"]
    if transcription is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transcription data not in request body") # TODO should this be a error?

    if not file.filename.lower().endswith(".wav"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Media file must be of type .wav")
    
    if speakers[0].isdigit():
        sp = int(speakers)
    else:
        sp = None

    # Initiate temporary dictionaries for Nemo output
    timestamp = ut.initialize_dirs()
    file_path = os.path.join(ut.TMP_DIR, file.filename)

    # Temporary save the uploaded media locally
    with open(file_path, "wb") as media_file:
        media_file.write(file.file.read())

    try:
        #
        di.create_diarization(file_path, None, sp) # TODO fix later
        diarization_segments = co.parse_rttm_from_file(file_path)
        transcription['segments'] = co.align_segments_with_overlap_info(transcription['segments'], diarization_segments)
    except MemoryError as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Memory error.")
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Diarization error.")
    finally:
        os.remove(file_path)
        ut.delete_dirs(timestamp)
        # Clear cache
        torch.cuda.empty_cache()
        gc.collect()

    return {"diarization": transcription}
    