FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

WORKDIR /transcription

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade faster-whisper==0.9.0

COPY ./requirements.txt /transcription/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /transcription/requirements.txt

COPY ./loadModel.py /transcription/loadModel.py

RUN python3.10 /transcription/loadModel.py

COPY ./app /transcription/app
