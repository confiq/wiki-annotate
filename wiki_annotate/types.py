from typing import List, Set, Dict, Tuple, Optional, Union
import pprint
from enum import Enum
from dataclasses import dataclass


class AnnotationCharData:
    def __init__(self, revision: Union[str, int], user: str):
        self.USER = user
        self.REVISION = revision



class AnnotatedText:
    def __init__(self, text: List[AnnotationCharData]):
        self.text = text

    def __str__(self):
        return pprint.pprint(self.text)
