import pywikibot
from urllib.parse import urlparse
from wiki_annotate.types import AnnotationCharData, AnnotatedText
from wiki_annotate.diff import DiffLogic
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
        page: pywikibot.Page = self.annotate.wiki.get_page()
        site: pywikibot.Site = page.site
        log.debug('getting revisions from API')
        # TODO:
        #  ugly workaround to get rvdir + startid
        #  this is instead of page.revisions(reverse=True, content=True) because we must use startid
        #  Still not decided if we should replace pywikibot for something more light
        site.loadrevisions(page, content=True, rvdir=True, startid=from_revision_id)
        # TODO: use async and batches. pywikibot does not return generator. We could use async + annotation simultaneously
        for idx, wiki_revision in enumerate(page._revisions):
            log.debug(f"working on revision: {page._revisions[wiki_revision].revid}")
            # TODO: don't run on deleted revisions
            if idx == 0:
                annotation_data = AnnotationCharData(**page._revisions[wiki_revision])
                annotated_text = DiffLogic.create_text(page._revisions[wiki_revision].text, annotation_data)
                continue
            annotation_data = AnnotationCharData(**page._revisions[wiki_revision])
            diff = DiffLogic(page._revisions[wiki_revision].text, annotated_text)
            annotated_text = diff.run(annotation_data)
            if page._revisions[wiki_revision].revid == 6945969:
                log.warning('breaking the loop at revid 6945969')
                break
            # TODO: process bar?
            # TODO: random save with config.CHANCE_SAVE_RANDOM_REVISION with async function
        log.info(f"annotation done! total chars: '{len(annotated_text)}' with total '{idx+1}' revisions")
        return annotated_text
