import pywikibot
from urllib.parse import urlparse


class Wiki:
    def __init__(self, url: str):
        self.url = url
        self._site = None
        self._siteinfo = None

    @property
    def site(self) -> pywikibot.Site:
        if not self._site:
            domain = urlparse(self.url).netloc
            domain_split = domain.split('.')
            if len(domain_split) != 3:
                raise NotImplemented(f"Can't parse domain {domain}")
            self._site = pywikibot.Site(domain_split[0], domain_split[1])
            self._siteinfo = self._site.siteinfo()
        return self._site

