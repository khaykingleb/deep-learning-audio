FROM nvidia/cuda:11.7.1-devel-ubuntu22.04

WORKDIR /Deep-Learning-for-Audio

# Prerequested
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get -y install git \
                       sudo \
                       curl \
                       wget

# System requirements
RUN apt-get -y install libsndfile1

# Set normal TZ for logs
RUN ln -sf /usr/share/zoneinfo/Europe/Moscow /etc/localtime

# Python dependencies
RUN apt-get -y install python3 \
                       python-is-python3 \
                       python3-pip \
    && pip install poetry

# Copy only requirements to cache in Docker layer
COPY pyproject.toml poetry.lock ./

# Project initialization
RUN poetry config virtualenvs.create false && poetry install --without test,research

COPY . .
