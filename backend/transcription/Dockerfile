FROM python:3.10

WORKDIR /transcription

RUN pip install --no-cache-dir --upgrade faster-whisper==0.9.0
COPY ./loadModel.py /transcription/loadModel.py
RUN python /transcription/loadModel.py

COPY ./requirements.txt /transcription/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /transcription/requirements.txt

COPY ./app /transcription/app

# EXPOSE 8080

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]