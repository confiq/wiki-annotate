import pywikibot
from urllib.parse import urlparse
from wiki_annotate.db.file_system import FileSystem
import logging
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.core import Annotate
log = logging.getLogger(__name__)


class Wiki:
    def __init__(self, url: str):
        self.url: str = url
        self._site: str = None
        self._wikiid: str = None

    @property
    def wikiid(self) -> str:
        if not self._wikiid:
            self._wikiid = f"{self.site.lang}-{self.site.code}-{self.site.family.name}"
        return self._wikiid

    @property
    def site(self) -> pywikibot.Site:
        if not self._site:
            domain = urlparse(self.url).netloc
            domain_split = domain.split('.')
            if len(domain_split) != 3:
                raise NotImplemented(f"Can't parse domain {domain}")
            self._site = pywikibot.Site(domain_split[0], domain_split[1])
        return self._site

    @property
    def page_name(self):
        # TODO: get if page is in params, it should be something like ?page=Demo
        path = urlparse(self.url).path
        return path.split('/')[2]

    def get_page(self, page: Optional[str] = None) -> pywikibot.Page:
        if not page:
            page = self.page_name
        return pywikibot.Page(self.site, page)


class WikiRevision:
    def __init__(self, annotate: Annotate):
        self.annotate = annotate
        pass

    def get_revisions(self, from_revision_id=None):
        page = self.annotate.wiki.get_page()
        revisions = page.revisions(reverse=True, content=True)
        first = True
        for revision in revisions:
            if first:
                




