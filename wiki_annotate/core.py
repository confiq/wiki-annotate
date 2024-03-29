import logging
from wiki_annotate.wiki import Wiki
from wiki_annotate.wiki_annotation import WikiPageAnnotation
from wiki_annotate.types import CachedRevision, RevisionData, UIRevision
from wiki_annotate.db.data import DataInterface
from wiki_annotate.utils import catchtime, timing
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.wiki_siteapi import WikiAPI
log = logging.getLogger(__name__)


class Annotate:

    def __init__(self, url: str):
        """
        :param url: full URL of page that should be annotated
        """
        self.wiki = Wiki(url)
        self.local_db = DataInterface(self)
        self.wiki_page_annotation = WikiPageAnnotation(self)
        self.wiki_api = WikiAPI(self)

    @timing
    def run(self) -> CachedRevision:
        latest_revision = RevisionData(self.wiki.get_page().latest_revision)
        cached_revision = self.local_db.get_page(latest_revision.id)
        if not cached_revision:
            log.debug('no cache found for this page')
            annotation, last_revision = self.wiki_page_annotation.get_annotation()
            cached_revision = CachedRevision(annotation, last_revision)
            self.local_db.save(cached_revision)
        elif cached_revision.latest_revision.revid < latest_revision.id:
            log.debug('refreshing cached annotation')
            annotation, last_revision = self.wiki_page_annotation.get_annotation(cached_revision)
            cached_revision = CachedRevision(annotation, last_revision)
            self.local_db.save(cached_revision)

        return cached_revision

    def get_ui_revisions(self, data: Optional[CachedRevision] = None) -> Tuple[UIRevision]:
        data = self.run() if not data else data
        return self.wiki_page_annotation.getUIRevisions(data)
