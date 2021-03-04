from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.types import CachedRevision


class AbstractDB(ABC):
    @abstractmethod
    def get_page_data(self, wikiid: str, page: str, revision: Optional[Union[int, str]]) -> Union[None, CachedRevision]:
        pass

    @abstractmethod
    def save_page_data(self, wikiid: str, page: str, obj: object, revision: int) -> bool: pass
