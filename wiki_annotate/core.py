import logging
from wiki_annotate.wiki import Wiki, WikiRevision
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
        page_data = self.local_db.get_page()
        if not page_data:
            # TODO: -> if not cached, run full annotation for the page
            data = self.revisions.get_revisions()
        
        #TODO: check if cached version match the live one
        wiki_page = self.wiki.get_page()
        # wiki_page.latest_revision_id == page_data.
        # local_db.get_page()


        #
        # -> if not, get delta

        pass

    def get_cached(self):

        pass


