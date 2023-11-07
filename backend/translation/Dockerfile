FROM python:3.10

WORKDIR /translation

#RUN pip install --no-cache-dir --upgrade argostranslate==1.9.1


COPY ./requirements.txt /translation/requirements.txt


RUN pip install --no-cache-dir --upgrade -r /translation/requirements.txt

#COPY ./load_model.py /translation/load_model.py
#RUN python /translation/load_model.py

COPY ./app /translation/app
