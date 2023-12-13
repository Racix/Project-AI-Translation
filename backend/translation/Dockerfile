FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

WORKDIR /translation

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

ENV ARGOS_DEVICE_TYPE=cuda

RUN pip install --no-cache-dir --upgrade argostranslate==1.9.1

COPY ./requirements.txt /translation/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /translation/requirements.txt


COPY ./app /translation/app