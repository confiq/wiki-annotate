# wiki-annotate

> git annotate, but for Wikipedia — see who wrote every line and when.

Given any Wikipedia article, wiki-annotate shows per-line authorship by replaying the full revision history. Users swap `.org` → `.red` in the URL to use the hosted version.

![example](frontend/public/change_to_red.gif)

## How to use (hosted)

Navigate to any Wikipedia article and change `.org` to `.red` in the URL:

```
https://en.wikipedia.org/wiki/Git
              ↓
https://en.wikipedia.red/wiki/Git
```

## Running locally

### Quick Start

```bash
./dev.sh
```

### Manual Setup

#### Requirements

- Python 3.11+
- Node 20+

#### Backend

```bash
# First time setup
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]" --index-url https://pypi.org/simple/

# Run
uvicorn wiki_annotate.api:app --reload --reload-dir wiki_annotate --port 8765
# API available at http://localhost:8765
```

#### Tests

```bash
# First time setup (if .venv does not exist yet)
python3 -m venv .venv
source .venv/bin/activate
pip install pytest pytest-mock httpx diff-match-patch jsons fastapi --index-url https://pypi.org/simple/

# Run all tests
.venv/bin/pytest tests/ -v

# Run a specific module
.venv/bin/pytest tests/test_diff.py -v
```

> Tests use mocks for external dependencies (pywikibot, GCP) — no credentials needed.

#### Frontend

```bash
cd frontend
npm install       # first time only
npm start         # starts Vite dev server at http://localhost:3000
```

> Both must run simultaneously. Open http://localhost:3000/wiki/Git to test.

#### Environment variables

| Variable | Default | Description |
|---|---|---|
| `DB_DRIVER` | `FileSystem` | Cache backend. Set to `GCPStorage` for production |
| `CACHE_BUCKET` | — | GCS bucket name (required when `DB_DRIVER=GCPStorage`) |
| `MAX_BATCH_COUNT` | `false` | Max revision batches to fetch. `false` = fetch all |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated extra allowed CORS origins |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`) |

Copy `.env.example` to `.env` and adjust as needed.

## Architecture

```
Request (URL)
  → api.py            FastAPI endpoints
  → core.py           Annotate — orchestrates everything
  → wiki.py           pywikibot wrapper, URL normalisation (.red → .org)
  → wiki_siteapi.py   Raw MediaWiki API calls (revision batches)
  → wiki_annotation.py  Processes revisions, builds AnnotatedText
  → diff.py           diff-match-patch wrapper — diffs two revisions char-by-char
  → db/               Cache layer (FileSystem default, GCPStorage in prod)
  → types.py          Dataclasses (AnnotatedText, CachedRevision, UIRevision…)
```

Frontend: React 18 + Semantic UI React, built with Vite.

## Tech stack

- **Backend:** Python 3.13, FastAPI, pywikibot, diff-match-patch
- **Frontend:** React 18, Semantic UI React, Vite
- **Cache:** Filesystem (dev) / Google Cloud Storage (prod)
- **Deploy:** Docker, GCP (App Engine + GCS)

## Contributing

See [CLAUDE.md](CLAUDE.md) for architecture details, conventions, and the TODO list.
