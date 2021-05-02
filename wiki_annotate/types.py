import logging
from typing import List, Set, Dict, Tuple, Optional, Union
from collections.abc import Mapping
from dataclasses import dataclass, field
import datetime
log = logging.getLogger(__name__)


@dataclass
class AnnotationCharData:
    revid: Union[str, int]
    user: str

    def __init__(self, revid, user, **args):
        """
        each char has specific values and these values are declared here
        :param revid: revision ID
        :param user: user that wrote this specific char
        :param args: the throw revision object here and pick only params that we want to save
        """
        self.revid = revid
        self.user = user

    def __getitem__(self, item):
        return getattr(self, item)


@dataclass
class RevisionData:
    """
    mainly data structure from pywikibot.page._revision.Revision
    """
    revision: Mapping

    @property
    def id(self):
        return self.revision.get('revid')


@dataclass
class AnnotatedText:
    text: Tuple[(str, AnnotationCharData)]
    """
    Annotated text that is fully historically generated
    """

    def __getitem__(self, item):
        return self.text[item]

    def __len__(self):
        return len(self.text)

    def __iter__(self):
        return self.text.__iter__()

    @property
    def clear_text(self) -> str:
        """
        get clear text of Annotation
        # TODO: run profile and check if this is expensive or not! If yes, send full text within __init__
        :return: clear text
        """
        if len(self.text) == 0:
            log.warning('Got length of 0 chars')
            return ''
        l, _ = zip(*self.text)
        return ''.join(l)


@dataclass
class SiteAPIRevisionStructure:
    """
    wikipedia returns json like this:
    revisions":[
       {
          "revid":467883,
          "parentid":0,
          "user":"CONFIQ",
          "userid":49399,
          "timestamp":"2021-02-27T17:16:58Z",
          "slots":{
             "main":{
                "contentmodel":"wikitext",
                "contentformat":"text/x-wiki",
                "content":"demo1"
             }
          },
          "comment":"Created page with \"demo1\""
       }
    """
    revid: int
    user: str
    userid: int
    timestamp: str  # TODO: datetime, does not work out of box
    comment: str
    content: str

    def __init__(self, content=None, **kwargs):
        self.revid = kwargs.get('revid')
        self.user = kwargs.get('user')
        self.userid = kwargs.get('userid')
        self.timestamp = kwargs.get('timestamp')
        self.comment = kwargs.get('comment')
        self.content = kwargs.get('slots')['main']['content'] if not content else content


@dataclass
class CachedRevision:
    annotated_text: AnnotatedText
    latest_revision: SiteAPIRevisionStructure


@dataclass
class UIRevision:
    users: []
    annotated_text: AnnotatedText

    def __init__(self, users: list, annotated_text: AnnotatedText):
        self.users = set(users)
        self.annotated_text = annotated_text


@dataclass
class APIPageData:
    is_error: bool = False
    errors_messages: List[str] = field(default_factory=lambda: [])  # why lambda? https://stackoverflow.com/q/52063759/1477764
    page_title: str = ''
    # language: str = ''
    # wiki_language: str = ''
    # wiki_more_languages: list = ''
    # cached_revid: Union[int, None] = None
    # refresh_needed: bool = False

    def add_error_msg(self, msg: str):
        self.errors_messages.append(msg)


@dataclass
class APIAnnotate:
    text: Tuple[UIRevision]
    need_refresh: bool = False  # TODO: we need to make batching process


