from wiki_annotate import config
import asyncio
import os
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, Query, Response, status, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from wiki_annotate.exceptions import WikiPageAPIException, WikiAPIException, AnnotatedTextException, DiffLogicException
from wiki_annotate.wiki import WikiPageAPI
from wiki_annotate.core import Annotate
from wiki_annotate.types import APIPageData, APIAnnotate, RevisionData
import logging

log = logging.getLogger(__name__)

def _get_max_workers(default: int = 4) -> int:
    """Safely parse ANNOTATE_WORKERS from the environment.

    Falls back to `default` on missing/invalid values and enforces a minimum of 1.
    """
    raw = os.getenv("ANNOTATE_WORKERS")
    if not raw:
        return default
    try:
        workers = int(raw)
        if workers < 1:
            raise ValueError("must be >= 1")
        return workers
    except (TypeError, ValueError) as exc:
        log.warning("Invalid ANNOTATE_WORKERS value %r (%s); falling back to default %d", raw, exc, default)
        return default


# Dedicated thread pool for CPU-bound / blocking work (DiffLogic, pywikibot, file I/O).
# Using a named pool makes it visible in thread dumps and profilers.
_executor = ThreadPoolExecutor(
    max_workers=_get_max_workers(),
    thread_name_prefix="wiki-annotate",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    _executor.shutdown(wait=False)


app = FastAPI(lifespan=lifespan)

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
async def get_page_info(response: Response, url: str = Query(..., pattern=WikiPageAPI.DOMAIN_REGEX)):
    loop = asyncio.get_running_loop()
    page_data = APIPageData(is_error=True)
    try:
        page_data = await loop.run_in_executor(_executor, lambda: WikiPageAPI(url).get_page_data())
    except WikiPageAPIException as e:
        log.exception(e)
        page_data.add_error_msg(f'Error: {e}')
        response.status_code = status.HTTP_400_BAD_REQUEST
    except Exception as e:
        log.exception(e)
        page_data.add_error_msg('Unknown error, please check server logs')
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return page_data


def _refresh_in_background(url: str):
    try:
        core = Annotate(url)
        core.run()
    except Exception as e:
        log.exception(f"Background refresh failed for {url}: {e}")


@app.get("/v1/page_annotation/")
async def get_annotation(response: Response, background_tasks: BackgroundTasks, url: str = Query(..., pattern=WikiPageAPI.DOMAIN_REGEX)):
    loop = asyncio.get_running_loop()
    try:
        url = WikiPageAPI(url).url
        core = Annotate(url)

        # Blocking: hits Wikipedia API + local cache — offload to thread pool
        latest_revision = await loop.run_in_executor(_executor, lambda: core.wiki.get_page().latest_revision)
        cached = await loop.run_in_executor(_executor, lambda: core.local_db.get_page(RevisionData(latest_revision).id))

        if cached:
            # Return stale cache immediately, refresh in background if needed
            cached_revid = cached.latest_revision.revid
            latest_revid = RevisionData(latest_revision).id
            is_stale = cached.need_refresh or (
                cached_revid is not None and
                latest_revid is not None and
                cached_revid < latest_revid
            )
            if is_stale:
                background_tasks.add_task(_refresh_in_background, url)
            timestamp = cached.latest_revision.timestamp
            # CPU-bound: building UI revision tuples — offload to thread pool
            ui_revisions = await loop.run_in_executor(_executor, lambda: core.get_ui_revisions(cached))
            return APIAnnotate(
                text=ui_revisions,
                need_refresh=True if is_stale else core.wiki_page_annotation.need_refresh,
                last_edited=timestamp[:10] if timestamp else None,
            )

        # No cache at all — block on first annotation run (DiffLogic-heavy)
        cached = await loop.run_in_executor(_executor, core.run)
        timestamp = cached.latest_revision.timestamp
        ui_revisions = await loop.run_in_executor(_executor, lambda: core.get_ui_revisions(cached))
        return APIAnnotate(
            text=ui_revisions,
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
