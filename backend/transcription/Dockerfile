FROM python:3.10 as python_stage

WORKDIR /transcription

RUN pip install --no-cache-dir --upgrade faster-whisper==0.9.0
COPY ./loadModel.py /transcription/loadModel.py
RUN python /transcription/loadModel.py

COPY ./requirements.txt /transcription/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /transcription/requirements.txt

COPY ./app /transcription/app

FROM nvidia/cuda:11.0.3-runtime-ubuntu20.04

COPY --from=python_stage /transcription /transcription

ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

WORKDIR /transcription/app
