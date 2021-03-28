# wiki-annotate

same as git annotate but for wikipedia markup language

## How to use

TODO

## development

## Prerequisites

* wiki-annotate was tested on python 3.9, but it should work on python 3.8<

* for frontend magic, node10 and npm

## Quickstart

### backend

Use [venv](https://pypi.org/project/virtualenv/) to create dev env

1. create venv, with python3 `python3 -m pip .venv`. This will create a folder `.venv` and to activate it, `source .venv/bin/activate`
2. `pip install -e .` will install package `wiki-annotate`
3. `uvicorn wiki_annotate.api:app --reload` will run fastAPI backend. 

### frontend

Frontend is done in [react-sematic-ui](https://react.semantic-ui.com/)! go to `frontend` directory and run `npm init` and after that `npm start` and follow the instructions.
