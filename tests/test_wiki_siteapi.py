"""Tests for wiki_annotate.wiki_siteapi module."""
import json
import time
import pytest
from unittest.mock import MagicMock, patch

from wiki_annotate.wiki_siteapi import WikiAPI
from wiki_annotate.types import SiteAPIRevisions
from wiki_annotate.exceptions import WikiAPIException


class TestWikiAPIShouldContinue:
    def _make_api(self):
        core = MagicMock()
        api = WikiAPI(core)
        api.reset_timer()
        return api

    @patch("wiki_annotate.wiki_siteapi.config")
    def test_default_continues(self, mock_config):
        mock_config.MAX_BATCH_COUNT = False
        api = self._make_api()
        assert api.should_continue() is True

    @patch("wiki_annotate.wiki_siteapi.config")
    def test_max_batch_count_stops(self, mock_config):
        mock_config.MAX_BATCH_COUNT = 2
        api = self._make_api()
        api.COUNT = 2
        assert api.should_continue() is False

    @patch("wiki_annotate.wiki_siteapi.config")
    def test_max_batch_count_allows_before_limit(self, mock_config):
        mock_config.MAX_BATCH_COUNT = 5
        api = self._make_api()
        api.COUNT = 3
        assert api.should_continue() is True

    @patch("wiki_annotate.wiki_siteapi.config")
    def test_negative_batch_count_continues(self, mock_config):
        mock_config.MAX_BATCH_COUNT = -1
        api = self._make_api()
        api.COUNT = 1000
        assert api.should_continue() is True

    @patch("wiki_annotate.wiki_siteapi.config")
    def test_cpu_time_exhausted(self, mock_config):
        mock_config.MAX_BATCH_COUNT = False
        api = self._make_api()
        # Simulate elapsed CPU time
        api.cpu_timer = time.process_time() - (WikiAPI.TOTAL_CPU_TIME + 1)
        assert api.should_continue() is False

    @patch("wiki_annotate.wiki_siteapi.config")
    def test_wall_time_exhausted(self, mock_config):
        mock_config.MAX_BATCH_COUNT = False
        api = self._make_api()
        # Simulate elapsed wall time
        api.total_time = time.time() - (WikiAPI.TOTAL_TIME + 1)
        assert api.should_continue() is False


class TestWikiAPIResetTimer:
    def test_reset_timer(self):
        core = MagicMock()
        api = WikiAPI(core)
        api.reset_timer()
        assert api.cpu_timer > 0
        assert api.total_time > 0


class TestWikiAPIRequest:
    @patch("wiki_annotate.wiki_siteapi.requests")
    def test_request_calls_get(self, mock_requests):
        mock_response = MagicMock()
        mock_response.json.return_value = {"query": {}}
        mock_requests.get.return_value = mock_response

        core = MagicMock()
        api = WikiAPI(core)
        # Set a fake api_url
        api.__dict__["api_url"] = "https://en.wikipedia.org/w/api.php"

        result = api.request({"action": "query"})
        mock_requests.get.assert_called_once_with(
            "https://en.wikipedia.org/w/api.php",
            {"action": "query"},
            headers=WikiAPI.HEADERS,
        )
        assert result == {"query": {}}


class TestWikiAPILoadRevisions:
    @patch("wiki_annotate.wiki_siteapi.requests")
    @patch("wiki_annotate.wiki_siteapi.config")
    def test_single_complete_batch(self, mock_config, mock_requests):
        mock_config.MAX_BATCH_COUNT = False
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "batchcomplete": True,
            "query": {"pages": [{"revisions": [
                {"revid": 1, "user": "A", "userid": 1, "timestamp": "t",
                 "comment": "", "slots": {"main": {"content": "hello"}}},
            ]}]},
        }
        mock_requests.get.return_value = mock_response

        core = MagicMock()
        core.wiki.get_page.return_value.title.return_value = "Test"
        core.wiki.site.code = "en"
        core.wiki.site.family.protocol.return_value = "https"
        core.wiki.site.family.hostname.return_value = "en.wikipedia.org"
        core.wiki.site.family.apipath.return_value = "/w/api.php"

        api = WikiAPI(core)
        batches = list(api.load_revisions())
        assert len(batches) == 1
        assert batches[0].batchcomplete is True
        assert len(batches[0].revisions) == 1

    @patch("wiki_annotate.wiki_siteapi.requests")
    @patch("wiki_annotate.wiki_siteapi.config")
    def test_raises_on_missing_batch_status(self, mock_config, mock_requests):
        """If no batchcomplete and no continue, should raise WikiAPIException."""
        mock_config.MAX_BATCH_COUNT = False
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "query": {"pages": [{"revisions": []}]},
        }
        mock_requests.get.return_value = mock_response

        core = MagicMock()
        core.wiki.get_page.return_value.title.return_value = "Test"
        core.wiki.site.code = "en"
        core.wiki.site.family.protocol.return_value = "https"
        core.wiki.site.family.hostname.return_value = "en.wikipedia.org"
        core.wiki.site.family.apipath.return_value = "/w/api.php"

        api = WikiAPI(core)
        with pytest.raises(WikiAPIException):
            list(api.load_revisions())
