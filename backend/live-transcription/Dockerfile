FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

WORKDIR /live-transcription

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade faster-whisper==0.9.0

COPY ./requirements.txt /live-transcription/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /live-transcription/requirements.txt

COPY ./loadModel.py /live-transcription/loadModel.py

RUN python3 /live-transcription/loadModel.py

COPY ./app /live-transcription/app
