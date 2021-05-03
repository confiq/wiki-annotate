from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.types import CachedRevision
import unicodedata
import re


class AbstractDB(ABC):
    @abstractmethod
    def get_page_data(self, wikiid: str, page: str, revision: Optional[Union[int, str]]) -> Union[None, CachedRevision]:
        pass

    @abstractmethod
    def save_page_data(self, wikiid: str, page: str, obj: object, revision: int) -> bool: pass

    @staticmethod
    def slugify(value, allow_unicode=False):
        """
        Taken from https://github.com/django/django/blob/master/django/utils/text.py
        Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
        dashes to single dashes. Remove characters that aren't alphanumerics,
        underscores, or hyphens. Convert to lowercase. Also strip leading and
        trailing whitespace, dashes, and underscores.
        """
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '-', value).strip('-_')