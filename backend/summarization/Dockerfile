FROM nvidia/cuda:11.0.3-runtime-ubuntu20.04

WORKDIR /summarize

RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y curl && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /summarize/models

RUN curl -L -o /summarize/models/mistral7b "https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF/resolve/main/openhermes-2.5-mistral-7b.Q4_K_M.gguf?download=true"

COPY ./requirements.txt /summarize/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /summarize/requirements.txt

COPY ./app /summarize/app

