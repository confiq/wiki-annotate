import pywikibot
from urllib.parse import urlparse
from wiki_annotate.types import AnnotationCharData, AnnotatedText
from wiki_annotate.diffInsertion import DiffInsertion
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

    def __init__(self, annotate):
        self.annotate = annotate

    def get_annotation(self, from_revision_id=None) -> Tuple[AnnotatedText, int]:
        # TODO: use from_revision_id args
        page = self.annotate.wiki.get_page()
        revisions = page.revisions(reverse=True, content=True)
        annotated_text: AnnotatedText = AnnotatedText
        last_revision = 0
        # TODO: use async and batches. pywikibot does not return real generator. We could use async + annotation simultaneously
        # this will probably not work with big pages
        for wiki_revision in revisions:
            # TODO: don't run on deleted revisions
            if last_revision == 0:
                annotation_data = AnnotationCharData(revision=wiki_revision.revid, user=wiki_revision.user)
                annotated_text = DiffInsertion.create_text(wiki_revision.text, annotation_data)
                last_revision = wiki_revision.revid
                continue
            annotation_data = AnnotationCharData(revision=wiki_revision.revid, user=wiki_revision.user)
            diff = DiffInsertion(wiki_revision.text, annotated_text)
            annotated_text = diff.run(annotation_data)
            last_revision = wiki_revision.revid
            # TODO: process bar?
            # TODO: random safe with config.CHANCE_SAVE_RANDOM_REVISION in async
        return annotated_text, last_revision

    def save_revision(self, annotated_text: AnnotatedText, revision_id: int):
        pass





