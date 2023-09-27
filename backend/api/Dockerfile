FROM python:3.10

WORKDIR /api

RUN pip install --no-cache-dir --upgrade faster-whisper

COPY ./loadModel.py /api/loadModel.py

RUN python /api/loadModel.py

COPY ./requirements.txt /api/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /api/requirements.txt

COPY ./app /api/app

# EXPOSE 8080

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
