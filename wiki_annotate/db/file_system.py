from wiki_annotate.db.abstraction import AbstractDB
from wiki_annotate.types import CachedRevision
from abc import ABC, abstractmethod
import functools
from typing import List, Set, Dict, Tuple, Optional, Union
from os import path
import os
import logging
import jsons
from wiki_annotate.utils import timing


log = logging.getLogger(__name__)


class FileSystem(AbstractDB):
    DATA_VERSION = 'v1'

    def save_page_data(self, wikiid: str, page: str, cached_revision: CachedRevision, revision: int) -> bool:
        page = self.slugify(page)
        filename = path.join(self.data_directory, wikiid, page, f"{revision}.json")
        if not os.path.isdir(path.dirname(filename)):
            os.makedirs(path.dirname(filename))
        with open(filename, 'w') as f:
            f.write(jsons.dumps(cached_revision))

    @timing
    def get_page_data(self, wikiid: str, page: str, revision: int = None) -> Union[None, CachedRevision]:
        page = self.slugify(page)
        dir_name = path.join(self.data_directory, wikiid, page)
        revision_file = None
        if path.exists(dir_name):
            revision_file = path.join(dir_name, f"{revision}.json")
            revision_file = revision_file if revision and path.exists(revision_file) else None
            if not revision_file:
                # need to get latest revision file, this can be very expensive if we have lot of revisions
                files = os.listdir(dir_name)
                if files:
                    files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
                    revision_file = path.join(dir_name, files.pop())
        if revision_file:
            with open(revision_file, 'r') as f:
                file_content = f.read()
            # the deserialization of this is  expensive :(
            return jsons.loads(file_content, CachedRevision)

    @functools.cached_property
    def data_directory(self):
        data_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'data-page', self.DATA_VERSION))
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir
