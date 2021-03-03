import logging
from wiki_annotate.wiki import Wiki

log = logging.getLogger(__name__)


class Annotate:
    wiki: Wiki

    def __init__(self, url: str):
        """
        :param url: full URL of page that should be annotated
        """
        self.wiki = Wiki(url)

    def run(self):
        # get cached
        
        # -> if not cached, run full annotation for the page
        # check if cached version match the live one
        # -> if not, get delta

        pass

    def get_cached(self):

        pass


