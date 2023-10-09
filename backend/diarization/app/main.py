import app.diarize as diarize
import os
import pymongo
from fastapi import FastAPI, HTTPException, status, BackgroundTasks, Request
from bson.objectid import ObjectId

# Connect to mongodb
client = pymongo.MongoClient(f"mongodb://{os.environ['MONGO_ADDRESS']}:{os.environ['MONGO_PORT']}/")
db = client["api"]
media_col = db["media"]
analysis_col = db["analysis"]

app = FastAPI()


@app.post("/diarize/{media_id}", status_code=status.HTTP_202_ACCEPTED)
async def diarize_media_file(media_id: str, request: Request, background_tasks: BackgroundTasks):
    media_info = media_col.find_one({"_id": ObjectId(media_id)})
    if media_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found")
    
    json = await request.json()
    transcription = json["transcription"]
    if transcription is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transcription data not in request body")

    background_tasks.add_task(diarize, media_id, media_info, transcription)

    return {"message": "Diarization of file started"}


def diarize(media_id: str, media_info, transcription):
    analysis_col.delete_one({"media_id": ObjectId(media_id)})
    y, sr = diarize.preprocess(media_info['file_path'])
    print(y)
    print(sr)

    diarize_res = transcription # TODO diarize the transcription
    diarize_res["media_id"] = ObjectId(media_id)
    analysis_col.insert_one(transcription)
    print("Diarized transcription:", diarize_res)

    