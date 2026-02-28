"""Tests for wiki_annotate.types module."""
import pytest
from wiki_annotate.types import (
    AnnotationCharData,
    RevisionData,
    AnnotatedText,
    SiteAPIRevisionStructure,
    CachedRevision,
    UIRevision,
    APIPageData,
    APIAnnotate,
    SiteAPIRevisions,
)


class TestAnnotationCharData:
    def test_basic_init(self):
        cd = AnnotationCharData(revid=1, user="Alice")
        assert cd.revid == 1
        assert cd.user == "Alice"

    def test_init_ignores_extra_kwargs(self):
        cd = AnnotationCharData(revid=1, user="Alice", comment="test", timestamp="x")
        assert cd.revid == 1
        assert cd.user == "Alice"
        assert not hasattr(cd, "comment")

    def test_getitem(self):
        cd = AnnotationCharData(revid=42, user="Bob")
        assert cd["revid"] == 42
        assert cd["user"] == "Bob"

    def test_getitem_missing_raises(self):
        cd = AnnotationCharData(revid=1, user="Alice")
        with pytest.raises(AttributeError):
            cd["nonexistent"]


class TestRevisionData:
    def test_id_property(self):
        rd = RevisionData(revision={"revid": 123})
        assert rd.id == 123

    def test_id_missing_returns_none(self):
        rd = RevisionData(revision={})
        assert rd.id is None


class TestAnnotatedText:
    def test_clear_text(self, make_char_data):
        cd = make_char_data()
        at = AnnotatedText(tuple((ch, cd) for ch in "abc"))
        assert at.clear_text == "abc"

    def test_clear_text_empty(self):
        at = AnnotatedText(())
        assert at.clear_text == ""

    def test_len(self, make_char_data):
        cd = make_char_data()
        at = AnnotatedText(tuple((ch, cd) for ch in "hello"))
        assert len(at) == 5

    def test_len_empty(self):
        at = AnnotatedText(())
        assert len(at) == 0

    def test_getitem(self, make_char_data):
        cd = make_char_data()
        at = AnnotatedText((("a", cd), ("b", cd)))
        assert at[0] == ("a", cd)
        assert at[1] == ("b", cd)

    def test_iter(self, make_char_data):
        cd = make_char_data()
        items = [("x", cd), ("y", cd)]
        at = AnnotatedText(tuple(items))
        assert list(at) == items

    def test_clear_text_preserves_whitespace(self, make_char_data):
        cd = make_char_data()
        at = AnnotatedText(tuple((ch, cd) for ch in "a b\nc"))
        assert at.clear_text == "a b\nc"


class TestSiteAPIRevisionStructure:
    def test_init_from_api_kwargs(self, sample_revision_kwargs):
        rev = SiteAPIRevisionStructure(**sample_revision_kwargs)
        assert rev.revid == 100
        assert rev.user == "Alice"
        assert rev.userid == 42
        assert rev.timestamp == "2024-01-15T10:00:00Z"
        assert rev.comment == "Initial revision"
        assert rev.content == "Hello world"

    def test_content_from_slots(self):
        rev = SiteAPIRevisionStructure(
            revid=1, user="A", userid=1, timestamp="t", comment="c",
            slots={"main": {"content": "slot content"}},
        )
        assert rev.content == "slot content"

    def test_content_param_overrides_slots(self):
        rev = SiteAPIRevisionStructure(
            content="direct content",
            revid=1, user="A", userid=1, timestamp="t", comment="c",
            slots={"main": {"content": "slot content"}},
        )
        assert rev.content == "direct content"


class TestCachedRevision:
    def test_fields(self, sample_cached_revision):
        assert sample_cached_revision.latest_revision.revid == 100
        assert sample_cached_revision.annotated_text.clear_text == "Hello world"


class TestUIRevision:
    def test_users_converted_to_set(self, make_annotated_text):
        at = make_annotated_text("hi")
        ui = UIRevision(users=["Alice", "Bob", "Alice"], annotated_text=at)
        assert ui.users == {"Alice", "Bob"}

    def test_empty_users(self, make_annotated_text):
        at = make_annotated_text("x")
        ui = UIRevision(users=[], annotated_text=at)
        assert ui.users == set()


class TestAPIPageData:
    def test_defaults(self):
        pd = APIPageData()
        assert pd.is_error is False
        assert pd.errors_messages == []
        assert pd.page_title == ""

    def test_add_error_msg(self):
        pd = APIPageData()
        pd.add_error_msg("Error 1")
        pd.add_error_msg("Error 2")
        assert pd.errors_messages == ["Error 1", "Error 2"]

    def test_separate_instances_dont_share_errors(self):
        pd1 = APIPageData()
        pd1.add_error_msg("only for pd1")
        pd2 = APIPageData()
        assert pd2.errors_messages == []


class TestAPIAnnotate:
    def test_defaults(self):
        aa = APIAnnotate(text=())
        assert aa.need_refresh is False
        assert aa.last_edited is None
        assert aa.total_revisions is False


class TestSiteAPIRevisions:
    def test_revisions_property(self):
        data = {
            "batchcomplete": True,
            "query": {"pages": [{"revisions": [{"revid": 1}, {"revid": 2}]}]},
        }
        sar = SiteAPIRevisions(data)
        assert len(sar.revisions) == 2
        assert sar.revisions[0]["revid"] == 1

    def test_batchcomplete_true(self):
        data = {"batchcomplete": True, "query": {"pages": [{"revisions": []}]}}
        assert SiteAPIRevisions(data).batchcomplete is True

    def test_batchcomplete_false_when_missing(self):
        data = {"query": {"pages": [{"revisions": []}]}}
        assert SiteAPIRevisions(data).batchcomplete is False

    def test_batchcomplete_false_when_falsy(self):
        data = {"batchcomplete": False, "query": {"pages": [{"revisions": []}]}}
        assert SiteAPIRevisions(data).batchcomplete is False

    def test_continue_from(self):
        data = {
            "continue": {"rvcontinue": "20210308214123|468927", "continue": "||"},
            "query": {"pages": [{"revisions": []}]},
        }
        sar = SiteAPIRevisions(data)
        assert sar.continue_from == "468927"

    def test_continue_from_none_when_batchcomplete(self):
        data = {
            "batchcomplete": True,
            "continue": {"rvcontinue": "20210308214123|468927", "continue": "||"},
            "query": {"pages": [{"revisions": []}]},
        }
        sar = SiteAPIRevisions(data)
        assert sar.continue_from is None

    def test_continue_from_none_when_no_continue(self):
        data = {"query": {"pages": [{"revisions": []}]}}
        sar = SiteAPIRevisions(data)
        assert sar.continue_from is None
