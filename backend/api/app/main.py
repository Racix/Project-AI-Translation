import aiohttp
import asyncio
import json
import mimetypes
import os
import pymongo
from typing import Any
from app.connectionManager import ConnectionManager
from bson.objectid import ObjectId
from fastapi import FastAPI, HTTPException, UploadFile, Body, status, BackgroundTasks, WebSocket, WebSocketDisconnect
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
    if not is_media_file(file):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file format.")

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
    # Check if media exists
    media_info = try_find_media(media_id)

    return FileResponse(media_info['file_path'], filename=media_info["name"])


@app.delete("/media/{media_id}")
async def delete_media_by_id(media_id: str):
    # Check if media exists
    media_info = try_find_media(media_id)

    # Delete all data about media_id
    analysis_col.delete_one({"media_id": ObjectId(media_id)})
    media_col.delete_one({"_id": ObjectId(media_id)})

    if os.path.exists(media_info['file_path']):
        os.remove(media_info['file_path'])

    return {"message": "Media deleted successfully", "media_id": media_id}


@app.post("/media/{media_id}/analysis", status_code=status.HTTP_202_ACCEPTED)
async def start_media_analysis(media_id: str, background_tasks: BackgroundTasks):
    # Check if media exists
    media_info = try_find_media(media_id)

    analysis_info = analysis_col.find_one({"media_id": ObjectId(media_id)})
    if analysis_info is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Analysis already exists. To re-analze, delete the existing analysis.")

    # Start analysis in the background
    background_tasks.add_task(analyze, media_info['file_path'], media_id)
    return {"message": "Media file analysis started"}


async def analyze(file_path: str, media_id: str):
    timeout_seconds = 600 #TODO Find a good timeout
    session_timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    transcribe_url = f"http://{os.environ['TRANSCRIPTION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/transcribe"
    diarize_url = f"http://{os.environ['DIARIZATION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/diarize"
    summarize_url = f"http://{os.environ['SUMMARIZATION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/summarize"
    transcription = {}
    diarization = {}
    summarize = {}
    status_data = {}

    # Transcribe
    try:
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            status_data = {"status": status.HTTP_200_OK, "message": "Transcription started..."}
            asyncio.create_task(analysisManager.broadcast(status_data, media_id))
            with open(file_path, 'rb') as file:
                async with session.post(transcribe_url, data={'file': file}) as response:
                    if response.status == status.HTTP_201_CREATED:
                        transcription = await response.json()
                        status_data = {"status": status.HTTP_200_OK, "message": "Transcription done."}
                    else:
                        status_data = {"status": response.status, "message": "Transcription error."}
                        return
    except TimeoutError as e:
        print("TimeoutError while transcribing:", e)
        status_data = {"status": status.HTTP_504_GATEWAY_TIMEOUT, "message": "Transcription timed out."}
        return
    except Exception as e:
        print("Unkonwn error while transcribing:", e)
        status_data = {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "Transcription error."}
        return
    finally:
        asyncio.create_task(analysisManager.broadcast(status_data, media_id))

    # Diarize
    try:
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            status_data = {"status": status.HTTP_200_OK, "message": "Diarization started..."}
            asyncio.create_task(analysisManager.broadcast(status_data, media_id))
            with open(file_path, 'rb') as file: 
                form = aiohttp.FormData()
                form.add_field('json_data', json.dumps(transcription), content_type='application/json')
                form.add_field('file', file)
                async with session.post(diarize_url, data=form) as response:
                    if response.status == status.HTTP_201_CREATED:
                        diarization = await response.json()
                        status_data = {"status": status.HTTP_200_OK, "message": "Diarization done."}
                    else:
                        status_data = {"status": response.status, "message": "Diarization error."}
                        return
    except TimeoutError as e:
        print("TimeoutError while diarizing:", e)
        status_data = {"status": status.HTTP_504_GATEWAY_TIMEOUT, "message": "Diarization timed out."}
        return
    except Exception as e:
        print("Unkonwn error while diarizing:", e)
        status_data = {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "Diarization error."}
        return
    finally:
        asyncio.create_task(analysisManager.broadcast(status_data, media_id))

    analysis_col.delete_one({"media_id": ObjectId(media_id)})
    diarization['media_id'] = ObjectId(media_id)
    analysis_col.insert_one(diarization)

    status_data = {"status": status.HTTP_201_CREATED, "message": "Analysis done."}
    asyncio.create_task(analysisManager.broadcast(status_data, media_id))


@app.get("/media/{media_id}/analysis")
async def get_media_analysis(media_id: str):
    # Check if media and analysis exists
    try_find_media(media_id)
    analysis_info = try_find_analysis(media_id)

    return {"message": analysis_info}


@app.put("/media/{media_id}/analysis")
async def update_media_analysis(media_id: str, segments: Any = Body(...)):
    # Check if media and analysis exists
    try_find_media(media_id)
    try_find_analysis(media_id)

    analysis_col.update_one({"media_id": ObjectId(media_id)}, {"$set": segments})
    analysis_info = try_find_analysis(media_id)

    return {"message": analysis_info}


@app.delete("/media/{media_id}/analysis")
async def delete_media_analysis(media_id: str):
    # Check if media and analysis exists
    try_find_media(media_id)
    try_find_analysis(media_id)

    analysis_col.delete_one({"media_id": ObjectId(media_id)})

    return {"message": "Analysis deleted successfully", "media_id": media_id}


@app.websocket("/ws/analysis/{media_id}")
async def analysis_websocket(websocket: WebSocket, media_id: str):
    await analysisManager.connect(websocket, media_id)

    # Check if media exists
    try:
        media_info = media_col.find_one({"_id": ObjectId(media_id)})
    except Exception:
        await websocket.close(code = 4000, reason = "Invalid media id")
        analysisManager.disconnect(websocket, media_id)
        return
    if media_info is None:
        await websocket.close(code = 4040, reason = "Media info not found")
        analysisManager.disconnect(websocket, media_id)
        return
    if not os.path.exists(media_info["file_path"]):
        await websocket.close(code = 4040, reason = "Media file not found")
        analysisManager.disconnect(websocket, media_id)
        return
    
    # Everything ok -> client listens
    try:
        while True:
            # Only here to keep the connection open to allow clients to listen
            await websocket.receive_json()
    except (WebSocketDisconnect, ConnectionClosedOK):
        pass
    except Exception as e:
        print("Analysis websocket error:", e)
    finally:
        analysisManager.disconnect(websocket, media_id)
        print(f"Client {websocket.client} disconnected")


@app.post("/media/{media_id}/analysis/summary")
async def get_media_summary(media_id: str, background_tasks: BackgroundTasks):
    # Check if media and analysis exists
    media_info = try_find_media(media_id)

    # Start analysis in the background
    background_tasks.add_task(do_summary, media_info['file_path'], media_id)
    return {"message": "Media file summary started"}


@app.get("/media/{media_id}/analysis/summary")
async def get_media_analysis(media_id: str):
    # Check if media and analysis exists
    try_find_media(media_id)
    analysis_info = try_find_analysis(media_id)
    analysis_info['summary'] = "This is a summary"
    analysis_col.update_one({"media_id": ObjectId(media_id)}, {"$set": {"summary": analysis_info['summary']}})

    updated_analysis_info = try_find_analysis(media_id)

    return {"message": updated_analysis_info}


async def do_summary(file_path: str, media_id: str):
    summarize_url = f"http://{os.environ['SUMMARIZATION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/summarize"
    summarize = {}
    try_find_media(media_id)
    analysis_info = try_find_analysis(media_id)

    try:
        status_data = {"status": status.HTTP_200_OK, "message": "Summarization started..."}
        asyncio.create_task(analysisManager.broadcast(status_data, media_id))

        with open(file_path, 'rb') as file:
            form_new = aiohttp.FormData()
            form_new.add_field('json_data', json.dumps(analysis_info), content_type='application/json')
            form_new.add_field('file', file)

            async with aiohttp.request('POST', summarize_url, data=form_new) as response:
                if response.status == status.HTTP_201_CREATED:
                    summarize = await response.json()
                    status_data = {"status": status.HTTP_200_OK, "message": "Summarization done."}
                else:
                    status_data = {"status": response.status, "message": "Summarization error."}
                    return
    except TimeoutError as e:
        print("TimeoutError while summarizing:", e)
        status_data = {"status": status.HTTP_504_GATEWAY_TIMEOUT, "message": "Summarization timed out."}
        return
    except Exception as e:
        print("Unknown error while summarizing:", e)
        status_data = {"status": status.HTTP_500_INTERNAL_SERVER_ERROR, "message": "Summarization error."}
        return
    finally:
        asyncio.create_task(analysisManager.broadcast(status_data, media_id))

    analysis_info['summary'] = summarize
    analysis_col.update_one({"media_id": ObjectId(media_id)}, {"$set": {"summary": analysis_info['summary']}})



def is_media_file(file: UploadFile):
    # Allowed media types
    allowed_media_types = ['audio', 'video']
    mime_type, _ = mimetypes.guess_type(file.filename)
    
    if mime_type:
        for media_type in allowed_media_types:
            if mime_type.startswith(media_type + '/'):
                return True

    return False


def try_find_media(media_id: str) -> dict[str, str]:
    """Help function for http endpoints to check if the media id is valid and media exists"""
    try:
        media_info = media_col.find_one({"_id": ObjectId(media_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid media id")
    if media_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media info not found")
    if not os.path.exists(media_info["file_path"]):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Media file not found")
    
    media_info['_id'] = str(media_info['_id'])
    return media_info


def try_find_analysis(media_id: str) -> dict[str, str]:
    """Help function for http endpoints to check if the analysis exists"""
    try:
        analysis_info = analysis_col.find_one({"media_id": ObjectId(media_id)})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid media id")
    if analysis_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analysis not found")
    
    analysis_info['_id'] = str(analysis_info['_id'])
    analysis_info['media_id'] = str(analysis_info['media_id'])
    return analysis_info
