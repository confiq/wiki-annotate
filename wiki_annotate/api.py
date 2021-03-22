from typing import Optional

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def index():
    return {"https://github.com/confiq/wiki-annotate"}


@app.get("/v1/page_info/")
def get_page_info(url):
    return {'todo2'}

@app.get("/v1/page_annotation/")
def get_annotation(url):
    return {'todo2'}
