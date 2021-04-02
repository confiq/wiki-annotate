FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

COPY ./ /app
WORKDIR /app

RUN pip install -e .


