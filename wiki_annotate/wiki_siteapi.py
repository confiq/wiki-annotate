import functools
import requests

class WikiAPI:
    def __init__(self, core):
        self.core = core

    def load_revisions(self, content=False, rvdir='newer', startid=1):
        """
        @see: U{https://www.mediawiki.org/wiki/API:Revisions}
        :param content:
        :param rvdir:
        :param startid:
        :return:
        """

        url = self.api_url
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": self.core.wiki.get_page().title(),
            "rvprop": "ids|timestamp|user|userid|comment|content",
            "rvslots": "main",
            "rvstartid": startid,
            "rvdir": rvdir,
            "formatversion": "2",
            "rvslots": "main",
            "rvlimit": "max",
            "format": "json"
        }
        data = requests.get(url, params)
        return data

    @functools.cached_property
    def api_url(self):
        code = self.core.wiki.site.code
        family = self.core.wiki.site.family
        return f"{family.protocol(code)}://{family.hostname(code)}{family.apipath(code)}"
