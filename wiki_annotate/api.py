from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from wiki_annotate.wiki import WikiPageAPI
from wiki_annotate.types import APIPageData
import logging
app = FastAPI()
log = logging.getLogger(__name__)


origins = [
    "http://localhost:3000",
    "https://*.wikipedia.red/",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"https://github.com/confiq/wiki-annotate": "🤷‍"}


@app.get("/v1/page_info/")
def get_page_info(url: str = Query(..., regex=WikiPageAPI.DOMAIN_REGEX)):

    page_data = APIPageData(is_error=True)
    try:
        page_data = WikiPageAPI(url).get_page_data()
    except Exception as e:
        log.exception(e)
        page_data.add_error_msg('Unknown error, please check server logs')

    return page_data


@app.get("/v1/page_annotation/")
def get_annotation(url):
    return {'todo2'}

