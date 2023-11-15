FROM python:3.10

WORKDIR /translation

COPY ./requirements.txt /translation/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /translation/requirements.txt

COPY ./load_model.py /translation/load_model.py

RUN python /translation/load_model.py

COPY ./app /translation/app
