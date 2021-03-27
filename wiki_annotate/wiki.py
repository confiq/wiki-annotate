import pywikibot
from urllib.parse import urlparse, parse_qs
from wiki_annotate.types import AnnotationCharData, AnnotatedText, CachedRevision, UIRevision, APIPageData
from wiki_annotate.diff import DiffLogic
from wiki_annotate.utils import catchtime
import logging
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.utils import timing
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


class WikiPageAnnotation:

    def __init__(self, annotate):
        self.annotate = annotate

    @timing
    def get_annotation(self, old_revision: Union[CachedRevision, None] = None) -> AnnotatedText:
        """
        ugly workaround to get rvdir + startid
        this is instead of page.revisions(reverse=True, content=True) because we must use startid
        Still not decided if we should replace pywikibot for something more light and async
        :param old_revision:
        :return:
        """
        annotated_text: AnnotatedText = {}
        previous_revision_id = 1
        page: pywikibot.Page = self.annotate.wiki.get_page()
        page._revisions = {}  # clear cache
        with catchtime() as t:
            from_revision_id = 0 if not old_revision else old_revision.latest_revision.id
            page.site.loadrevisions(page, content=True, rvdir=True, startid=from_revision_id)
        log.debug(f"API call page.site.loadrevisions: {t():.4f} secs")

        log.debug('getting revisions from API')
        # TODO: use async and batches. pywikibot does not return generator. We could use async + annotation simultaneously
        for idx, revid in enumerate(sorted(page._revisions)):
            log.debug(f"working on revision: {page._revisions[revid].revid}")
            if previous_revision_id > page._revisions[revid].revid:
                log.error(
                    f"order of revisions is wrong, old_rev={previous_revision_id}>new_rev={page._revisions[revid].revid}")
            # TODO: don't run on deleted revisions
            if idx == 0:
                if not old_revision:
                    annotation_data = AnnotationCharData(**page._revisions[revid])
                    annotated_text = DiffLogic.init_text(page._revisions[revid].text, annotation_data)
                else:
                    annotated_text = old_revision.annotated_text
                continue
            annotation_data = AnnotationCharData(**page._revisions[revid])
            diff = DiffLogic(page._revisions[revid].text, annotated_text)
            annotated_text = diff.run(annotation_data)
            previous_revision_id = page._revisions[revid].revid
            # TODO: process bar?
            # TODO: random save with config.CHANCE_SAVE_RANDOM_REVISION with async function
        log.info(f"annotation done! total chars: '{len(annotated_text)}' with total '{idx + 1}' revisions")
        return annotated_text

    @timing
    def getUIRevisions(self, data: CachedRevision) -> Tuple[UIRevision]:
        """
        modify data to be UI friendly so normal users can read it.
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
                buffered_line_line = buffered_line + [(buffered_word, previous_char_data)]
                return_data.append((UIRevision(users=buffered_authors, annotated_text=buffered_line_line)))
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
            return_data.append((UIRevision(users=buffered_authors, annotated_text=buffered_line)))
        return tuple(return_data)
