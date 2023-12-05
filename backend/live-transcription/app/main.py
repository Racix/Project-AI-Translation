import os
import app.transcribe as tr
from fastapi import FastAPI, HTTPException, status, UploadFile
import torch

TMP_DIR = "/tmp"
os.makedirs(TMP_DIR, exist_ok=True)

app = FastAPI()


@app.post("/transcribe-live", status_code=status.HTTP_201_CREATED)
async def transcribe_media_file(file: UploadFile):
    file_path = os.path.join(TMP_DIR, file.filename)

    # Temporary save the uploaded media locally
    with open(file_path, "wb") as media_file:
        media_file.write(file.file.read())

    try:
        res = tr.transcribe(file_path)
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Live-transcription error")
    finally:
        # Remove temp file
        os.remove(file_path)
        # Clear cache
        torch.cuda.empty_cache()

    return {"transcription": res}