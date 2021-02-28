from typing import List, Set, Dict, Tuple, Optional, Union
import pprint
from enum import Enum
from dataclasses import dataclass


class AnnotationCharData:
    def __init__(self, revision: Union[str, int], user: str):
        self.USER = user
        self.REVISION = revision

    def __repr__(self):
        return f"AnnotationCharData(revision='{self.REVISION}') at {hex(id(self))}"


class AnnotatedText:
    def __init__(self, text: Tuple[Tuple[str, AnnotationCharData]]):
        self.text = text

    @property
    def clear_text(self) -> str:
        l, _ = zip(*self.text)
        return ''.join(l)
