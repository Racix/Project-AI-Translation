import aiohttp
import asyncio
import json
import os
import pymongo
from app.connectionManager import ConnectionManager
from bson.objectid import ObjectId
from fastapi import FastAPI, HTTPException, UploadFile, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from websockets.exceptions import ConnectionClosedOK

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to restrict origins as needed
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.environ['UPLOAD_DIR']

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Connect to mongodb
client = pymongo.MongoClient(f"mongodb://{os.environ['MONGO_ADDRESS']}:{os.environ['MONGO_PORT']}/")
db = client["api"]
media_col = db["media"]
analysis_col = db["analysis"]
print(client) #TODO print for debug connection 

# Websocket analysis status manager
analysisManager = ConnectionManager()


@app.get("/media")
async def get_all_media():
    res = list(media_col.find())
    for row in res:
        row['_id'] = str(row['_id'])
    return {"message": res}


@app.post("/media", status_code=status.HTTP_201_CREATED)
async def upload_media(file: UploadFile):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded media locally
    with open(file_path, "wb") as media_file:
        media_file.write(file.file.read())
    
    # Parse data and insert into database
    data = {"name": file.filename, "file_path": file_path}
    res = media_col.insert_one(data)
    
    return {"message": "Media file uploaded successfully", "media_id": str(res.inserted_id)}


@app.get("/media/{media_id}")
async def get_media_by_id(media_id: str):
    media_info = media_col.find_one({"_id": ObjectId(media_id)})
    if media_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Media file with id {media_id} was not found")

    media_path = media_info["file_path"]
    if not os.path.exists(media_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The assisiating media file for id {media_id} was not found")

    return FileResponse(media_info["file_path"], media_type="media/mp4", filename=media_info["name"])


# @app.patch("/media/{media_id}") TODO implement


# @app.delete("/media/{media_id}") TODO implement


@app.post("/media/{media_id}/analysis", status_code=status.HTTP_202_ACCEPTED)
async def start_media_analysis(media_id: str, background_tasks: BackgroundTasks):
    media_info = media_col.find_one({"_id": ObjectId(media_id)})
    if media_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found")

    background_tasks.add_task(analyze, media_info['file_path'], media_id)

    return {"message": "Media file analysis started"}


async def analyze(file_path: str, media_id: str):
    timeout_seconds = 600 #TODO Find a good timeout
    session_timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    transcribe_url = f"http://{os.environ['TRANSCRIPTION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/transcribe"
    diarize_url = f"http://{os.environ['DIARIZATION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/diarize"
    transcription = {}
    diarization = {}
    data = {}

    # Transcribe
    with open(file_path, 'rb') as file:
        try:
            async with aiohttp.ClientSession(timeout=session_timeout) as session:
                data = {"status": status.HTTP_200_OK, "message": "Transcription started..."}
                asyncio.create_task(analysisManager.broadcast(data))
                async with session.post(transcribe_url, data={'file': file}) as response:
                    if response.status == status.HTTP_201_CREATED:
                        transcription = await response.json()
                        data = {"status": status.HTTP_200_OK, "message": "Transcription done."}
                    else:
                        data = {"status": response.status, "message": "Transcription error."}
                        return
        except TimeoutError as e:
            print("Error while connecting for transcription:", e)
            data = {"status": status.HTTP_504_GATEWAY_TIMEOUT, "message": "Transcription timed out."}
            return
        finally:
            asyncio.create_task(analysisManager.broadcast(data))

    # Diarize
    with open(file_path, 'rb') as file: 
        form = aiohttp.FormData()
        form.add_field('json_data', json.dumps(transcription), content_type='application/json')
        form.add_field('file', file)
        try:
            async with aiohttp.ClientSession(timeout=session_timeout) as session:
                data = {"status": status.HTTP_200_OK, "message": "Diarization started..."}
                asyncio.create_task(analysisManager.broadcast(data))
                async with session.post(diarize_url, data=form) as response:
                    if response.status == status.HTTP_201_CREATED:
                        diarization = await response.json()
                        data = {"status": status.HTTP_200_OK, "message": "Diarization done."}
                    else:
                        data = {"status": response.status, "message": "Diarization error."}
                        return
        except TimeoutError as e:
            print("Error while connecting for transcription:", e)
            data = {"status": status.HTTP_504_GATEWAY_TIMEOUT, "message": "Diarization timed out."}
            return
        finally:
            asyncio.create_task(analysisManager.broadcast(data))

    analysis_col.delete_one({"media_id": ObjectId(media_id)})
    diarization['media_id'] = ObjectId(media_id)
    analysis_col.insert_one(diarization)
    data = {"status": status.HTTP_201_CREATED, "message": "Analysis done."}
    asyncio.create_task(analysisManager.broadcast(data))


@app.get("/media/{media_id}/analysis")
async def get_media_analysis(media_id: str):
    analysis_info = analysis_col.find_one({"media_id": ObjectId(media_id)}, {"_id": 0, "media_id": 0})
    if analysis_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media file not found")

    return {"message": analysis_info, "media_id": media_id}


# @app.delete("/media/{media_id}/analysis") TODO implement


@app.websocket("/ws/analysis/{media_id}")
async def websocket_endpoint(websocket: WebSocket, media_id: str):
    await analysisManager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            data["media_id"] = media_id
            await analysisManager.broadcast(data)
    except (WebSocketDisconnect, ConnectionClosedOK):
        pass
    except Exception as e:
        print("Analysis websocket error:", e)
    finally:
        analysisManager.disconnect(websocket)  
        print(f"Client {websocket.client} disconnected")
