"""Tests for wiki_annotate.db modules."""
import pytest
from wiki_annotate.db.abstraction import AbstractDB


class TestSlugify:
    def test_simple_text(self):
        assert AbstractDB.slugify("Hello World") == "hello-world"

    def test_special_chars_removed(self):
        assert AbstractDB.slugify("Hello! World?") == "hello-world"

    def test_dashes_preserved(self):
        assert AbstractDB.slugify("hello-world") == "hello-world"

    def test_underscores_preserved(self):
        assert AbstractDB.slugify("hello_world") == "hello_world"

    def test_multiple_spaces(self):
        assert AbstractDB.slugify("hello   world") == "hello-world"

    def test_multiple_dashes(self):
        assert AbstractDB.slugify("hello---world") == "hello-world"

    def test_leading_trailing_stripped(self):
        assert AbstractDB.slugify("--hello--") == "hello"
        assert AbstractDB.slugify("__hello__") == "hello"

    def test_unicode_default(self):
        # Without allow_unicode, non-ASCII chars are removed
        result = AbstractDB.slugify("café")
        assert result == "cafe"

    def test_unicode_allowed(self):
        result = AbstractDB.slugify("café", allow_unicode=True)
        assert result == "café"

    def test_wikipedia_page_title(self):
        result = AbstractDB.slugify("United_States")
        assert result == "united_states"

    def test_empty_string(self):
        assert AbstractDB.slugify("") == ""

    def test_page_with_colon(self):
        result = AbstractDB.slugify("Help:Contents")
        assert result == "helpcontents"

    def test_mixed_case(self):
        assert AbstractDB.slugify("HelloWorld") == "helloworld"
