import os
import json
import app.summarize as sm
from fastapi import FastAPI, HTTPException, status, Form
import tempfile
import traceback
import sys

app = FastAPI()
TMP_DIR = "/tmp"
os.makedirs(TMP_DIR, exist_ok=True)

@app.post("/summarize", status_code=status.HTTP_201_CREATED)
async def transcribe_media_file(json_data: str = Form(...)):
    transcription = json.loads(json_data)["diarization"]
    if transcription is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transcription data not in request body") # TODO should this be a error?
    
    with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp_file:
        json.dump(transcription, tmp_file, ensure_ascii=False, indent=4)
        tmp_file_path = tmp_file.name
    try:
        res = sm.create_summarize(tmp_file_path)
    except Exception as e:
        #print(transcription)
        print(f"An error occurred: {e}", file=sys.stderr)
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Summarization error")

    return {"summarization": res}