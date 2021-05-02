from wiki_annotate.utils import timing
from wiki_annotate.diff import DiffLogic
from wiki_annotate.utils import catchtime
import dataclasses
from wiki_annotate.wiki_siteapi import WikiAPI
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.types import AnnotationCharData, AnnotatedText, CachedRevision, UIRevision, APIPageData, SiteAPIRevisionStructure
import logging
import pywikibot

log = logging.getLogger(__name__)


class WikiPageAnnotation:

    def __init__(self, core):
        self.core = core

    @timing
    def get_annotation(self, cached_revision: Union[CachedRevision, None] = None) -> (AnnotatedText, SiteAPIRevisionStructure):
        """
        ugly workaround to get rvdir + startid
        this is instead of page.revisions(reverse=True, content=True) because we must use startid
        Still not decided if we should replace pywikibot for something more light and async
        :param cached_revision: object that was retrieved from cache
        :return:
        """
        annotated_text: AnnotatedText = {}
        previous_revision_id = 1
        first = True
        total_revisions = 0
        revision: SiteAPIRevisionStructure = None
        startid = 1 if not cached_revision else cached_revision.latest_revision.revid
        wiki_api: WikiAPI = self.core.wiki_api
        wiki_api.reset_timer()
        for revisions_batch in wiki_api.load_revisions(startid=startid):
            for idx, api_revision in enumerate(revisions_batch.revisions):
                total_revisions += 1
                # TODO: don't run on deleted revisions
                revision = SiteAPIRevisionStructure(**api_revision)
                log.debug(f"working on revision: {revision.revid}")
                if previous_revision_id > revision.revid:
                    log.error(f"order of revisions is wrong, old_rev={previous_revision_id}>new_rev={revision.revid}")
                # continue from cached revision
                if first:
                    first = False
                    if not cached_revision:
                        char_data = AnnotationCharData(**dataclasses.asdict(revision))
                        annotated_text = DiffLogic.init_text(revision.content, char_data)
                    else:
                        annotated_text = cached_revision.annotated_text
                    continue
                char_data = AnnotationCharData(**dataclasses.asdict(revision))
                diff = DiffLogic(revision.content, annotated_text)
                annotated_text = diff.run(char_data)
                previous_revision_id = revision.revid
                # TODO: process bar?
                # TODO: random save with config.CHANCE_SAVE_RANDOM_REVISION with async function
        log.info(f"annotation done! total chars: '{len(annotated_text)}' with total '{total_revisions}' revisions")
        return annotated_text, revision

    @timing
    def getUIRevisions(self, data: CachedRevision) -> Tuple[UIRevision]:
        """
        modify data to be UI friendly so frontend can read and print it.
        :rtype: tuple(UIRevision)
        """
        previous_char_data: AnnotationCharData = {}
        return_data: [UIRevision] = []
        buffered_word = ''
        buffered_line = []
        buffered_authors = []
        for annotated_text in data.annotated_text.text:
            buffered_authors.append(annotated_text[1]['user'])
            if annotated_text[0] == "\n":
                final_lines = buffered_line + [(buffered_word, previous_char_data)]
                return_data.append((UIRevision(users=buffered_authors, annotated_text=final_lines)))
                buffered_authors = []
                buffered_line = []
                buffered_word = ''
            elif not buffered_word or annotated_text[1]['revid'] == previous_char_data['revid']:
                buffered_word += annotated_text[0]
                previous_char_data = annotated_text[1]
            else:
                buffered_line.append((buffered_word, previous_char_data))
                buffered_word = annotated_text[0]
                previous_char_data = annotated_text[1]

        if buffered_word:
            final_lines = buffered_line + [(buffered_word, previous_char_data)]
            return_data.append((UIRevision(users=buffered_authors, annotated_text=final_lines)))
        return tuple(return_data)
