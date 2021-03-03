from wiki_annotate.db.file_system import FileSystem
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.types import WikiRevision
import wiki_annotate.config as config


class DataInterface:
    DRIVER = config.DB_DRIVER

    def __init__(self, annotate):
        self.annotate = annotate
        self.db = DataInterface.DRIVER()

    def get_page(self, revision=None) -> Union[None, WikiRevision]:
        return self.db.get_page_data(self.annotate.wiki.wikiid, self.annotate.wiki.page_name, revision)
