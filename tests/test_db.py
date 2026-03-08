"""Tests for wiki_annotate.db modules."""
import json
import os
import time
import pytest
import jsons
from wiki_annotate.db.abstraction import AbstractDB
import wiki_annotate.db.file_system as fs_module
from wiki_annotate.db.file_system import FileSystem


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


@pytest.fixture
def fs(tmp_path, monkeypatch):
    """FileSystem instance pointing at a temp directory."""
    instance = FileSystem.__new__(FileSystem)
    monkeypatch.setattr(type(instance), "data_directory",
                        property(lambda self: str(tmp_path)))
    return instance


def _write_cache(fs, wikiid, page, revision, cached_revision):
    """Helper: serialise and write a valid cache file."""
    fs.save_page_data(wikiid, page, cached_revision, revision)


def _write_corrupt(fs, wikiid, page, revision):
    """Helper: write an empty / invalid JSON file to simulate corruption."""
    slug = AbstractDB.slugify(page)
    dir_name = os.path.join(fs.data_directory, wikiid, slug)
    os.makedirs(dir_name, exist_ok=True)
    with open(os.path.join(dir_name, f"{revision}.json"), "w") as f:
        f.write("")  # empty → invalid JSON


class TestFileSystemGetPageData:

    def test_returns_none_when_no_cache_dir(self, fs):
        assert fs.get_page_data("en-wikipedia", "nonexistent") is None

    def test_returns_none_when_dir_empty(self, fs, sample_cached_revision):
        slug = AbstractDB.slugify("pele")
        os.makedirs(os.path.join(fs.data_directory, "en-wikipedia", slug))
        assert fs.get_page_data("en-wikipedia", "pele") is None

    def test_returns_valid_cache(self, fs, sample_cached_revision):
        _write_cache(fs, "en-wikipedia", "pele", 100, sample_cached_revision)
        result = fs.get_page_data("en-wikipedia", "pele")
        assert result is not None
        assert result.latest_revision.revid == sample_cached_revision.latest_revision.revid

    def test_corrupt_latest_falls_back_to_previous(self, fs, sample_cached_revision):
        # Write a valid older cache, then a corrupt newer one
        _write_cache(fs, "en-wikipedia", "pele", 100, sample_cached_revision)
        time.sleep(0.01)  # ensure mtime ordering
        _write_corrupt(fs, "en-wikipedia", "pele", 200)

        result = fs.get_page_data("en-wikipedia", "pele")
        assert result is not None
        assert result.latest_revision.revid == 100

    def test_corrupt_file_is_deleted_after_fallback(self, fs, sample_cached_revision):
        _write_cache(fs, "en-wikipedia", "pele", 100, sample_cached_revision)
        time.sleep(0.01)
        _write_corrupt(fs, "en-wikipedia", "pele", 200)

        slug = AbstractDB.slugify("pele")
        corrupt_path = os.path.join(fs.data_directory, "en-wikipedia", slug, "200.json")
        assert os.path.exists(corrupt_path)

        fs.get_page_data("en-wikipedia", "pele")
        assert not os.path.exists(corrupt_path)

    def test_all_corrupt_returns_none(self, fs):
        _write_corrupt(fs, "en-wikipedia", "pele", 100)
        _write_corrupt(fs, "en-wikipedia", "pele", 200)
        assert fs.get_page_data("en-wikipedia", "pele") is None

    def test_specific_revision_returned_when_requested(self, fs, sample_cached_revision):
        _write_cache(fs, "en-wikipedia", "pele", 100, sample_cached_revision)
        result = fs.get_page_data("en-wikipedia", "pele", revision=100)
        assert result is not None
        assert result.latest_revision.revid == 100

    def test_specific_revision_missing_falls_back_to_latest(self, fs, sample_cached_revision):
        # revision=999 doesn't exist — should fall back to latest valid file
        _write_cache(fs, "en-wikipedia", "pele", 100, sample_cached_revision)
        result = fs.get_page_data("en-wikipedia", "pele", revision=999)
        assert result is not None
        assert result.latest_revision.revid == 100

    def test_multiple_corrupt_falls_back_to_oldest_valid(self, fs, sample_cached_revision):
        # valid at 100, corrupt at 200 and 300
        _write_cache(fs, "en-wikipedia", "pele", 100, sample_cached_revision)
        time.sleep(0.01)
        _write_corrupt(fs, "en-wikipedia", "pele", 200)
        time.sleep(0.01)
        _write_corrupt(fs, "en-wikipedia", "pele", 300)

        result = fs.get_page_data("en-wikipedia", "pele")
        assert result is not None
        assert result.latest_revision.revid == 100


@pytest.fixture(autouse=True)
def clear_memory_cache():
    """Reset the module-level in-memory cache between tests."""
    fs_module._memory_cache.clear()
    fs_module._file_locks.clear()
    yield
    fs_module._memory_cache.clear()
    fs_module._file_locks.clear()


class TestFileSystemMemoryCache:

    def test_jsons_loads_called_once_for_repeated_reads(self, fs, sample_cached_revision, monkeypatch):
        """Second call for the same revision must be served from memory — jsons.loads not called again."""
        _write_cache(fs, "en-wikipedia", "pele", 100, sample_cached_revision)

        call_count = 0
        original_loads = jsons.loads

        def counting_loads(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return original_loads(*args, **kwargs)

        monkeypatch.setattr(fs_module.jsons, "loads", counting_loads)

        fs.get_page_data("en-wikipedia", "pele")
        fs.get_page_data("en-wikipedia", "pele")

        assert call_count == 1, f"jsons.loads called {call_count} times; expected 1 (cache should serve second read)"

    def test_cache_result_is_identical_object(self, fs, sample_cached_revision):
        """Memory cache should return the exact same CachedRevision instance."""
        _write_cache(fs, "en-wikipedia", "pele", 100, sample_cached_revision)

        result1 = fs.get_page_data("en-wikipedia", "pele")
        result2 = fs.get_page_data("en-wikipedia", "pele")

        assert result1 is result2

    def test_lru_eviction_respects_max_size(self, fs, sample_cached_revision, monkeypatch):
        """Cache should not grow beyond _CACHE_MAX_SIZE entries."""
        monkeypatch.setattr(fs_module, "_CACHE_MAX_SIZE", 3)

        for rev in range(1, 6):
            _write_cache(fs, "en-wikipedia", f"page{rev}", rev, sample_cached_revision)
            fs.get_page_data("en-wikipedia", f"page{rev}")

        assert len(fs_module._memory_cache) <= 3

    def test_different_revisions_each_deserialize_once(self, fs, sample_cached_revision, monkeypatch):
        """Each distinct revision file should be deserialized exactly once."""
        _write_cache(fs, "en-wikipedia", "pele", 100, sample_cached_revision)
        _write_cache(fs, "en-wikipedia", "maradona", 200, sample_cached_revision)

        call_count = 0
        original_loads = jsons.loads

        def counting_loads(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return original_loads(*args, **kwargs)

        monkeypatch.setattr(fs_module.jsons, "loads", counting_loads)

        # Read each twice
        fs.get_page_data("en-wikipedia", "pele")
        fs.get_page_data("en-wikipedia", "pele")
        fs.get_page_data("en-wikipedia", "maradona")
        fs.get_page_data("en-wikipedia", "maradona")

        assert call_count == 2, f"Expected 2 deserialisations (one per unique file), got {call_count}"
