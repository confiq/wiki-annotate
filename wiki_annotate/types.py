from typing import List, Set, Dict, Tuple, Optional, Union
import logging
from pywikibot.page._revision import Revision
import json

log = logging.getLogger(__name__)


class AnnotationCharData:
    """
    Structured data about the written char
    """
    def __init__(self, revision: Union[str, int], user: str):
        self.USER = user
        self.REVISION = revision

    def __repr__(self):
        return f"AnnotationCharData(revision='{self.REVISION}') at {hex(id(self))}"


class AnnotatedText:
    """
    Annotated text that is fully historically generated
    """
    def __init__(self, text: Tuple[Tuple[str, AnnotationCharData]]):
        self.text = text

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


class RevisionData:
    def __init__(self, revision: Revision):
        self.revision = revision

    @property
    def id(self):
        return self.revision.get('revid')

    def to_json(self) -> str:
        return json.dumps(self.revision, default=lambda o: o.__dict__['_data'], sort_keys=True)


class CachedRevision:
    def __init__(self, annotated_text: AnnotatedText, revision_data: RevisionData):
        """
        structure for how CachedRevision data should look like
        :param annotated_text:
        :param revision_data:
        """
        self.annotated_text = annotated_text
        self.revision_data = revision_data

    def encode(self):
        pass

    def decode(self):
        pass