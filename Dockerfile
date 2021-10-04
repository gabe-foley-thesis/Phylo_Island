FROM python:3.6
COPY pi/install/requirements.txt pi/requirements.txt 
WORKDIR /pi
RUN pip install -r requirements.txt
COPY . /pi