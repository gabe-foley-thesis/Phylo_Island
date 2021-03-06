FROM python:3.8
COPY pi/install/requirements.txt pi/requirements.txt 
WORKDIR /pi
RUN pip install -r requirements.txt
COPY . /pi