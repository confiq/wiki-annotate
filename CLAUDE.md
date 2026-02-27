# CLAUDE.md — wiki-annotate

## What this is

"git annotate for Wikipedia" — given any Wikipedia article URL, show every line annotated with who wrote it and in which revision. Users swap `.org` → `.red` in the URL to use it.

## Running locally

```bash
source .venv/bin/activate   # Python 3.13 venv
uvicorn wiki_annotate.api:app --reload --reload-dir wiki_annotate --port 8765
```

Frontend: `cd frontend && npm install && npm start` (React on :3000)

## Architecture

```
Request (URL) 
  → api.py          FastAPI endpoints
  → core.py         Annotate — orchestrates everything
  → wiki.py         pywikibot wrapper, URL normalisation (.red → .org)
  → wiki_siteapi.py Raw MediaWiki API calls (revision batches)
  → wiki_annotation.py  Processes revisions, builds AnnotatedText
  → diff.py         diff-match-patch wrapper — diffs two revisions char-by-char
  → db/             Cache layer (FileSystem default, GCPStorage in prod)
  → types.py        All dataclasses (AnnotatedText, CachedRevision, UIRevision…)
```

### Key types
- `AnnotatedText` — tuple of `(char, AnnotationCharData)` for every character
- `AnnotationCharData` — just `revid` + `user` per char
- `CachedRevision` — serialised to JSON on disk/GCS, keyed by `wikiid/page/revid.json`
- `UIRevision` — line-grouped output for the frontend: `{users: set, annotated_text: [...]}`

### Cache
- Default: filesystem at `data-page/v1/<wikiid>/<page>/<revid>.json`
- Prod: GCP Storage — set `DB_DRIVER=GCPStorage` + `CACHE_BUCKET=<name>`
- Serialisation via `jsons` lib (slow on deserialise, candidate for replacement)

## Active branch

`chore/modernize-py313-deps` — modernisation work in progress:
- Migrated `setup.py` → `pyproject.toml` (Python ≥3.11)
- All deps upgraded (FastAPI 0.133, uvicorn 0.41, pywikibot 11, google-cloud-storage 3.9)
- Fixed `Query(regex=)` → `Query(pattern=)` (Pydantic v2)
- Fixed DOMAIN_REGEX to remove lookbehind (Pydantic v2 uses Rust regex, no lookarounds)

## Known TODOs (prioritised)

### Must fix
- [ ] `/v1/page_annotation/` has no try/except — any error crashes with 500 and no message
- [ ] Deleted revisions are not skipped (`# TODO: don't run on deleted revisions` in wiki_annotation.py)
- [ ] `WikiAPI.request()` has no retry on network errors
- [ ] Locking: concurrent requests for the same page can corrupt cache (diff.py TODO)

### Performance
- [ ] `DiffLogic` is CPU-bound but runs inside async event loop — blocks everything. Fix: `run_in_executor`
- [ ] `AnnotatedText.clear_text` does a full zip+join on every diff — may be expensive for large articles
- [ ] `jsons` deserialisation is slow — consider pydantic or msgspec

### Features
- [ ] `need_refresh=True` is set when a batch is incomplete (long articles hit time limit) but the frontend has no way to continue / poll for more
- [ ] No progress indication for long annotations (SSE or websocket would help UX)
- [ ] `SiteAPIRevisionStructure.timestamp` is a raw string — should be datetime

### Cleanup
- [ ] `AnnotatedTextException.__str__` returns literal "TODO"
- [ ] `LOG_DEBUG_LEVEL` hardcoded to DEBUG in config.py — should be INFO in prod
- [ ] `in_container()` in utils.py logs warnings at import time unnecessarily
- [ ] `setup.py.old` can be deleted
- [ ] `requirements.txt` is now stale (superseded by pyproject.toml) — delete or note it

## Deployment

- Dockerfile: `python:3.13-slim`, installs package, runs uvicorn on `$PORT` (default 8080)
- `infra/` has Pulumi config for GCP (App Engine + GCS bucket) — may be stale

## Conventions

- All new endpoints need try/except with proper HTTP status codes (see `/v1/page_info/` as the good example)
- Don't use `pywikibot` outside of `wiki.py` — keep it contained
- Cache reads/writes go through `db/data.py DataInterface` only, never directly to FileSystem/GCS
