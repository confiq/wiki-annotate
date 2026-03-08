from wiki_annotate.db.abstraction import AbstractDB
from wiki_annotate.types import CachedRevision
from abc import ABC, abstractmethod
import collections
import functools
import threading
from typing import List, Set, Dict, Tuple, Optional, Union
from os import path
import os
import tempfile
import time
import logging
import jsons
from wiki_annotate.utils import timing


log = logging.getLogger(__name__)

# In-memory LRU cache of deserialized CachedRevision objects, keyed by absolute file path.
# Filenames are revision-based so a new revision = new key; no explicit invalidation needed.
# Bounded to _CACHE_MAX_SIZE entries; oldest entries are evicted when full.
_CACHE_MAX_SIZE = 256
_memory_cache: collections.OrderedDict[str, CachedRevision] = collections.OrderedDict()
_memory_cache_lock = threading.Lock()  # guards all _memory_cache operations

# Per-file locks: ensures only one thread deserializes a given file at a time.
# Other threads that race to the same file will block and then get the cached result.
_file_locks: dict[str, threading.Lock] = {}
_file_locks_lock = threading.Lock()  # guards _file_locks dict membership


def _get_file_lock(file_path: str) -> threading.Lock:
    with _file_locks_lock:
        if file_path not in _file_locks:
            _file_locks[file_path] = threading.Lock()
        return _file_locks[file_path]


class FileSystem(AbstractDB):
    DATA_VERSION = 'v1'

    def save_page_data(self, wikiid: str, page: str, cached_revision: CachedRevision, revision: int) -> bool:
        page = self.slugify(page)
        dir_name = path.join(self.data_directory, wikiid, page)
        filename = path.join(dir_name, f"{revision}.json")
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        try:
            data = jsons.dumps(cached_revision)
        except Exception as e:
            log.error(f"Failed to serialize cache for revision {revision}: {e}")
            return False
        # Atomic write: serialize to a temp file in the same dir, then rename
        # into place. Prevents corrupt/empty files if the process is interrupted.
        # NamedTemporaryFile avoids the fd-leak risk of mkstemp+fdopen.
        try:
            with tempfile.NamedTemporaryFile(mode='w', dir=dir_name, suffix='.tmp', delete=False) as f:
                tmp_path = f.name
                try:
                    f.write(data)
                    f.flush()
                    os.fsync(f.fileno())
                except Exception:
                    try:
                        os.remove(tmp_path)
                    except OSError:
                        pass
                    raise
            os.replace(tmp_path, filename)
        except Exception as e:
            log.error(f"Failed to write cache file {filename}: {e}")
            try:
                os.remove(tmp_path)
            except (OSError, NameError):
                pass
            return False

        return True

    @timing
    def get_page_data(self, wikiid: str, page: str, revision: int = None) -> Union[None, CachedRevision]:
        page = self.slugify(page)
        dir_name = path.join(self.data_directory, wikiid, page)
        if not path.exists(dir_name):
            return None

        # If a specific revision was requested and it exists, try that first
        if revision and path.exists(path.join(dir_name, f"{revision}.json")):
            requested_file = f"{revision}.json"
            candidates = [requested_file]
        else:
            requested_file = None
            candidates = []

        # Append all files sorted by mtime descending as fallback candidates,
        # excluding the requested_file if it was already added above.
        # Only consider plain *.json files — ignore swap files, temp files, etc.
        files = [f for f in os.listdir(dir_name) if f.endswith('.json') and not f.startswith('.')]
        if requested_file is not None:
            files = [f for f in files if f != requested_file]
        candidates += sorted(files, key=lambda f: os.path.getmtime(path.join(dir_name, f)), reverse=True)

        for filename in candidates:
            revision_file = path.join(dir_name, filename)

            # Fast path: check cache before acquiring per-file lock.
            with _memory_cache_lock:
                if revision_file in _memory_cache:
                    log.debug(f"Cache hit (memory) for {revision_file}")
                    _memory_cache.move_to_end(revision_file)
                    return _memory_cache[revision_file]

            # Slow path: acquire per-file lock so only one thread deserializes.
            # Other threads racing here will block, then hit the fast-path above.
            file_lock = _get_file_lock(revision_file)
            with file_lock:
                # Re-check: another thread may have populated the cache while we waited.
                with _memory_cache_lock:
                    if revision_file in _memory_cache:
                        log.debug(f"Cache hit (memory, post-lock) for {revision_file}")
                        _memory_cache.move_to_end(revision_file)
                        return _memory_cache[revision_file]

                try:
                    with open(revision_file, 'r') as f:
                        file_content = f.read()
                    t0 = time.perf_counter()
                    result = jsons.loads(file_content, CachedRevision)
                    duration = time.perf_counter() - t0
                    log.debug(f"Cache deserialised in {duration:.2f}s ({len(file_content)} bytes, {revision_file})")
                    if duration > 0.5:
                        log.info(f"Slow cache deserialisation in {duration:.2f}s ({len(file_content)} bytes, {revision_file})")

                    with _memory_cache_lock:
                        _memory_cache[revision_file] = result
                        _memory_cache.move_to_end(revision_file)
                        if len(_memory_cache) > _CACHE_MAX_SIZE:
                            _memory_cache.popitem(last=False)

                    return result
                except Exception as e:
                    log.warning(f"Corrupt or empty cache file {revision_file}, falling back to previous: {e}")
                    try:
                        os.remove(revision_file)
                    except OSError:
                        pass

        return None

    @functools.cached_property
    def data_directory(self):
        data_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'data-page', self.DATA_VERSION))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir
