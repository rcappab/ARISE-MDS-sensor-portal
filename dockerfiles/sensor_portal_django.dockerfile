# syntax=docker/dockerfile:1
FROM python:3.10
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./sensor_portal /usr/src/sensor_portal

WORKDIR /usr/src/sensor_portal

# install dependencies
RUN apt-get update && apt-get install -y binutils libproj-dev gdal-bin 
RUN apt-get install postgresql-client -y


ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt
RUN apt-get install -y ffmpeg
