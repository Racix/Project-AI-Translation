import aiohttp
import asyncio
import json
import librosa
import mimetypes
import os
import io
import numpy as np
import pymongo
import soundfile as sf
import wave
from typing import Any
from app.connectionManager import ConnectionManager
from bson.objectid import ObjectId
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, Body, status, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydub import AudioSegment
from starlette.responses import FileResponse
from websockets.exceptions import ConnectionClosedOK

SAMPLE_RATE = 16000

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
translate_col = db["translation"]
print(client) #TODO print for debug connection 

# Websocket status managers
analysisManager = ConnectionManager()
liveTransciptionManager = ConnectionManager()


@app.get("/media")
async def get_all_media():
    res = list(media_col.find())
    for row in res:
        row['_id'] = str(row['_id'])
    return res


@app.post("/media", status_code=status.HTTP_201_CREATED)
async def upload_media(file: UploadFile, background_tasks: BackgroundTasks):
    if not is_media_file(file):
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, detail="Unsupported file format.")

    # Names and paths
    now = datetime.now()
    date = now.strftime('%Y-%m-%d %H:%M:%S.%f')
    storage_name = now.strftime(f'%Y_%m_%d_%H_%M_%S_%f_{file.filename}')
    wav_name = os.path.splitext(os.path.basename(storage_name))[0] + ".mono.wav"
    file_path = os.path.join(UPLOAD_DIR, storage_name)
    wav_path = os.path.join(UPLOAD_DIR, wav_name)

    # Save the uploaded media locally
    with open(file_path, "wb") as media_file:
        media_file.write(file.file.read())

    # Write file in the background
    background_tasks.add_task(write_mono_wav_file, file_path, wav_path)

    # Parse data and insert into database
    data = {"name": file.filename, "file_path": file_path, "wav_path": wav_path, "date": date}
    media_col.insert_one(data)
    
    data['_id'] = str(data['_id'])
    return data


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
    background_tasks.add_task(analyze, media_info['file_path'], media_info['wav_path'], media_id)
    return {"message": "Media file analysis started"}


async def analyze(file_path: str, wav_path: str, media_id: str):
    timeout_seconds = 600 #TODO Find a good timeout
    session_timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    transcribe_url = f"http://{os.environ['TRANSCRIPTION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/transcribe"
    diarize_url = f"http://{os.environ['DIARIZATION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/diarize"
    transcription = {}
    diarization = {}
    status_data = {}

    # Crete the mono .wav version if not exists
    if not os.path.exists(wav_path):
        status_data = {"status": status.HTTP_200_OK, "message": "Converting to wav..."}
        asyncio.create_task(analysisManager.broadcast(status_data, media_id))
        await write_mono_wav_file(file_path, wav_path)

    # Transcribe
    try:
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            status_data = {"status": status.HTTP_200_OK, "message": "Transcription started..."}
            asyncio.create_task(analysisManager.broadcast(status_data, media_id))
            with open(wav_path, 'rb') as file:
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
            with open(wav_path, 'rb') as file: 
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

    return analysis_info


@app.put("/media/{media_id}/analysis")
async def update_media_analysis(media_id: str, segments: Any = Body(...)):
    # Check if media and analysis exists
    try_find_media(media_id)
    try_find_analysis(media_id)

    analysis_col.update_one({"media_id": ObjectId(media_id)}, {"$set": segments})
    analysis_info = try_find_analysis(media_id)

    return analysis_info


@app.delete("/media/{media_id}/analysis")
async def delete_media_analysis(media_id: str):
    # Check if media and analysis exists
    try_find_media(media_id)
    try_find_analysis(media_id)

    analysis_col.delete_one({"media_id": ObjectId(media_id)})

    return {"message": "Analysis deleted successfully", "media_id": media_id}


@app.post("/media/{media_id}/analysis/translate/{language}", status_code=status.HTTP_201_CREATED)
async def start_translation(media_id: str, language: str,):
    # Check if media exists
    try_find_media(media_id)
    try_find_analysis(media_id)

    translation = await translate_analysis(media_id, language)
    return translation


async def translate_analysis(media_id: str, to_language: str) -> dict:
    timeout_seconds = 300
    session_timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    translate_url = f"http://{os.environ['TRANSLATION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/translate"
    translation = {}
    try:
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            json_analysis = analysis_col.find_one({"media_id": ObjectId(media_id)})
            json_analysis['_id'] = str(json_analysis['_id'])
            json_analysis['media_id'] = str(json_analysis['media_id'])
            detected_language = json_analysis["diarization"]["Detected language"]
            async with session.post(translate_url, json=json_analysis, params={"from_language": detected_language, "to_language": to_language}) as response:
                if response.status == status.HTTP_201_CREATED:
                    translation = await response.json()
                    print("TRANS:", translation)
                else:
                    raise Exception()
    except TimeoutError as e:
        print("TimeoutError while translating:", e)
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=f"TimeoutError while translating")
    except Exception as e:
        print("Unkonwn error while translating:", e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unkonwn error while translating")
    
    translation['media_id'] = ObjectId(media_id)
    translate_col.insert_one(translation)

    translation['_id'] = str(translation['_id'])
    translation['media_id'] = str(translation['media_id'])
    return translation


@app.get("/media/{media_id}/analysis/translate/{language}")
async def get_translation(media_id: str, language: str):
    try_find_media(media_id)
    translation_info = try_find_translation(media_id, language)

    return translation_info


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


@app.websocket("/ws/live-transcription/{live_id}")
async def live_transcription_websocket(websocket: WebSocket, live_id: str):
    timeout_seconds = 30 #TODO Find a good timeout
    session_timeout = aiohttp.ClientTimeout(total=timeout_seconds)
    transcribe_url = f"http://{os.environ['TRANSCRIPTION_ADDRESS']}:{os.environ['API_PORT_GUEST']}/transcribe"
    max_queue_len  = 25
    min_queue_len  = 15
    queue = []
    

    await liveTransciptionManager.connect(websocket, live_id)
    
    try:
        while True:
            data = await websocket.receive_bytes()
            data = np.frombuffer(data, dtype=np.int16)

            queue.append(data)

            queue_len = queue_length(queue)
            print("queue_len before pop", queue_len)

            queue_len = queue_length(queue)

            while queue_len > max_queue_len and queue_len-(len(queue[0])/SAMPLE_RATE) > min_queue_len:
                queue.pop(0)
                queue_len = queue_length(queue)


            queue_len = queue_length(queue)
            print("queue_len after pop", queue_len)

            data = bytes_to_wave(queue)

            
            form_data = aiohttp.FormData()
            form_data.add_field('file', data, filename=f'live_id_{live_id}_{hash(data)}.wav', content_type='audio/wav')

            transcription = None
            text = None

            try:
                async with aiohttp.ClientSession(timeout=session_timeout) as session:
                    async with session.post(transcribe_url, data=form_data) as response:
                        print("Response: ", response)
                        if response.status == status.HTTP_201_CREATED:
                            transcription = await response.json()
            except TimeoutError as e:
                print("TimeoutError while live transcribing:", e)
            except Exception as e:
                print("Unkonwn error while live transcribing:", e)

            if transcription is not None:
                segments = transcription['transcription']['segments']
                text = ''.join(item['text'] for item in segments)

            print("text:", transcription)
            if text is not None:
                await liveTransciptionManager.broadcast(text, live_id)

    except (WebSocketDisconnect, ConnectionClosedOK):
        pass
    except Exception as e:
        print("Live transcription websocket error:", e)
    finally:
        liveTransciptionManager.disconnect(websocket, live_id)
        print(f"Client {websocket.client} disconnected")

    
def bytes_to_wave(queue):
    # Ensure the array is of type int16

    
    # print("InitDATA: ", queue)
    n_channels = 1
    
    
    # print("laterDAta: ", queue)
    # print("n_channels", n_channels, "sample_rate", SAMPLE_RATE)
    
    # Create a wave file in memory
    with io.BytesIO() as wave_buffer:
        with wave.open(wave_buffer, 'w') as wave_file:
            wave_file.setnchannels(n_channels)  # 1 channel (mono)
            wave_file.setsampwidth(2)   # 2 bytes per sample (16-bit PCM)
            wave_file.setframerate(SAMPLE_RATE)

            data = np.concatenate(queue)
            wave_file.writeframes(data.tobytes())
            
        
        # Get the wave file data from the buffer
        wave_data = wave_buffer.getvalue()
        with open('output.wav', 'wb') as output_file:
                output_file.write(wave_data)

        return wave_data


def queue_length(queue):
    """Queue lenght in seconds"""
    length = 0
    for sound in queue:
        length += len(sound)

    return length/SAMPLE_RATE


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


def try_find_translation(media_id: str, language: str) -> dict[str, str]:
    """Help function for http endpoints to check if the translation exists"""
    try:
        translation_info = translate_col.find_one({"media_id": ObjectId(media_id), "translation.language": language})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid media id")
    if translation_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Translation not found")
    
    translation_info['_id'] = str(translation_info['_id'])
    translation_info['media_id'] = str(translation_info['media_id'])
    return translation_info
  

async def write_mono_wav_file(file_path: str, wav_path: str):
    # Crete the mono .wav version
    convert_to_wav(file_path, wav_path)
    to_mono(wav_path)


def convert_to_wav(file_path: str, output_path: str):
    """Converts audio file to .wav format."""
    audio = AudioSegment.from_file(file_path)
    audio.export(output_path, format="wav")

    
def to_mono(file_path: str):
    """Convert audio file to mono and 16000hz subsample"""
    y, sr = librosa.load(file_path, sr=16000, mono=True)
    sf.write(file_path, y, sr)
