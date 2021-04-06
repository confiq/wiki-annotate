FROM python:3.8-slim
WORKDIR /app
COPY ./ /app
RUN pip install -e .

ARG PORT=8080
ENV PORT=$PORT

CMD exec uvicorn wiki_annotate.api:app --port $PORT --host 0.0.0.0
