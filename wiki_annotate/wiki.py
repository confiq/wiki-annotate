import pywikibot
from urllib.parse import urlparse
from wiki_annotate.types import AnnotationCharData, AnnotatedText
from wiki_annotate.diff import DiffLogic
from wiki_annotate.utils import catchtime
import logging
import wiki_annotate.config as config
from typing import List, Set, Dict, Tuple, Optional, Union
# from wiki_annotate.core import Annotate

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
                raise NotImplementedError(f"Can't parse domain {domain}")
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


class WikiRevision:  # should we rename to WikiPageAnnotation ? WikiAnnotateGenerate

    def __init__(self, annotate):
        self.annotate = annotate

    def get_annotation(self, from_revision_id=1) -> AnnotatedText:
        annotated_text: AnnotatedText = {}
        previous_revision_id = 1
        # TODO:
        #  ugly workaround to get rvdir + startid
        #  this is instead of page.revisions(reverse=True, content=True) because we must use startid
        #  Still not decided if we should replace pywikibot for something more light and async
        page: pywikibot.Page = self.annotate.wiki.get_page()
        page._revisions = {}  # clear cache
        with catchtime() as t:
            page.site.loadrevisions(page, content=True, rvdir=True, startid=from_revision_id)
        log.debug(f"API call: {t():.4f} secs")

        log.debug('getting revisions from API')
        # TODO: use async and batches. pywikibot does not return generator. We could use async + annotation simultaneously
        for idx, revid in enumerate(sorted(page._revisions)):
            log.debug(f"working on revision: {page._revisions[revid].revid}")
            if previous_revision_id > page._revisions[revid].revid:
                log.warning(f"order of revisions is wrong, old_rev={previous_revision_id}>new_rev={page._revisions[revid].revid}")
            # TODO: don't run on deleted revisions
            if idx == 0:
                annotation_data = AnnotationCharData(**page._revisions[revid])
                annotated_text = DiffLogic.create_text(page._revisions[revid].text, annotation_data)
                continue
            annotation_data = AnnotationCharData(**page._revisions[revid])
            diff = DiffLogic(page._revisions[revid].text, annotated_text)
            annotated_text = diff.run(annotation_data)
            previous_revision_id = page._revisions[revid].revid
            # TODO: process bar?
            # TODO: random save with config.CHANCE_SAVE_RANDOM_REVISION with async function
        log.info(f"annotation done! total chars: '{len(annotated_text)}' with total '{idx+1}' revisions")
        return annotated_text
