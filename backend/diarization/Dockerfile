FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

WORKDIR /diarization

RUN apt-get update && \
    apt-get install -y ffmpeg wget unzip git curl && \
    apt-get install -y build-essential gcc && \
    apt-get install -y python3 python3-pip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/vad_multilingual_marblenet/versions/1.10.0/zip -O vad_multilingual_marblenet_1.10.0.zip && \
    wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/titanet_large/versions/v1/zip -O titanet_large_v1.zip && \
    wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/diar_msdd_telephonic/versions/1.0.1/zip -O diar_msdd_telephonic_1.0.1.zip && \
    unzip vad_multilingual_marblenet_1.10.0.zip -d /diarization/models && \
    unzip titanet_large_v1.zip -d /diarization/models && \
    unzip diar_msdd_telephonic_1.0.1.zip -d /diarization/models && \
    rm vad_multilingual_marblenet_1.10.0.zip titanet_large_v1.zip diar_msdd_telephonic_1.0.1.zip

COPY ./requirements.txt /diarization/requirements.txt

RUN pip install --no-cache-dir --upgrade Cython==3.0.3
RUN pip install --no-cache-dir --upgrade -r /diarization/requirements.txt
RUN pip install torch==2.1.1+cu118 torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
COPY ./app /diarization/app