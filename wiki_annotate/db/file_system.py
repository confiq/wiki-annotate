from wiki_annotate.db.abstraction import AbstractDB
from wiki_annotate.types import CachedRevision
from typing import List, Set, Dict, Tuple, Optional, Union
from os import path
import os
import json
import unicodedata
import re
import logging

log = logging.getLogger(__name__)

def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


class FileSystem(AbstractDB):
    _DATA_DIRECTORY = None

    def save_page_data(self, wikiid: str, page: str, cached_revision: CachedRevision, revision: int) -> bool:
        page = slugify(page)
        filename = path.join(self.data_directory, wikiid, page, f"{revision}.json")

        with open(filename, 'w') as f:
            f.write(json.dumps(CachedRevision))  # TODO:
        pass

    def get_page_data(self, wikiid: str, page: str, revision: int = None) -> Union[None, CachedRevision]:
        page = slugify(page)
        dir_name = path.join(self.data_directory, wikiid, page)
        if path.exists(dir_name):
            revision_file = path.join(dir_name, f"{revision}.json")
            if path.exists(revision_file):
                return CachedRevision(json.load(revision_file))  # TODO: fix it
            else:
                files = os.listdir(dir_name)
                files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
                return CachedRevision(json.load(files.pop()))
        return None

    @property
    def data_directory(self):
        if not FileSystem._DATA_DIRECTORY:
            data = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'wiki-page-data'))
            if not os.path.exists(data):
                os.makedirs(data)
            FileSystem._DATA_DIRECTORY = data
        return FileSystem._DATA_DIRECTORY

