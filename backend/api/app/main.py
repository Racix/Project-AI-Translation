from fastapi import FastAPI, HTTPException, UploadFile, status
from starlette.responses import FileResponse
import os
import pymongo

app = FastAPI()

# Define the directory where video files will be saved
UPLOAD_DIR = "/videos"

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Mock data to store video information
videos_db = {}

mongoClient = pymongo.MongoClient("mongodb://10.20.0.2:27017/")
print(mongoClient)

@app.get("/videos")
async def get_videos():
    return list(videos_db.values())


@app.post("/videos", status_code=status.HTTP_201_CREATED)
async def upload_video(file: UploadFile):

    # Generate a unique filename for the uploaded video
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Save the uploaded video locally
    with open(file_path, "wb") as video_file:
        video_file.write(file.file.read())

    # Increment video_id and save to mock database
    video_id = len(videos_db) + 1
    videos_db[str(video_id)] = {"name": file.filename, "file_path": file_path}

    return {"message": "Video uploaded successfully", "video_id": video_id}


@app.get("/videos/{video_id}")
async def get_video(video_id: str):
    video_info = videos_db.get(video_id)
    if video_info is None:
        raise HTTPException(status_code=404, detail="Video not found")

    video_path = video_info["file_path"]
    if not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    # Return the video file as a response
    return FileResponse(video_path, media_type="video/mp4", filename=video_info["name"])


# @app.patch("/videos/{video_id}") TODO implement
# @app.delete("/videos/{video_id}") TODO implement


@app.post("/videos/{video_id}/analysis")
async def start_video_analysis(video_id: str):
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")

    return {"message": "Video analysis not implemented yet", "video_id": video_id}


@app.get("/videos/{video_id}/analysis")
async def get_video_analysis(video_id: str):
    if video_id not in videos_db:
        raise HTTPException(status_code=404, detail="Video not found")

    return {"message": "Video analysis not implemented yet", "video_id": video_id}


# @app.delete("/videos/{video_id}/analysis") TODO implement
