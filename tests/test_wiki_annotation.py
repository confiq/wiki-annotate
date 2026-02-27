"""Tests for wiki_annotate.wiki_annotation module."""
import dataclasses
import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from wiki_annotate.wiki_annotation import WikiPageAnnotation
from wiki_annotate.types import (
    AnnotationCharData,
    AnnotatedText,
    CachedRevision,
    SiteAPIRevisionStructure,
    SiteAPIRevisions,
    UIRevision,
)
from wiki_annotate.diff import DiffLogic


def _make_revision_dict(revid, user, content, **kwargs):
    """Helper to build a dict in MediaWiki API revision format."""
    return {
        "revid": revid,
        "user": user,
        "userid": 1,
        "timestamp": "2024-01-01T00:00:00Z",
        "comment": "",
        "slots": {"main": {"content": content}},
        **kwargs,
    }


def _make_batch(revisions, batchcomplete=True):
    """Create a SiteAPIRevisions with the given revision dicts."""
    data = {
        "query": {"pages": [{"revisions": revisions}]},
    }
    if batchcomplete:
        data["batchcomplete"] = True
    return SiteAPIRevisions(data)


class TestGetAnnotation:
    def test_single_revision(self):
        """First revision should initialize text with DiffLogic.init_text."""
        core = MagicMock()
        batch = _make_batch([
            _make_revision_dict(1, "Alice", "hello"),
        ])
        core.wiki_api.load_revisions.return_value = iter([batch])

        wpa = WikiPageAnnotation(core)
        text, revision = wpa.get_annotation()

        assert text.clear_text == "hello"
        assert revision.user == "Alice"
        assert revision.revid == 1
        # All chars should be attributed to Alice
        for _, cd in text:
            assert cd.user == "Alice"

    def test_two_revisions(self):
        """Second revision should run DiffLogic to produce combined annotation."""
        core = MagicMock()
        batch = _make_batch([
            _make_revision_dict(1, "Alice", "hello"),
            _make_revision_dict(2, "Bob", "hello world"),
        ])
        core.wiki_api.load_revisions.return_value = iter([batch])

        wpa = WikiPageAnnotation(core)
        text, revision = wpa.get_annotation()

        assert text.clear_text == "hello world"
        assert revision.revid == 2
        # "hello" chars from Alice
        for i in range(5):
            assert text[i][1].user == "Alice"
        # " world" chars from Bob
        for i in range(5, 11):
            assert text[i][1].user == "Bob"

    def test_three_revisions(self):
        """Three revisions chain correctly."""
        core = MagicMock()
        batch = _make_batch([
            _make_revision_dict(1, "Alice", "a"),
            _make_revision_dict(2, "Bob", "ab"),
            _make_revision_dict(3, "Charlie", "abc"),
        ])
        core.wiki_api.load_revisions.return_value = iter([batch])

        wpa = WikiPageAnnotation(core)
        text, revision = wpa.get_annotation()

        assert text.clear_text == "abc"
        assert text[0][1].user == "Alice"
        assert text[1][1].user == "Bob"
        assert text[2][1].user == "Charlie"

    def test_with_cached_revision(self):
        """When cached revision provided, should continue from cache."""
        core = MagicMock()

        # Simulate cache: text="ab", latest revision id=2
        cd_alice = AnnotationCharData(revid=1, user="Alice")
        cd_bob = AnnotationCharData(revid=2, user="Bob")
        cached_text = AnnotatedText((("a", cd_alice), ("b", cd_bob)))
        cached_rev = SiteAPIRevisionStructure(
            content="ab", revid=2, user="Bob", userid=1,
            timestamp="t", comment="c",
        )
        cached = CachedRevision(annotated_text=cached_text, latest_revision=cached_rev)

        # New batch starts from revid 2 (the cached one), then has revid 3
        batch = _make_batch([
            _make_revision_dict(2, "Bob", "ab"),  # this is the cached starting point, will be skipped
            _make_revision_dict(3, "Charlie", "abc"),
        ])
        core.wiki_api.load_revisions.return_value = iter([batch])

        wpa = WikiPageAnnotation(core)
        text, revision = wpa.get_annotation(cached_revision=cached)

        assert text.clear_text == "abc"
        assert text[0][1].user == "Alice"
        assert text[1][1].user == "Bob"
        assert text[2][1].user == "Charlie"

    def test_need_refresh_true_when_incomplete(self):
        """need_refresh should be True when batch is not complete."""
        core = MagicMock()
        batch = _make_batch(
            [_make_revision_dict(1, "Alice", "hello")],
            batchcomplete=False,
        )
        # Add continue data
        batch.data["continue"] = {"rvcontinue": "xxx|999", "continue": "||"}
        core.wiki_api.load_revisions.return_value = iter([batch])

        wpa = WikiPageAnnotation(core)
        text, revision = wpa.get_annotation()

        assert wpa.need_refresh is True

    def test_need_refresh_false_when_complete(self):
        """need_refresh should be False when batch is complete."""
        core = MagicMock()
        batch = _make_batch([_make_revision_dict(1, "Alice", "hello")])
        core.wiki_api.load_revisions.return_value = iter([batch])

        wpa = WikiPageAnnotation(core)
        text, revision = wpa.get_annotation()

        assert wpa.need_refresh is False


class TestGetUIRevisions:
    def _make_cached(self, text_str, revid=1, user="Alice"):
        cd = AnnotationCharData(revid=revid, user=user)
        at = AnnotatedText(tuple((ch, cd) for ch in text_str))
        rev = SiteAPIRevisionStructure(
            content=text_str, revid=revid, user=user, userid=1,
            timestamp="t", comment="c",
        )
        return CachedRevision(annotated_text=at, latest_revision=rev)

    def test_single_line_no_newline(self):
        """Single line text without newline should produce one UIRevision."""
        core = MagicMock()
        wpa = WikiPageAnnotation(core)
        cached = self._make_cached("hello")
        result = wpa.getUIRevisions(cached)

        assert len(result) == 1
        assert "Alice" in result[0].users

    def test_multiline_text(self):
        """Text with newlines should be split into lines."""
        core = MagicMock()
        wpa = WikiPageAnnotation(core)
        cached = self._make_cached("line1\nline2\nline3")
        result = wpa.getUIRevisions(cached)

        assert len(result) == 3

    def test_multiple_authors_on_line(self):
        """Different authors on the same line should all be in users set."""
        core = MagicMock()
        wpa = WikiPageAnnotation(core)
        cd1 = AnnotationCharData(revid=1, user="Alice")
        cd2 = AnnotationCharData(revid=2, user="Bob")
        at = AnnotatedText((
            ("h", cd1), ("i", cd1), (" ", cd2), ("!", cd2), ("\n", cd1),
        ))
        rev = SiteAPIRevisionStructure(
            content="hi !\n", revid=2, user="Bob", userid=1,
            timestamp="t", comment="c",
        )
        cached = CachedRevision(annotated_text=at, latest_revision=rev)

        result = wpa.getUIRevisions(cached)
        assert len(result) == 1
        assert result[0].users == {"Alice", "Bob"}

    def test_word_grouping_by_revid(self):
        """Consecutive chars with same revid should be grouped into words."""
        core = MagicMock()
        wpa = WikiPageAnnotation(core)
        cd1 = AnnotationCharData(revid=1, user="Alice")
        cd2 = AnnotationCharData(revid=2, user="Bob")
        # "ab" by Alice, "cd" by Bob
        at = AnnotatedText((
            ("a", cd1), ("b", cd1), ("c", cd2), ("d", cd2),
        ))
        rev = SiteAPIRevisionStructure(
            content="abcd", revid=2, user="Bob", userid=1,
            timestamp="t", comment="c",
        )
        cached = CachedRevision(annotated_text=at, latest_revision=rev)

        result = wpa.getUIRevisions(cached)
        assert len(result) == 1
        # Should have 2 word groups
        line = result[0].annotated_text
        assert len(line) == 2
        assert line[0][0] == "ab"
        assert line[1][0] == "cd"

    def test_empty_text(self):
        """Empty annotated text should produce no UIRevisions."""
        core = MagicMock()
        wpa = WikiPageAnnotation(core)
        at = AnnotatedText(())
        rev = SiteAPIRevisionStructure(
            revid=1, user="Alice", userid=1,
            timestamp="t", comment="c",
            slots={"main": {"content": ""}},
        )
        cached = CachedRevision(annotated_text=at, latest_revision=rev)
        result = wpa.getUIRevisions(cached)
        assert len(result) == 0

    def test_trailing_newline(self):
        """Text ending with newline should have the last line contain the content before it."""
        core = MagicMock()
        wpa = WikiPageAnnotation(core)
        cached = self._make_cached("hi\n")
        result = wpa.getUIRevisions(cached)
        # "hi\n" => one line with "hi" in it
        assert len(result) == 1
