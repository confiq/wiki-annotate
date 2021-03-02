import pywikibot
from urllib.parse import urlparse
from wiki_annotate.db.file_system import FileSystem


class Wiki:
    DB_DRIVER: FileSystem

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

    def get_page(self, page: str) -> pywikibot.Page:
        return pywikibot.Page(self.site, page)

