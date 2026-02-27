"""Shared fixtures for wiki-annotate tests.

Mocks external dependencies (google.cloud, pywikibot) that aren't installed
in the test environment, then provides reusable test fixtures.
"""
import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Mock external packages BEFORE any wiki_annotate module is imported.
# google.cloud.storage and pywikibot are required at import-time by
# config.py, wiki.py, wiki_annotation.py etc. but are not installed in dev.
# ---------------------------------------------------------------------------

_google = MagicMock()
sys.modules.setdefault("google", _google)
sys.modules.setdefault("google.cloud", _google.cloud)
sys.modules.setdefault("google.cloud.storage", _google.cloud.storage)
sys.modules.setdefault("google.cloud.exceptions", _google.cloud.exceptions)

_pywikibot = MagicMock()
sys.modules.setdefault("pywikibot", _pywikibot)

# python-dotenv and requests have no Python 3.14 wheels
_dotenv = MagicMock()
sys.modules.setdefault("dotenv", _dotenv)

_requests = MagicMock()
sys.modules.setdefault("requests", _requests)

# ---------------------------------------------------------------------------
# Now safe to import from wiki_annotate
# ---------------------------------------------------------------------------

import pytest
from wiki_annotate.types import (
    AnnotationCharData,
    AnnotatedText,
    SiteAPIRevisionStructure,
    CachedRevision,
)


@pytest.fixture
def make_char_data():
    """Factory fixture to create AnnotationCharData."""
    def _make(revid=1, user="TestUser"):
        return AnnotationCharData(revid=revid, user=user)
    return _make


@pytest.fixture
def make_annotated_text(make_char_data):
    """Factory fixture to create AnnotatedText from a string and optional char data."""
    def _make(text="hello", revid=1, user="TestUser"):
        cd = make_char_data(revid=revid, user=user)
        return AnnotatedText(tuple((ch, cd) for ch in text))
    return _make


@pytest.fixture
def sample_revision_kwargs():
    """A dict matching the MediaWiki API revision format."""
    return {
        "revid": 100,
        "user": "Alice",
        "userid": 42,
        "timestamp": "2024-01-15T10:00:00Z",
        "comment": "Initial revision",
        "slots": {"main": {"content": "Hello world"}},
    }


@pytest.fixture
def sample_revision(sample_revision_kwargs):
    return SiteAPIRevisionStructure(**sample_revision_kwargs)


@pytest.fixture
def sample_cached_revision(make_annotated_text, sample_revision):
    return CachedRevision(
        annotated_text=make_annotated_text("Hello world", revid=100, user="Alice"),
        latest_revision=sample_revision,
    )
