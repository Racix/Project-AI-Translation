FROM nvidia/cuda:11.6.1-cudnn8-runtime-ubuntu20.04

WORKDIR /diarization

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get install -y wget && \
    apt-get install -y unzip && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get install -y python3.10 python3.10-dev python3.10-distutils && \
    apt-get install -y git && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/vad_multilingual_marblenet/versions/1.10.0/zip -O vad_multilingual_marblenet_1.10.0.zip && \
    wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/titanet_large/versions/v1/zip -O titanet_large_v1.zip && \
    wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/diar_msdd_telephonic/versions/1.0.1/zip -O diar_msdd_telephonic_1.0.1.zip && \
    unzip vad_multilingual_marblenet_1.10.0.zip -d /diarization/models && \
    unzip titanet_large_v1.zip -d /diarization/models && \
    unzip diar_msdd_telephonic_1.0.1.zip -d /diarization/models && \
    rm vad_multilingual_marblenet_1.10.0.zip titanet_large_v1.zip diar_msdd_telephonic_1.0.1.zip

RUN curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.10 get-pip.py && \
    rm get-pip.py

RUN apt-get update && \
    apt-get install -y build-essential gcc && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /diarization/requirements.txt

RUN pip install --no-cache-dir --upgrade Cython==3.0.3
RUN pip install --no-cache-dir --upgrade -r /diarization/requirements.txt

RUN pip install torch==1.13.1+cu116 torchvision==0.14.1+cu116 torchaudio==0.13.1 --extra-index-url https://download.pytorch.org/whl/cu116

COPY ./app /diarization/app



