from wiki_annotate.db.abstraction import AbstractDB
from wiki_annotate.types import CachedRevision
from abc import ABC, abstractmethod
import functools
from typing import List, Set, Dict, Tuple, Optional, Union
from os import path
import os
import tempfile
import time
import logging
import jsons
from wiki_annotate.utils import timing


log = logging.getLogger(__name__)


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
        try:
            fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
            try:
                with os.fdopen(fd, 'w') as f:
                    f.write(data)
                os.replace(tmp_path, filename)
            except Exception:
                os.remove(tmp_path)
                raise
        except Exception as e:
            log.error(f"Failed to write cache file {filename}: {e}")
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
        files = os.listdir(dir_name)
        if requested_file is not None:
            files = [f for f in files if f != requested_file]
        candidates += sorted(files, key=lambda f: os.path.getmtime(path.join(dir_name, f)), reverse=True)

        for filename in candidates:
            revision_file = path.join(dir_name, filename)
            # the deserialization of this is expensive :(
            try:
                with open(revision_file, 'r') as f:
                    file_content = f.read()
                t0 = time.perf_counter()
                result = jsons.loads(file_content, CachedRevision)
                log.info(f"Cache deserialised in {time.perf_counter() - t0:.2f}s ({len(file_content)} bytes, {revision_file})")
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
