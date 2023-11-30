FROM nvidia/cuda:11.6.1-cudnn8-runtime-ubuntu20.04

WORKDIR /transcription

RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get update && \
    apt-get install -y python3.10 python3.10-dev python3.10-distutils && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py

RUN pip install --no-cache-dir --upgrade faster-whisper==0.9.0

COPY ./requirements.txt /transcription/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /transcription/requirements.txt

COPY ./loadModel.py /transcription/loadModel.py

RUN python3.10 /transcription/loadModel.py

COPY ./app /transcription/app


