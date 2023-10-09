FROM python:3.10

WORKDIR /diarization

COPY ./requirements.txt /diarization/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /diarization/requirements.txt

COPY ./app /diarization/app

# EXPOSE 8080

# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
