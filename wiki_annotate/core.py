import logging
from wiki_annotate.wiki import Wiki, WikiRevision
from wiki_annotate.types import CachedRevision, RevisionData
from wiki_annotate.db.data import DataInterface
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
        self.revisions = WikiRevision(self)

    def run(self):
        cached_revision = self.local_db.get_page()
        latest_revision = RevisionData(self.wiki.get_page().latest_revision)
        if not cached_revision:
            with catchtime() as ct:
                annotation = self.revisions.get_annotation()
            log.debug(f"annotating took {ct():.4f} secs")
            cached_revision = CachedRevision(annotation, latest_revision)
            self.local_db.save(cached_revision)
        else:
            log.debug('using cache')
            if cached_revision.latest_revision.id < latest_revision.id:
                with catchtime() as ct:
                    annotation = self.revisions.get_annotation(cached_revision.latest_revision.id)
                log.debug(f"annotating took {ct():.4f} secs")
                self.local_db.save(CachedRevision(annotation, latest_revision))
        return cached_revision

    def get_cached(self):

        pass


