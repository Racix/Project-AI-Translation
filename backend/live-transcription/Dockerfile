FROM python:3.10

WORKDIR /live-transcription

RUN pip install --no-cache-dir --upgrade faster-whisper==0.9.0
COPY ./loadModel.py /live-transcription/loadModel.py
RUN python /live-transcription/loadModel.py

COPY ./requirements.txt /live-transcription/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /live-transcription/requirements.txt

COPY ./app /live-transcription/app

# EXPOSE 8080

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
