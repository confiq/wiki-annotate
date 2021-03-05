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


class WikiRevision:

    def __init__(self, annotate):
        self.annotate = annotate

    def get_annotation(self, from_revision_id=1) -> AnnotatedText:
        # TODO: use from_revision_id args!
        page = self.annotate.wiki.get_page()
        revisions = page.revisions(reverse=True, content=True)
        annotated_text: AnnotatedText = AnnotatedText
        # TODO: use async and batches. pywikibot does not return generator. We could use async + annotation simultaneously
        # this will probably not work with big pages
        for idx, wiki_revision in enumerate(revisions):
            # TODO: don't run on deleted revisions
            if idx == 0:
                annotation_data = AnnotationCharData(*wiki_revision)
                annotated_text = DiffLogic.create_text(wiki_revision.text, annotation_data)
                continue
            annotation_data = AnnotationCharData(*wiki_revision)
            diff = DiffLogic(wiki_revision.text, annotated_text)
            annotated_text = diff.run(annotation_data)
            # TODO: process bar?
            # TODO: random save with config.CHANCE_SAVE_RANDOM_REVISION with async function
        return annotated_text
