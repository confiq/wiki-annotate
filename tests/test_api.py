"""Tests for wiki_annotate.api module."""
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from wiki_annotate.api import app
from wiki_annotate.exceptions import (
    WikiPageAPIException,
    WikiAPIException,
    AnnotatedTextException,
    DiffLogicException,
)
from wiki_annotate.types import APIPageData, AnnotatedText, AnnotationCharData


@pytest.fixture
def client():
    return TestClient(app)


class TestIndexEndpoint:
    def test_index(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        data = resp.json()
        assert "https://github.com/confiq/wiki-annotate" in data


class TestPageInfoEndpoint:
    @patch("wiki_annotate.api.WikiPageAPI")
    def test_success(self, MockWikiPageAPI, client):
        mock_instance = MagicMock()
        mock_instance.get_page_data.return_value = APIPageData(
            is_error=False, page_title="Test"
        )
        MockWikiPageAPI.return_value = mock_instance

        resp = client.get("/v1/page_info/", params={"url": "https://en.wikipedia.org/wiki/Test"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_error"] is False
        assert data["page_title"] == "Test"

    @patch("wiki_annotate.api.WikiPageAPI")
    def test_wiki_page_api_exception(self, MockWikiPageAPI, client):
        MockWikiPageAPI.side_effect = WikiPageAPIException("bad page")
        resp = client.get("/v1/page_info/", params={"url": "https://en.wikipedia.org/wiki/Test"})
        assert resp.status_code == 400

    @patch("wiki_annotate.api.WikiPageAPI")
    def test_generic_exception(self, MockWikiPageAPI, client):
        MockWikiPageAPI.side_effect = RuntimeError("unexpected")
        resp = client.get("/v1/page_info/", params={"url": "https://en.wikipedia.org/wiki/Test"})
        assert resp.status_code == 500

    def test_missing_url_param(self, client):
        resp = client.get("/v1/page_info/")
        assert resp.status_code == 422  # Validation error


class TestPageAnnotationEndpoint:
    @patch("wiki_annotate.api.Annotate")
    @patch("wiki_annotate.api.WikiPageAPI")
    def test_success(self, MockWikiPageAPI, MockAnnotate, client):
        mock_wiki = MagicMock()
        mock_wiki.url = "https://en.wikipedia.org/wiki/Test"
        MockWikiPageAPI.return_value = mock_wiki

        cd = AnnotationCharData(revid=1, user="Alice")
        mock_ui_revision = MagicMock()
        mock_ui_revision.users = {"Alice"}
        mock_ui_revision.annotated_text = [("hello", cd)]

        mock_cached = MagicMock()
        mock_cached.latest_revision.timestamp = "2024-03-15T10:00:00Z"

        mock_core = MagicMock()
        mock_core.run.return_value = mock_cached
        mock_core.get_ui_revisions.return_value = (mock_ui_revision,)
        mock_core.wiki_page_annotation.need_refresh = False
        MockAnnotate.return_value = mock_core

        resp = client.get("/v1/page_annotation/", params={"url": "https://en.wikipedia.org/wiki/Test"})
        assert resp.status_code == 200

    @patch("wiki_annotate.api.WikiPageAPI")
    def test_wiki_page_api_exception(self, MockWikiPageAPI, client):
        MockWikiPageAPI.side_effect = WikiPageAPIException("bad page")
        resp = client.get("/v1/page_annotation/", params={"url": "https://en.wikipedia.org/wiki/Test"})
        assert resp.status_code == 400
        assert "error" in resp.json()

    @patch("wiki_annotate.api.Annotate")
    @patch("wiki_annotate.api.WikiPageAPI")
    def test_wiki_api_exception(self, MockWikiPageAPI, MockAnnotate, client):
        mock_wiki = MagicMock()
        mock_wiki.url = "https://en.wikipedia.org/wiki/Test"
        MockWikiPageAPI.return_value = mock_wiki
        MockAnnotate.side_effect = WikiAPIException("upstream error")

        resp = client.get("/v1/page_annotation/", params={"url": "https://en.wikipedia.org/wiki/Test"})
        assert resp.status_code == 502
        assert "Wikipedia API error" in resp.json()["error"]

    @patch("wiki_annotate.api.Annotate")
    @patch("wiki_annotate.api.WikiPageAPI")
    def test_diff_logic_exception(self, MockWikiPageAPI, MockAnnotate, client):
        mock_wiki = MagicMock()
        mock_wiki.url = "https://en.wikipedia.org/wiki/Test"
        MockWikiPageAPI.return_value = mock_wiki

        # DiffLogicException needs a diff object with pointer, previous_annotation, new_revision_text
        mock_diff_obj = MagicMock()
        mock_diff_obj.pointer = 0
        mock_diff_obj.previous_annotation = "test"
        mock_diff_obj.new_revision_text = "test"
        MockAnnotate.side_effect = DiffLogicException("diff error", mock_diff_obj)

        resp = client.get("/v1/page_annotation/", params={"url": "https://en.wikipedia.org/wiki/Test"})
        assert resp.status_code == 500
        assert "Annotation error" in resp.json()["error"]

    @patch("wiki_annotate.api.Annotate")
    @patch("wiki_annotate.api.WikiPageAPI")
    def test_generic_exception(self, MockWikiPageAPI, MockAnnotate, client):
        mock_wiki = MagicMock()
        mock_wiki.url = "https://en.wikipedia.org/wiki/Test"
        MockWikiPageAPI.return_value = mock_wiki
        MockAnnotate.side_effect = RuntimeError("unexpected")

        resp = client.get("/v1/page_annotation/", params={"url": "https://en.wikipedia.org/wiki/Test"})
        assert resp.status_code == 500
        assert "Unexpected error" in resp.json()["error"]

    def test_missing_url_param(self, client):
        resp = client.get("/v1/page_annotation/")
        assert resp.status_code == 422
