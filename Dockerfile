FROM python:3.13-slim
WORKDIR /app
COPY ./ /app
RUN pip install --no-cache-dir .

ARG PORT=8080
ENV PORT=$PORT

CMD exec uvicorn wiki_annotate.api:app --port $PORT --host 0.0.0.0
