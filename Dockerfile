FROM python:3.8-slim

WORKDIR /app
COPY . /app
RUN apt update && apt install --no-install-recommends --no-install-suggests -y git wait-for-it
RUN pip install --upgrade pip && pip install -r requirements.txt
