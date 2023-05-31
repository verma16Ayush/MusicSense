# Use an official Python runtime as the base image
FROM ubuntu:latest

RUN mkdir /MusicSense
COPY . /MusicSense

# Install required system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libblas-dev \
        liblapack-dev \
        gfortran \
        portaudio19-dev \
        python3 \
        python3-dev \
        python3-pip \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# RUN apt -y install portaudio19-dev

# Install NumPy and SciPy
RUN pip install -r /MusicSense/requirements.txt
WORKDIR /MusicSense/
CMD ["uvicorn", "main:app"]