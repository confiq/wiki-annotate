"""Tests for wiki_annotate.diff module."""
import pytest
from wiki_annotate.diff import DiffLogic
from wiki_annotate.types import AnnotatedText, AnnotationCharData
from wiki_annotate.exceptions import DiffLogicException


class TestDiffLogicInitText:
    def test_basic_text(self):
        cd = AnnotationCharData(revid=1, user="Alice")
        at = DiffLogic.init_text("abc", cd)
        assert isinstance(at, AnnotatedText)
        assert len(at) == 3
        assert at[0] == ("a", cd)
        assert at[1] == ("b", cd)
        assert at[2] == ("c", cd)

    def test_empty_text(self):
        cd = AnnotationCharData(revid=1, user="Alice")
        at = DiffLogic.init_text("", cd)
        assert len(at) == 0

    def test_single_char(self):
        cd = AnnotationCharData(revid=1, user="Alice")
        at = DiffLogic.init_text("x", cd)
        assert len(at) == 1
        assert at[0] == ("x", cd)

    def test_whitespace_and_newlines(self):
        cd = AnnotationCharData(revid=1, user="Alice")
        at = DiffLogic.init_text("a\nb", cd)
        assert at.clear_text == "a\nb"
        assert len(at) == 3

    def test_all_chars_share_same_annotation(self):
        cd = AnnotationCharData(revid=5, user="Bob")
        at = DiffLogic.init_text("hello", cd)
        for ch, data in at:
            assert data is cd


class TestDiffLogicRun:
    def _make_annotated(self, text, revid=1, user="Alice"):
        cd = AnnotationCharData(revid=revid, user=user)
        return DiffLogic.init_text(text, cd)

    def test_no_change(self):
        """Diffing identical text should preserve all annotations."""
        prev = self._make_annotated("hello")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("hello", prev)
        result = dl.run(new_cd)
        assert result.clear_text == "hello"
        # All chars should retain original annotation (Alice, rev 1)
        for _, cd in result:
            assert cd.revid == 1
            assert cd.user == "Alice"

    def test_append_text(self):
        """Appending text should create new annotations for added chars."""
        prev = self._make_annotated("hello")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("hello world", prev)
        result = dl.run(new_cd)
        assert result.clear_text == "hello world"
        # First 5 chars ("hello") should be Alice's
        for i in range(5):
            assert result[i][1].user == "Alice"
        # " world" (6 chars) should be Bob's
        for i in range(5, 11):
            assert result[i][1].user == "Bob"

    def test_prepend_text(self):
        """Prepending text should attribute new chars to new author."""
        prev = self._make_annotated("world")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("hello world", prev)
        result = dl.run(new_cd)
        assert result.clear_text == "hello world"
        # "hello " should be Bob's
        for i in range(6):
            assert result[i][1].user == "Bob"
        # "world" should be Alice's
        for i in range(6, 11):
            assert result[i][1].user == "Alice"

    def test_delete_text(self):
        """Deleting text should remove those chars entirely."""
        prev = self._make_annotated("hello world")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("hello", prev)
        result = dl.run(new_cd)
        assert result.clear_text == "hello"
        for _, cd in result:
            assert cd.user == "Alice"

    def test_replace_text(self):
        """Replacing a substring should attribute replacement to new author."""
        prev = self._make_annotated("hello world")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("hello earth", prev)
        result = dl.run(new_cd)
        assert result.clear_text == "hello earth"
        # "hello " preserved from Alice
        for i in range(6):
            assert result[i][1].user == "Alice"
        # "earth" from Bob
        for i in range(6, 11):
            assert result[i][1].user == "Bob"

    def test_full_replacement(self):
        """Completely replacing text should all be from new author."""
        prev = self._make_annotated("abc")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("xyz", prev)
        result = dl.run(new_cd)
        assert result.clear_text == "xyz"
        for _, cd in result:
            assert cd.user == "Bob"

    def test_insert_in_middle(self):
        """Inserting text in the middle."""
        prev = self._make_annotated("ac")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("abc", prev)
        result = dl.run(new_cd)
        assert result.clear_text == "abc"
        assert result[0][1].user == "Alice"  # 'a'
        assert result[1][1].user == "Bob"    # 'b'
        assert result[2][1].user == "Alice"  # 'c'

    def test_multiple_revisions_chain(self):
        """Chain three revisions and verify cumulative attribution."""
        cd1 = AnnotationCharData(revid=1, user="Alice")
        text1 = DiffLogic.init_text("hello", cd1)

        cd2 = AnnotationCharData(revid=2, user="Bob")
        text2 = DiffLogic("hello world", text1).run(cd2)

        cd3 = AnnotationCharData(revid=3, user="Charlie")
        text3 = DiffLogic("hello brave world", text2).run(cd3)

        assert text3.clear_text == "hello brave world"
        # "hello" (0-4) from Alice (original text)
        for i in range(5):
            assert text3[i][1].user == "Alice"
        # The space at index 5 was Bob's (" world" insertion in rev 2)
        assert text3[5][1].user == "Bob"
        # "world" at the end is Bob's
        assert text3[-1][1].user == "Bob"

    def test_empty_to_text(self):
        """Diff from empty to text - all new."""
        prev = self._make_annotated("")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("hello", prev)
        result = dl.run(new_cd)
        assert result.clear_text == "hello"
        for _, cd in result:
            assert cd.user == "Bob"

    def test_text_to_empty(self):
        """Diff from text to empty - all deleted."""
        prev = self._make_annotated("hello")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("", prev)
        result = dl.run(new_cd)
        assert result.clear_text == ""
        assert len(result) == 0

    def test_unicode_text(self):
        """Handle unicode characters correctly."""
        prev = self._make_annotated("café")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("café latte", prev)
        result = dl.run(new_cd)
        assert result.clear_text == "café latte"

    def test_multiline_diff(self):
        """Handle multiline text with newlines."""
        prev = self._make_annotated("line1\nline2")
        new_cd = AnnotationCharData(revid=2, user="Bob")
        dl = DiffLogic("line1\nline2\nline3", prev)
        result = dl.run(new_cd)
        assert result.clear_text == "line1\nline2\nline3"


class TestDiffLogicAppendEqual:
    def test_append_equal_matches(self):
        cd = AnnotationCharData(revid=1, user="Alice")
        prev = DiffLogic.init_text("abc", cd)
        dl = DiffLogic("abc", prev)
        result = dl._append_equal("abc")
        assert len(result) == 3
        assert result[0] == ("a", cd)
        assert result[1] == ("b", cd)
        assert result[2] == ("c", cd)

    def test_append_equal_mismatch_raises(self):
        cd = AnnotationCharData(revid=1, user="Alice")
        prev = DiffLogic.init_text("abc", cd)
        dl = DiffLogic("xyz", prev)
        with pytest.raises(DiffLogicException):
            dl._append_equal("xyz")
