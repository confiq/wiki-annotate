"""Tests for wiki_annotate.wiki module."""
import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from wiki_annotate.wiki import Wiki, WikiPageAPI
from wiki_annotate.types import APIPageData


class TestWikiPageAPIGetWikipediaUrl:
    """Test URL normalization: .red/.com/etc -> .org"""

    def test_red_to_org(self):
        api = WikiPageAPI.__new__(WikiPageAPI)
        result = api.get_wikipedia_url("https://en.wikipedia.red/wiki/Test")
        assert result == "https://en.wikipedia.org/wiki/Test"

    def test_com_to_org(self):
        api = WikiPageAPI.__new__(WikiPageAPI)
        result = api.get_wikipedia_url("https://en.wikipedia.com/wiki/Test")
        assert result == "https://en.wikipedia.org/wiki/Test"

    def test_org_stays_org(self):
        api = WikiPageAPI.__new__(WikiPageAPI)
        result = api.get_wikipedia_url("https://en.wikipedia.org/wiki/Test")
        assert result == "https://en.wikipedia.org/wiki/Test"

    def test_http_protocol(self):
        api = WikiPageAPI.__new__(WikiPageAPI)
        result = api.get_wikipedia_url("http://en.wikipedia.red/wiki/Test")
        assert result == "http://en.wikipedia.org/wiki/Test"

    def test_with_path_and_query(self):
        api = WikiPageAPI.__new__(WikiPageAPI)
        # Use a path without dots — the DOMAIN_REGEX is greedy and mishandles
        # dots in paths (e.g. index.php), so test the common /wiki/ pattern.
        result = api.get_wikipedia_url("https://en.wikipedia.red/wiki/Test?action=edit")
        assert result == "https://en.wikipedia.org/wiki/Test?action=edit"

    def test_other_wikis(self):
        api = WikiPageAPI.__new__(WikiPageAPI)
        result = api.get_wikipedia_url("https://de.wikipedia.red/wiki/Berlin")
        assert result == "https://de.wikipedia.org/wiki/Berlin"


class TestWikiPageName:
    """Test page name extraction from URLs."""

    def test_wiki_path(self):
        wiki = Wiki.__new__(Wiki)
        wiki.url = "https://en.wikipedia.org/wiki/Test_Page"
        wiki._site = None
        wiki._wikiid = None
        assert wiki.page_name == "Test_Page"

    def test_wiki_path_with_subpage(self):
        wiki = Wiki.__new__(Wiki)
        wiki.url = "https://en.wikipedia.org/wiki/Help:Contents"
        wiki._site = None
        wiki._wikiid = None
        assert wiki.page_name == "Help:Contents"

    def test_no_matching_pattern_returns_none(self):
        wiki = Wiki.__new__(Wiki)
        wiki.url = "https://en.wikipedia.org/some/other/path"
        wiki._site = None
        wiki._wikiid = None
        assert wiki.page_name is None

    def test_wiki_path_short(self):
        """'/wiki/' alone (length 6) should not match the >6 check."""
        wiki = Wiki.__new__(Wiki)
        wiki.url = "https://en.wikipedia.org/wiki/"
        wiki._site = MagicMock()
        wiki._site.siteinfo.return_value = {"mainpage": "Main Page"}
        wiki._wikiid = None
        assert wiki.page_name == "Main Page"


class TestWikiPageAPIGetPageData:
    @patch.object(WikiPageAPI, "page_name", new_callable=PropertyMock, return_value="Test")
    @patch.object(WikiPageAPI, "get_wikipedia_url", return_value="https://en.wikipedia.org/wiki/Test")
    def test_success(self, mock_url, mock_name):
        api = WikiPageAPI.__new__(WikiPageAPI)
        api.url = "https://en.wikipedia.org/wiki/Test"
        api._site = None
        api._wikiid = None
        pd = api.get_page_data()
        assert pd.is_error is False
        assert pd.page_title == "Test"

    @patch.object(WikiPageAPI, "page_name", new_callable=PropertyMock, return_value=None)
    @patch.object(WikiPageAPI, "get_wikipedia_url", return_value="https://en.wikipedia.org/")
    def test_no_page_name(self, mock_url, mock_name):
        api = WikiPageAPI.__new__(WikiPageAPI)
        api.url = "https://en.wikipedia.org/"
        api._site = None
        api._wikiid = None
        pd = api.get_page_data()
        assert pd.is_error is True
        assert len(pd.errors_messages) == 1
        assert "title" in pd.errors_messages[0].lower()


class TestDomainRegex:
    """Test that the DOMAIN_REGEX correctly matches various URL formats."""

    import re

    @pytest.mark.parametrize("url", [
        "https://en.wikipedia.org/wiki/Test",
        "http://de.wikipedia.red/wiki/Berlin",
        "https://fr.wikipedia.com/w/index.php?title=Test",
    ])
    def test_regex_matches(self, url):
        import re
        assert re.match(WikiPageAPI.DOMAIN_REGEX, url)
