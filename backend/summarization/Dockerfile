FROM nvidia/cuda:11.6.1-cudnn8-runtime-ubuntu20.04

WORKDIR /summarize

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

RUN mkdir -p /summarize/models

RUN curl -L -o /summarize/models/mistral7b "https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF/resolve/main/openhermes-2.5-mistral-7b.Q4_K_M.gguf?download=true"

RUN apt-get update && \
    apt-get install -y build-essential gcc g++ && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /summarize/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /summarize/requirements.txt

COPY ./app /summarize/app

