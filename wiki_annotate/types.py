from typing import List, Set, Dict, Tuple, Optional, Union
import logging
from pywikibot.page._revision import Revision
import json
from dataclasses import dataclass

log = logging.getLogger(__name__)


@dataclass
class AnnotationCharData:
    revision: Union[str, int]
    user: str


@dataclass
class AnnotatedText:
    text: Tuple[Tuple[str, AnnotationCharData]]
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
class RevisionData:
    revision: Revision

    @property
    def id(self):
        return self.revision.get('revid')

    def to_json(self) -> str:
        return json.dumps(self.revision, default=lambda o: o.__dict__['_data'], sort_keys=True)


@dataclass
class CachedRevision:
    annotated_text: AnnotatedText
    revision_data: RevisionData