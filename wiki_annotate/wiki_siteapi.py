import json

from wiki_annotate import config
from dataclasses import dataclass, field
from typing import Generator, Iterator
from wiki_annotate.exceptions import WikiAPIException
from wiki_annotate.types import SiteAPIRevisions
import functools
import requests
import time
import logging

log = logging.getLogger(__name__)

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class WikiAPI:

    TOTAL_CPU_TIME = 50
    TOTAL_TIME = 60
    COUNT = 0

    def __init__(self, core):
        self.cpu_timer: float = 0
        self.total_time: float = 0
        self.core = core

    def load_revisions(self, startid=1) -> Iterator[SiteAPIRevisions]:
        """
        @see: U{https://www.mediawiki.org/wiki/API:Revisions}
        :param startid:
        :return:
        """
        self.reset_timer()
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": self.core.wiki.get_page().title(),
            "rvprop": "ids|timestamp|user|userid|comment|content",
            "rvstartid": startid,
            "rvdir": "newer",
            "formatversion": "2",
            "rvslots": "main",
            "rvlimit": "max",
            "format": "json"
        }

        while self.should_continue():
            self.COUNT += 1
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
        self.cpu_timer = time.process_time()
        self.total_time = time.time()

    def should_continue(self):
        if config.RUN_ONLY_ONE_PATCH_PROCESS and self.COUNT > 0:
            log.debug("config.RUN_ONLY_ONE_PATCH_PROCESS: True, running only one loop")
            return False
        elif config.DISABLE_BATCH_PROCESS:
            return True
        elif self.cpu_timer + self.TOTAL_CPU_TIME <= time.process_time():
            log.debug('CPU Time exhausted '+str(time.process_time()))
            return False
        elif self.total_time + self.TOTAL_TIME <= time.time():
            log.debug('Total time exhausted')
            return False
        else:
            return True

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


