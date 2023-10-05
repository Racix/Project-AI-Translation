import os
import pymongo
import aiohttp
import json
import app.transcribe as transcribe
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from bson.objectid import ObjectId

# Connect to mongodb
client = pymongo.MongoClient(f"mongodb://{os.environ['MONGO_ADDRESS']}:{os.environ['MONGO_PORT']}/")
db = client["api"]
media_col = db["media"]
print("Mongoclient:", client)

app = FastAPI()


@app.post("/transcribe/{media_id}", status_code=status.HTTP_202_ACCEPTED)
async def transcribe_media_file(media_id: str, background_tasks: BackgroundTasks):
    media_info = media_col.find_one({"_id": ObjectId(media_id)})
    statusSession = aiohttp.ClientSession()
    url = f"ws://{os.environ['API_ADDRESS']}:{os.environ['API_PORT_GUEST']}/ws/analysis/{media_id}"
    # ws = statusSession.ws_connect(url)
    media_info = None
    if media_info is None:
        # async with aiohttp.ClientSession() as session:
        #     url = f"http://{os.environ['API_ADDRESS']}:{os.environ['API_PORT_GUEST']}/ws/analysis/{media_id}"
        async with statusSession.ws_connect(url) as ws:
            ws.send_json({"status": status.HTTP_404_NOT_FOUND, "message": "Transcription failed. Media file not found."})

        # print(statusSession)
        # print(ws)
        # await ws.send_json({"status": status.HTTP_404_NOT_FOUND, "message": "Transcription failed. Media file not found."})
        
        # ws.close()
        statusSession.close()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found")

    background_tasks.add_task(trancribe, media_id, media_info, statusSession)

    return {"message": "Trancription of file started"}


async def trancribe(media_id: str, media_info, statusSession):
    async with statusSession.ws_connect(url) as ws:
        ws.send_json({"status": status.HTTP_200_OK, "message": "Transcription started."})
    trancribe_res = transcribe.transcribe(media_info['file_path'])
    print("trancribe_res:", trancribe_res)
    async with statusSession.ws_connect(url) as ws:
        ws.send_json({"status": status.HTTP_200_OK, "message": "Transcription done."})
    # ws.close()
    statusSession.close()
    async with aiohttp.ClientSession() as session:
        url = f"http://{os.environ['DIARIZATION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/diarize/{media_id}"
        res = await session.post(url, json={'transcription': trancribe_res})
        print("res:", res)