import functools
from os import path
import jsons
from wiki_annotate.db.file_system import FileSystem
from wiki_annotate.types import CachedRevision
from wiki_annotate import config
from typing import List, Set, Dict, Tuple, Optional, Union
from google.cloud import storage
from google.cloud.exceptions import NotFound
from wiki_annotate.utils import timing


class GCPStorage(FileSystem):
    def __init__(self):
        self.db = GCPStorageAPI(config.CACHE_BUCKET)

    def save_page_data(self, wikiid: str, page: str, cached_revision: CachedRevision, revision: int) -> None:
        page = self.slugify(page)
        filename = path.join(self.data_directory, wikiid, page, f"{revision}.json")
        self.db.write_blob(filename, jsons.dumps(cached_revision))

    @timing
    def get_page_data(self, wikiid: str, page: str, revision: int = None) -> Union[None, CachedRevision]:
        page = self.slugify(page)
        dir_name = path.join(self.data_directory, wikiid, page)
        file_content = None
        revision_file = path.join(dir_name, f"{revision}.json")
        # it's better to ask forgiveness than permission
        try:
            file_content = self.db.get_blob(revision_file) if revision else None
        except NotFound:
            pass
        try:
            if not file_content:
                # try to catch the latest
                # need to get the latest revision files, this can be very expensive if we have a lot of revisions
                files = self.db.list_blobs(dir_name, delimiter=None)
                if files:
                    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
                    cached_file_name = path.join(dir_name, files.pop())
                    file_content = self.db.get_blob(cached_file_name)
        except NotFound:
            pass
        if file_content:
            return jsons.loads(file_content, CachedRevision)

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

    def list_blobs(self, prefix, delimiter='/'):
        blobs = self.bucket.list_blobs(prefix=prefix, delimiter=delimiter)
        return [path.basename(blob.name) for blob in blobs]
