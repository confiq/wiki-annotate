from typing import List, Set, Dict, Tuple, Optional, Union
import logging
from collections.abc import Mapping
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class AnnotationCharData:
    revid: Union[str, int]
    user: str

    def __init__(self, revid, user, **args):
        """
        pick which which keys to save in json file per char
        :param revid:
        :param user:
        :param args:
        """
        self.revid = revid
        self.user = user

    def __getitem__(self, item):
        return getattr(self, item)


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
class GroupedAnnotatedText:
    pass


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
class CachedRevision:
    annotated_text: AnnotatedText
    latest_revision: RevisionData
