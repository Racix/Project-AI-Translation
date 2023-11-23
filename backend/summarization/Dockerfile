FROM python:3.10

WORKDIR /summarize

RUN mkdir -p /summarize/models

RUN curl -L -o /summarize/models/mistral7b "https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF/resolve/main/openhermes-2.5-mistral-7b.Q4_K_M.gguf?download=true"

COPY ./requirements.txt /summarize/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /summarize/requirements.txt

COPY ./app /summarize/app