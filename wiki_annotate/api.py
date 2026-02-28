from wiki_annotate import config
import asyncio
import os
from fastapi import FastAPI, Query, Response, status
from fastapi.middleware.cors import CORSMiddleware
from wiki_annotate.exceptions import WikiPageAPIException, WikiAPIException, AnnotatedTextException, DiffLogicException
from wiki_annotate.wiki import WikiPageAPI
from wiki_annotate.core import Annotate
from wiki_annotate.types import APIPageData, APIAnnotate
import logging

app = FastAPI()
log = logging.getLogger(__name__)


_extra = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]
origins = ["http://localhost:3000"] + _extra
regex_origins = r"https?://.*\.wikipedia\.red"
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=regex_origins,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"https://github.com/confiq/wiki-annotate": "🧐‍"}


@app.get("/v1/page_info/")
def get_page_info(response: Response, url: str = Query(..., pattern=WikiPageAPI.DOMAIN_REGEX)):

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
def get_annotation(response: Response, url: str = Query(..., pattern=WikiPageAPI.DOMAIN_REGEX)):
    try:
        url = WikiPageAPI(url).url
        core = Annotate(url)
        cached = core.run()
        timestamp = cached.latest_revision.timestamp
        return APIAnnotate(
            text=core.get_ui_revisions(cached),
            need_refresh=core.wiki_page_annotation.need_refresh,
            last_edited=timestamp[:10] if timestamp else None,
        )
    except WikiPageAPIException as e:
        log.exception(e)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": str(e)}
    except WikiAPIException as e:
        log.exception(e)
        response.status_code = status.HTTP_502_BAD_GATEWAY
        return {"error": f"Wikipedia API error: {e}"}
    except (AnnotatedTextException, DiffLogicException) as e:
        log.exception(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": f"Annotation error: {e}"}
    except Exception as e:
        log.exception(e)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Unexpected error, please check server logs"}
