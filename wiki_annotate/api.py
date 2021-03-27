from fastapi import FastAPI, Query
from wiki_annotate.wiki import WikiPageAPI
from wiki_annotate.types import APIPageData
import logging
app = FastAPI()
log = logging.getLogger(__name__)

@app.get("/")
def index():
    return {"https://github.com/confiq/wiki-annotate": "🤷‍"}


@app.get("/v1/page_info/")
def get_page_info(url: str = Query(..., regex=WikiPageAPI.DOMAIN_REGEX)):

    page_data = APIPageData(is_error=True)

    try:
        page = WikiPageAPI(url)
        # page_data = page.get_api_data()
    except Exception as e:
        log.exception(e)
        page_data.add_error_msg('Unknown error, please check server logs')

    return page_data


@app.get("/v1/page_annotation/")
def get_annotation(url):
    return {'todo2'}

