import functools
import logging
from os import path
import jsons
from wiki_annotate.db.file_system import FileSystem
from wiki_annotate.types import CachedRevision
from wiki_annotate import config
from typing import List, Set, Dict, Tuple, Optional, Union
from google.cloud import storage
from google.cloud.exceptions import NotFound
from wiki_annotate.utils import timing

log = logging.getLogger(__name__)


class GCPStorage(FileSystem):
    def __init__(self):
        self.db = GCPStorageAPI(config.CACHE_BUCKET)

    def save_page_data(self, wikiid: str, page: str, cached_revision: CachedRevision, revision: int) -> bool:
        page = self.slugify(page)
        filename = path.join(self.data_directory, wikiid, page, f"{revision}.json")
        try:
            data = jsons.dumps(cached_revision)
        except Exception as e:
            log.error(f"Failed to serialize cache for revision {revision}: {e}")
            return False
        # GCS uploads are atomic by nature — no temp file needed
        try:
            self.db.write_blob(filename, data)
        except Exception as e:
            log.error(f"Failed to write cache blob {filename}: {e}")
            return False

        return True

    @timing
    def get_page_data(self, wikiid: str, page: str, revision: int = None) -> Union[None, CachedRevision]:
        page = self.slugify(page)
        dir_name = path.join(self.data_directory, wikiid, page)

        # Build candidates list: specific revision first, then all blobs sorted by updated time desc
        candidates = []
        if revision:
            candidates.append((path.join(dir_name, f"{revision}.json"), True))

        try:
            blobs = self.db.list_blobs(dir_name, delimiter=None)
            if blobs:
                sorted_blobs = sorted(blobs, key=lambda b: b[1], reverse=True)
                requested_filename = f"{revision}.json" if revision else None
                for name, _updated in sorted_blobs:
                    if name != requested_filename:
                        candidates.append((path.join(dir_name, name), False))
        except NotFound:
            pass

        for blob_path, is_specific in candidates:
            try:
                file_content = self.db.get_blob(blob_path)
                return jsons.loads(file_content, CachedRevision)
            except NotFound:
                continue
            except Exception as e:
                log.warning(f"Corrupt or unreadable cache blob {blob_path}, falling back to previous: {e}")
                try:
                    self.db.delete_blob(blob_path)
                except Exception:
                    pass

        return None

    @functools.cached_property
    def data_directory(self):
        return self.DATA_VERSION


class GCPStorageAPI:
    def __init__(self, bucket_name):
        client = storage.Client()
        self.bucket = client.bucket(bucket_name)

    def get_blob(self, filename):
        return self.bucket.blob(filename).download_as_string()

    def write_blob(self, filename, content):
        self.bucket.blob(filename).upload_from_string(content)

    def blob_exists(self, filename):
        return self.bucket.blob(filename).exists()

    def delete_blob(self, filename):
        self.bucket.blob(filename).delete()

    def list_blobs(self, prefix, delimiter='/'):
        blobs = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        return [(path.basename(blob.name), blob.updated) for blob in blobs]
