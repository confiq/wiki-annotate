import logging
from wiki_annotate.wiki import Wiki, WikiRevision
from wiki_annotate.types import CachedRevision, RevisionData
from wiki_annotate.db.data import DataInterface
log = logging.getLogger(__name__)


class Annotate:

    def __init__(self, url: str):
        """
        :param url: full URL of page that should be annotated
        """
        self.wiki = Wiki(url)
        self.local_db = DataInterface(self)
        self.revisions = WikiRevision(self)

    def run(self):
        cached_revision = self.local_db.get_page()
        if not cached_revision:
            revision_data = RevisionData(self.wiki.get_page().latest_revision)
            annotation = self.revisions.get_annotation()
            cached_revision = CachedRevision(annotation, revision_data)
            self.local_db.save(cached_revision)

        #TODO: check if cached version match the live one
        return cached_revision

    def get_cached(self):

        pass


