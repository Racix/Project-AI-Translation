FROM nvidia/cuda:11.6.1-cudnn8-runtime-ubuntu20.04


WORKDIR /transcription

RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade faster-whisper==0.9.0
COPY ./loadModel.py /transcription/loadModel.py
RUN python3 /transcription/loadModel.py

COPY ./requirements.txt /transcription/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /transcription/requirements.txt

COPY ./app /transcription/app


