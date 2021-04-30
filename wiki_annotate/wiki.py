import pywikibot
from urllib.parse import urlparse, parse_qs
from wiki_annotate.types import AnnotationCharData, AnnotatedText, CachedRevision, UIRevision, APIPageData
import logging
from typing import List, Set, Dict, Tuple, Optional, Union
import re
import functools

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
            self._site = pywikibot.Site(url=self.url)
        return self._site

    @functools.cached_property  # ❤️ >=3.8
    def page_name(self) -> str:
        """
        based on: https://www.mediawiki.org/w/index.php?title=Manual:Short_URL/wiki/Page_Title_--_.htaccess
        it's little reverse engineering how to get page_name because it seems pywikibot does not have it
        :return: str
        """
        url = urlparse(self.url)
        page_name = None
        if url.path.startswith('/wiki/') and len(url.path) > 6:
            page_name = url.path[6:]
        elif url.path == '/w/index.php' and url.query and 'title' in parse_qs(url.query):
            page_name = url.query['title'][0]
        elif url.path in ['/wiki/', 'w/index.php']:
            # we try to get name of homepage but the challenge is, each wiki-family/lang had different name for homepage
            page_name = self.site.siteinfo()['mainpage']
        return page_name

    def get_page(self, page: Optional[str] = None) -> pywikibot.Page:
        if not page:
            page = self.page_name
        return pywikibot.Page(self.site, page)


class WikiPageAPI(Wiki):
    WIKI_ROOT_DOMAIN = 'org'
    DOMAIN_REGEX = r"(https?://)?(.+(?<=\.))(\w+)([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?"

    def __init__(self, url: str):
        super().__init__(self.get_wikipedia_url(url))

    def get_wikipedia_url(self, url):
        """
        always return wiki-family domain from any url. Ex: https://en.wikipedia.red/wiki/Annotation will turn into
        https://en.wikipedia.org/wiki/Annotation
        :return: string
        """
        result = re.sub(self.DOMAIN_REGEX, r"\1\2" + self.WIKI_ROOT_DOMAIN + r"\4", url)
        return result

    def get_page_data(self) -> APIPageData:
        page_data = APIPageData(is_error=False)
        if not self.page_name:
            page_data.is_error = True
            page_data.add_error_msg('Could not find title for this page')
            return page_data
        else:
            page_data.page_title = self.page_name
        return page_data
