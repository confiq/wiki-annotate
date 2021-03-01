from wiki_annotate.db.abstraction import AbstractDB
from wiki_annotate.types import WikiPage
from typing import List, Set, Dict, Tuple, Optional, Union
from os import path
import os
import json

class FileSystem(AbstractDB):
    _DATA_DIRECTORY = None

    def get_page_data(self, domain: str, page: str, revision=None) -> Union[None, WikiPage]:
        # TODO: check if folder <domain>/<page>/ exist and get latest one
        if path.exists(path.join(self.data_directory, domain, page)):
            revision_file = path.join(self.data_directory, domain, page, f"{revision}.json")
            if path.exists(revision_file):
                return WikiPage(json.load(revision_file)) #TODO: fix it
            else:
                # TODO: scan and get the latest
                pass
        return None

    @property
    def data_directory(self):
        if not FileSystem._DATA_DIRECTORY:
            data = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', '..', 'wiki-page-data'))
            if not os.path.exists(data):
                os.mkdir(data)
            FileSystem._DATA_DIRECTORY = data
        return FileSystem._DATA_DIRECTORY
