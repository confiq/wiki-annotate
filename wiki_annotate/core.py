import logging
from wiki_annotate.wiki import Wiki, WikiPageAnnotation
from wiki_annotate.types import CachedRevision, RevisionData, UIRevision
from wiki_annotate.db.data import DataInterface
from typing import List, Set, Dict, Tuple, Optional, Union

from wiki_annotate.utils import catchtime
from IPython import embed

log = logging.getLogger(__name__)


class Annotate:

    def __init__(self, url: str):
        """
        :param url: full URL of page that should be annotated
        """
        self.wiki = Wiki(url)
        self.local_db = DataInterface(self)
        self.wiki_page_annotation = WikiPageAnnotation(self)

    def run(self) -> CachedRevision:
        cached_revision = self.local_db.get_page()
        latest_revision = RevisionData(self.wiki.get_page().latest_revision)
        if not cached_revision:
            log.debug('no cache found for this page')
            annotation = self.wiki_page_annotation.get_annotation()
            cached_revision = CachedRevision(annotation, latest_revision)
            self.local_db.save(cached_revision)
        elif cached_revision.latest_revision.id < latest_revision.id:
            log.debug('refreshing cached annotation')
            annotation = self.wiki_page_annotation.get_annotation(cached_revision)
            self.local_db.save(CachedRevision(annotation, latest_revision))
        return cached_revision


class APIAnnotate(Annotate):
    def get_ui_revisions(self, text: CachedRevision) -> Tuple[UIRevision]:
        return self.wiki_page_annotation.getUIRevisions(text)
