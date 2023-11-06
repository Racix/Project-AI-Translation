import os
import app.translate as te
from fastapi import FastAPI, Request, HTTPException, status
import traceback

TMP_DIR = "/tmp"
os.makedirs(TMP_DIR, exist_ok=True)

app = FastAPI()


@app.post("/translate", status_code=status.HTTP_201_CREATED)
async def translate_analysis_file(request: Request):
    try:
        json_data = await request.json()
        print(json_data)
        res = te.translate_to_swedish(json_data)
    
    except Exception:
        print(traceback.format_exc())
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Translate error")

    return {"translation": res}