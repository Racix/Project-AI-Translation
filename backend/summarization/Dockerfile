FROM python:3.10

WORKDIR /summarize

COPY ./requirements.txt /summarize/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /summarize/requirements.txt

COPY ./app /summarize/app