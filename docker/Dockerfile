FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY djau/. .
RUN apt-get update && apt-get install -y git wait-for-it \
    libgl1 \
    libglib2.0-0 && \
    apt clean && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install -r requirements.txt
