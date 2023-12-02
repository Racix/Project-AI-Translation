FROM nvidia/cuda:12.0.0-cudnn8-devel-ubuntu22.04

WORKDIR /summarize

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /summarize/models

RUN curl -L -o /summarize/models/mistral7b "https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF/resolve/main/openhermes-2.5-mistral-7b.Q4_K_M.gguf?download=true"

RUN apt-get update && \
    apt-get install -y build-essential gcc g++ && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

ENV CUDA_DOCKER_ARCH=all
ENV LLAMA_CUBLAS=1

RUN CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install llama-cpp-python

COPY ./requirements.txt /summarize/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /summarize/requirements.txt

COPY ./app /summarize/app

