FROM python:3.10

WORKDIR /diarization

# RUN ngc registry model download-version "nvidia/nemo/vad_multilingual_marblenet:1.10.0"
RUN wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/vad_multilingual_marblenet/versions/1.10.0/zip -O vad_multilingual_marblenet_1.10.0.zip
RUN wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/titanet_large/versions/v1/zip -O titanet_large_v1.zip
RUN wget --content-disposition https://api.ngc.nvidia.com/v2/models/nvidia/nemo/diar_msdd_telephonic/versions/1.0.1/zip -O diar_msdd_telephonic_1.0.1.zip

COPY ./requirements.txt /diarization/requirements.txt

RUN pip install Cython
RUN pip install --no-cache-dir --upgrade -r /diarization/requirements.txt

RUN unzip vad_multilingual_marblenet_1.10.0.zip -d /models
RUN unzip titanet_large_v1.zip -d /models
RUN unzip diar_msdd_telephonic_1.0.1.zip -d /models

COPY ./app /diarization/app

# EXPOSE 8080

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
