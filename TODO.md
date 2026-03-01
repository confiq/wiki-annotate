# TODO — wiki-annotate

> Scratch pad for things to fix/ship. See CLAUDE.md for architecture context.

---

## 🛠 Dev Tooling

- [x] **`dev.sh` — one-command local dev startup**
  Start backend + frontend in parallel with a single script.
  Both processes in the same terminal (tmux panes, or just prefixed output).
  Backend: `uvicorn wiki_annotate.api:app --reload --reload-dir wiki_annotate --port 8765`
  Frontend: `cd frontend && npm start`
  Should kill both on Ctrl-C cleanly.

---

## 🐛 Must Fix

- [ ] `/v1/page_annotation/` has no try/except — any error crashes with 500 and no message
- [ ] Deleted revisions are not skipped (`# TODO: don't run on deleted revisions` in wiki_annotation.py)
- [ ] `WikiAPI.request()` has no retry on network errors
- [ ] Locking: concurrent requests for the same page can corrupt cache (diff.py TODO)
- [ ] `AnnotatedTextException.__str__` returns literal "TODO"

---

## ⏳ From PR #12 Review

- [ ] **Infinite polling** — frontend will poll forever if backend always returns `need_refresh: true`
  Add max retries cap (e.g. 20 polls ~100s) or a max-duration timeout
- [x] **Two `<Table.Body>` siblings** in `MainAnnotation` — spinner banner should live outside or inside the main body, not as a sibling table body
- [ ] `conftest.py` comment says "Python 3.14 wheels" — misleading, fix to say "not in test venv"
- [ ] No `requirements-dev.txt` — test deps are only in README, easy to drift

---

## ⚡ Performance

- [ ] `DiffLogic` is CPU-bound but runs inside async event loop — blocks everything. Fix: `run_in_executor`
- [ ] `AnnotatedText.clear_text` does a full join on every diff — may be expensive for large articles
- [ ] `jsons` deserialisation is slow — consider pydantic or msgspec

---

## ✨ Features

- [ ] No progress indication for long annotations (SSE or websocket for UX)
- [ ] `SiteAPIRevisionStructure.timestamp` is a raw string — should be datetime

---

## 🔒 Security

- [ ] No rate limiting on API endpoints — could be abused
- [ ] GitHub Dependabot flagging vulns on main — clears once PRs #5 + #6 merge

---

## 🧹 Cleanup

- [ ] `in_container()` in utils.py logs warnings at import time unnecessarily
- [ ] Add architecture diagram or flow description for new contributors

