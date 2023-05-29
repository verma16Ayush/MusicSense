FROM python:3.10-alpine3.18

COPY . /MusicSense

RUN apk --no-cache add musl-dev linux-headers g++
RUN pip install -r /MusicSense/requirements.txt

