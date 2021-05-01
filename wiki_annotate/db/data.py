from wiki_annotate.db.file_system import FileSystem
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.types import CachedRevision
import wiki_annotate.config as config
import logging

log = logging.getLogger(__name__)


class DataInterface:
    DRIVER = config.DB_DRIVER

    def __init__(self, core):
        self.core = core
        self.db = DataInterface.DRIVER()

    def get_page(self, revision=None) -> Union[None, CachedRevision]:
        return self.db.get_page_data(self.core.wiki.wikiid, self.core.wiki.page_name, revision)

    def save(self, cached_revision: CachedRevision):
        log.debug('saving cache')
        return self.db.save_page_data(self.annotate.wiki.wikiid, self.annotate.wiki.page_name, cached_revision,
                                      cached_revision.latest_revision.id)
