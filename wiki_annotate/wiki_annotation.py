from wiki_annotate.utils import timing
from wiki_annotate.diff import DiffLogic
from wiki_annotate.utils import catchtime
import dataclasses
import asyncio
from wiki_annotate.wiki_siteapi import WikiAPI
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.types import AnnotationCharData, AnnotatedText, CachedRevision, UIRevision, APIPageData, SiteAPIRevisionStructure
import logging
import pywikibot

log = logging.getLogger(__name__)


class WikiPageAnnotation:

    def __init__(self, core):
        self.core = core
        self.text: AnnotatedText = {}

    @timing
    def get_annotation(self, cached_revision: Union[CachedRevision, None] = None) -> (AnnotatedText, SiteAPIRevisionStructure):
        """

        :param cached_revision: object that was retrieved from cache
        :return:
        """
        previous_revision_id = 1
        first = True
        total_revisions = 0
        revision: SiteAPIRevisionStructure = None
        startid = 1 if not cached_revision else cached_revision.latest_revision.revid
        wiki_api: WikiAPI = self.core.wiki_api

        loop = asyncio.get_event_loop()
        queue = asyncio.Queue()
        task = loop.create_task(self.annotate_text(queue))

        for revisions_batch in wiki_api.load_revisions(startid=startid):
            for idx, api_revision in enumerate(revisions_batch.revisions):
                total_revisions += 1
                # TODO: don't run on deleted revisions
                revision = SiteAPIRevisionStructure(**api_revision)
                if previous_revision_id > revision.revid:
                    log.error(f"order of revisions are wrong, old_rev={previous_revision_id}>new_rev={revision.revid}")
                # continue from cached revision
                if first:
                    first = False
                    if not cached_revision:
                        char_data = AnnotationCharData(**dataclasses.asdict(revision))
                        self.text = DiffLogic.init_text(revision.content, char_data)
                    else:
                        self.text = cached_revision.annotated_text
                    continue
                loop.run_until_complete(queue.put(revision))
                previous_revision_id = revision.revid
                # TODO: process bar?
        loop.run_until_complete(queue.put(False))
        loop.run_until_complete(task)
        log.info(f"annotation done! total chars: '{len(self.text)}' with total '{total_revisions}' revisions")

        return self.text, revision

    async def annotate_text(self, queue):
        while True:
            revision = await queue.get()
            if revision is False:
                return
            log.debug(f"working on revision: {revision.revid}")
            char_data = AnnotationCharData(**dataclasses.asdict(revision))
            diff = DiffLogic(revision.content, self.text)
            self.text = diff.run(char_data)
            queue.task_done()

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
