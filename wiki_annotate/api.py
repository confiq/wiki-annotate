from fastapi import FastAPI, Query
from wiki_annotate.wiki import WikiPageAPI

app = FastAPI()


@app.get("/")
def index():
    return {"https://github.com/confiq/wiki-annotate": "🤷‍"}


@app.get("/v1/page_info/")
def get_page_info(url: str = Query(..., regex=WikiPageAPI.DOMAIN_REGEX)):
    """
    "errors": {
        "is_error": false,
        "error_message": "alles gute"
    },
    "page_title": "English Language",
    "language": "Simple English",
    "wiki_language": "simple",
    "wiki_more_languages": ["en","fr","he"],
    "cached_revid": 123123,
    "refresh_needed": false
    """
    page = WikiPageAPI(url)

    return {page.get_wikipedia_url()}


@app.get("/v1/page_annotation/")
def get_annotation(url):
    return {'todo2'}

