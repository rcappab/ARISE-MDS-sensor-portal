# syntax=docker/dockerfile:1
FROM python:3.11-alpine3.22

RUN echo "@testing http://dl-cdn.alpinelinux.org/alpine/edge/testing" >> /etc/apk/repositories
RUN apk add --update --no-cache py3-numpy py3-pandas@testing

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY ./sensor_portal /usr/src/sensor_portal

WORKDIR /usr/src/sensor_portal

# install dependencies
RUN apk add --update --no-cache binutils gdal postgresql-client git



ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

RUN pip install --upgrade pip 
RUN pip install --no-cache-dir -r requirements.txt
#RUN apk add --update --no-cache install -y ffmpeg
