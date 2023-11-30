FROM nvidia/cuda:11.0.3-runtime-ubuntu20.04

WORKDIR /diarization

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get install -y wget && \
    apt-get install -y unzip && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/vad_multilingual_marblenet/versions/1.10.0/zip -O vad_multilingual_marblenet_1.10.0.zip && \
    wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/titanet_large/versions/v1/zip -O titanet_large_v1.zip && \
    wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/diar_msdd_telephonic/versions/1.0.1/zip -O diar_msdd_telephonic_1.0.1.zip && \
    unzip vad_multilingual_marblenet_1.10.0.zip -d /diarization/models && \
    unzip titanet_large_v1.zip -d /diarization/models && \
    unzip diar_msdd_telephonic_1.0.1.zip -d /diarization/models && \
    rm vad_multilingual_marblenet_1.10.0.zip titanet_large_v1.zip diar_msdd_telephonic_1.0.1.zip

RUN apt-get update && \
    apt-get install -y python3-pip python3-dev && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /diarization/requirements.txt

RUN pip install --no-cache-dir --upgrade Cython==3.0.3
RUN pip install --no-cache-dir --upgrade -r /diarization/requirements.txt

COPY ./app /diarization/app

ENV LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH

