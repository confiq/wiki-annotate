import json

from wiki_annotate import config
from dataclasses import dataclass, field
from wiki_annotate.exceptions import WikiAPIException
import functools
import requests
import time
import logging

log = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class WikiAPI:

    BREAK_AFTER = config.BRAKE_BATCH_AFTER

    def __init__(self, core):
        self.timer_start: float = 0
        self.core = core

    def load_revisions(self, startid=1):
        """
        @see: U{https://www.mediawiki.org/wiki/API:Revisions}
        :param startid:
        :return:
        """

        params = {
            "action": "query",
            "prop": "revisions",
            "titles": self.core.wiki.get_page().title(),
            "rvprop": "ids|timestamp|user|userid|comment|content",
            "rvstartid": startid,
            "rvdir": "newer",
            "formatversion": "2",
            "rvslots": "main",
            # "rvlimit": "max",
            "rvlimit": "7",
            "format": "json"
        }

        while self.should_continue():
            api_data = self.request(params)
            data = SiteAPIRevisions(api_data)
            if data.batchcomplete:
                yield data
                break
            elif data.continue_from:
                params['rvstartid'] = data.continue_from
                yield data
            else:
                raise WikiAPIException('The API did not return expecting batch status. Full JSON response: '
                                       + json.dumps(data.data))
        else:
            log.debug('finish the loop without the break, could not load the whole batch of revisions')

    def reset_timer(self):
        self.timer_start = time.process_time()

    def should_continue(self):
        return True if self.timer_start + self.BREAK_AFTER >= time.process_time() else False

    def request(self, params):
        # TODO: retry on network issues
        log.debug('fetching data from API')
        data = requests.get(self.api_url, params)
        return data.json()

    @functools.cached_property
    def api_url(self):
        code = self.core.wiki.site.code
        family = self.core.wiki.site.family
        return f"{family.protocol(code)}://{family.hostname(code)}{family.apipath(code)}"


@dataclass
class SiteAPIRevisions:
    """
    wikipedia returns json like this:
    {
   "continue":{
      "rvcontinue":"20210308214123|468927",
      "continue":"||"
   },
   "query":{
      "pages":{
         "119047":{
            "pageid":119047,
            "ns":0,
            "title":"Demo",
            revisions":[]
         }
      }
   }
}
    """
    def __init__(self, data):
        self.data = data

    @property
    def revisions(self):
        return self.data['query']['pages'][0]['revisions']

    @property
    def continue_from(self):
        if not self.batchcomplete and 'continue' in self.data:
            return self.data['continue']['rvcontinue'].split('|')[1]

    @property
    def batchcomplete(self):
        return True if 'batchcomplete' in self.data and self.data['batchcomplete'] else False

