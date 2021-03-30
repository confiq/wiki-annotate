from wiki_annotate import config
from fastapi import FastAPI, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from wiki_annotate.exceptions import WikiPageAPIException
from wiki_annotate.wiki import WikiPageAPI
from wiki_annotate.core import AnnotateAPI
from wiki_annotate.types import APIPageData, APIAnnotate
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
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"https://github.com/confiq/wiki-annotate": "🧐‍"}


@app.get("/v1/page_info/")
def get_page_info(response: Response, url: str = Query(..., regex=WikiPageAPI.DOMAIN_REGEX)):

    page_data = APIPageData(is_error=True)
    try:
        page_data = WikiPageAPI(url).get_page_data()
    except WikiPageAPIException as e:
        log.exception(e)
        page_data.add_error_msg(f'Error: {e}')
        response.status_code = status.HTTP_400_BAD_REQUEST
    except Exception as e:
        log.exception(e)
        page_data.add_error_msg('Unknown error, please check server logs')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return page_data


@app.get("/v1/page_annotation/")
def get_annotation(url: str = Query(..., regex=WikiPageAPI.DOMAIN_REGEX)):
    url = WikiPageAPI(url).url
    text = AnnotateAPI(url).get_ui_revisions()
    return APIAnnotate(text=text)
