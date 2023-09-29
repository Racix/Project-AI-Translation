import os
import pymongo
import app.whisperTest as whisperTest
from fastapi import FastAPI, HTTPException, UploadFile, status, BackgroundTasks
from starlette.responses import FileResponse, JSONResponse
from bson.objectid import ObjectId

app = FastAPI()

# Directory where video files will be saved
UPLOAD_DIR = "/videos"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Connect to mongodb
mongo_port = os.environ['MONGO_PORT']
mongo_address = os.environ['MONGO_ADDRESS']
client = pymongo.MongoClient(f"mongodb://{mongo_address}:{mongo_port}/")
db = client["api"]
video_col = db["videos"]
analysis_col = db["analysis"]
print(client) #TODO print for debug connection 


@app.get("/videos")
async def get_videos():
    res = list(video_col.find())
    for row in res:
        row['_id'] = str(row['_id'])
    return {"message": res}


@app.post("/videos", status_code=status.HTTP_201_CREATED)
async def upload_video(file: UploadFile):

    # Generate a unique filename for the uploaded video
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded video locally
    with open(file_path, "wb") as video_file:
        video_file.write(file.file.read())
    
    # Parse data and insert into database
    data = {"name": file.filename, "file_path": file_path}
    res = video_col.insert_one(data)
    
    return {"message": "Video uploaded successfully", "video_id": str(res.inserted_id)}


@app.get("/videos/{video_id}")
async def get_video(video_id: str):
    video_info = video_col.find_one({"_id": ObjectId(video_id)})
    if video_info is None:
        raise HTTPException(status_code=404, detail=f"Video with id {video_id} was not found")

    video_path = video_info["file_path"]
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail=f"The assisiating video file for id {video_id} was not found")

    # Return the video file as a response
    return FileResponse(video_info["file_path"], media_type="video/mp4", filename=video_info["name"])


# @app.patch("/videos/{video_id}") TODO implement


# @app.delete("/videos/{video_id}") TODO implement


@app.post("/videos/{video_id}/analysis", status_code=status.HTTP_202_ACCEPTED)
async def start_video_analysis(video_id: str, background_tasks: BackgroundTasks):
    video_info = video_col.find_one({"_id": ObjectId(video_id)})
    if video_info is None:
        raise HTTPException(status_code=404, detail="Video not found")
    background_tasks.add_task(analyze, video_info, video_id)
    return {"message": "Video analysis started",}


def analyze(video_info, video_id):
    analysis_col.delete_one({"video_id": ObjectId(video_id)})
    whisper_res = whisperTest.transcribe(video_info['file_path'])
    whisper_res["video_id"] = ObjectId(video_id)
    analysis_col.insert_one(whisper_res)


@app.get("/videos/{video_id}/analysis")
async def get_video_analysis(video_id: str):
    analysis_info = analysis_col.find_one({"video_id": ObjectId(video_id)}, {"_id":0,"video_id":0})
    if analysis_info is None:
        raise HTTPException(status_code=404, detail="Video not found")

    return {"message": analysis_info, "video_id": video_id}


# @app.delete("/videos/{video_id}/analysis") TODO implement
