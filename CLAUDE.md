# CLAUDE.md — wiki-annotate

## What this is

"git annotate for Wikipedia" — given any Wikipedia article URL, show every line annotated with who wrote it and in which revision. Users swap `.org` → `.red` in the URL to use it.

## Running locally

### Backend
```bash
# First time only:
python3.13 -m venv .venv

source .venv/bin/activate
pip install -e ".[dev]" --index-url https://pypi.org/simple/
uvicorn wiki_annotate.api:app --reload --reload-dir wiki_annotate --port 8765
# API available at http://localhost:8765
```

### Frontend
```bash
cd frontend
npm install       # first time only
npm start         # starts Vite dev server at http://localhost:3000
```

> Both must be running at the same time. Backend on :8765, frontend on :3000.
> The frontend dev config (`.env.development`) already points to localhost:8765.

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

## Recent modernisation (2026-02)

- Migrated `setup.py` → `pyproject.toml` (Python ≥3.11)
- All deps upgraded (FastAPI 0.133, uvicorn 0.41, pywikibot 11, google-cloud-storage 3.9)
- Fixed `Query(regex=)` → `Query(pattern=)` (Pydantic v2)
- Fixed DOMAIN_REGEX to remove lookbehind (Pydantic v2 uses Rust regex, no lookarounds)
- Frontend migrated from CRA → Vite 7, React 17 → 18

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

### Docs
- [x] README is outdated — references python 3.9, `npm init`, old setup.py workflow
- [x] README rewritten with quickstart, env vars, architecture, tech stack
- [ ] Add architecture diagram or at least a flow description for new contributors

### Security
- [x] `npm audit fix` run — 0 vulnerabilities
- [ ] GitHub Dependabot flagging 84 vulns on main — will clear once PRs #5 + #6 merge
- [x] CORS origins moved to `CORS_ORIGINS` env var
- [ ] No rate limiting on API endpoints — could be abused

### Cleanup
- [ ] `AnnotatedTextException.__str__` returns literal "TODO"
- [x] `LOG_LEVEL` now reads from env var (default INFO)
- [ ] `in_container()` in utils.py logs warnings at import time unnecessarily
- [x] `setup.py.old` deleted
- [x] `requirements.txt` deleted
- [x] Wikipedia User-Agent 403 fix applied

## Deployment

- Dockerfile: `python:3.13-slim`, installs package, runs uvicorn on `$PORT` (default 8080)
- `infra/` has Pulumi config for GCP (App Engine + GCS bucket) — may be stale

## Conventions

- All new endpoints need try/except with proper HTTP status codes (see `/v1/page_info/` as the good example)
- Don't use `pywikibot` outside of `wiki.py` — keep it contained
- Cache reads/writes go through `db/data.py DataInterface` only, never directly to FileSystem/GCS
- **`FileSystem` and `GCPStorage` both implement `get_page_data` and `save_page_data` independently** — any behavioural change (fallback logic, error handling, serialisation) must be applied to both. There is no shared base implementation.
