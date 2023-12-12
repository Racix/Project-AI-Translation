FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

WORKDIR /translation

RUN pip install --no-cache-dir --upgrade argostranslate==1.9.1


COPY ./requirements.txt /translation/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /translation/requirements.txt


COPY ./app /translation/app