import aiohttp
import os
import pymongo
import app.transcribe as tr
from bson.objectid import ObjectId
from fastapi import FastAPI, HTTPException, status, BackgroundTasks

# Connect to mongodb
client = pymongo.MongoClient(f"mongodb://{os.environ['MONGO_ADDRESS']}:{os.environ['MONGO_PORT']}/")
db = client["api"]
media_col = db["media"]
print("Mongoclient:", client)

app = FastAPI()


@app.post("/transcribe/{media_id}", status_code=status.HTTP_202_ACCEPTED)
async def transcribe_media_file(media_id: str, background_tasks: BackgroundTasks):
    media_info = media_col.find_one({"_id": ObjectId(media_id)})
    if media_info is None:
        # Notify through websocket transcription failed
        async with aiohttp.ClientSession() as session:
            data = {"status": status.HTTP_404_NOT_FOUND, "message": "Transcription failed. Media file not found."}
            await send_status(data, media_id, session)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found")

    background_tasks.add_task(transcribe, media_id, media_info)

    return {"message": "Trancription of file started"}


async def send_status(data: dict, media_id: str, session):
    url = f"ws://{os.environ['API_ADDRESS']}:{os.environ['API_PORT_GUEST']}/ws/analysis/{media_id}"
    async with session.ws_connect(url) as ws:
        await ws.send_json(data)


async def transcribe(media_id: str, media_info):
    async with aiohttp.ClientSession() as session:
        # Notify through websocket transcription started
        data = {"status": status.HTTP_200_OK, "message": "Transcription started..."}
        await send_status(data, media_id, session)

        # Transcribe and send result to diarization model
        trancribe_res = tr.transcribe(media_info['file_path'])
        await send_diarization_req(media_id, trancribe_res)

        # Notify through websocket transcription finished
        data = {"status": status.HTTP_200_OK, "message": "Transcription done."}
        await send_status(data, media_id, session)


async def send_diarization_req(media_id, trancribe_res):
    async with aiohttp.ClientSession() as session:
        url = f"http://{os.environ['DIARIZATION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/diarize/{media_id}"
        res = await session.post(url, json={'transcription': trancribe_res})
        print("res:", res)