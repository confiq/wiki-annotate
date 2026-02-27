"""Tests for wiki_annotate.exceptions module."""
import pytest
from wiki_annotate.exceptions import (
    WikiException,
    AnnotatedTextException,
    DiffLogicException,
    WikiPageAPIException,
    WikiAPIException,
)
from wiki_annotate.types import AnnotatedText, AnnotationCharData


class TestWikiException:
    def test_is_exception(self):
        assert issubclass(WikiException, Exception)


class TestAnnotatedTextException:
    def test_str(self):
        cd = AnnotationCharData(revid=1, user="Alice")
        at = AnnotatedText((("a", cd),))
        exc = AnnotatedTextException("something broke", at)
        assert str(exc) == "something broke"

    def test_message_attribute(self):
        cd = AnnotationCharData(revid=1, user="Alice")
        at = AnnotatedText((("a", cd),))
        exc = AnnotatedTextException("msg", at)
        assert exc.message == "msg"

    def test_inherits_wiki_exception(self):
        assert issubclass(AnnotatedTextException, WikiException)


class TestDiffLogicException:
    def test_str_with_diff_object(self):
        from wiki_annotate.diff import DiffLogic
        cd = AnnotationCharData(revid=1, user="Alice")
        prev = DiffLogic.init_text("abc", cd)
        dl = DiffLogic("xyz", prev)
        exc = DiffLogicException("mismatch", dl)
        result = str(exc)
        assert "mismatch" in result
        assert "Pointer is at" in result
        assert "previous_annotation:" in result
        assert "new_revision_text:" in result

    def test_inherits_wiki_exception(self):
        assert issubclass(DiffLogicException, WikiException)


class TestWikiPageAPIException:
    def test_inherits_wiki_exception(self):
        assert issubclass(WikiPageAPIException, WikiException)


class TestWikiAPIException:
    def test_inherits_wiki_exception(self):
        assert issubclass(WikiAPIException, WikiException)
