from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.types import WikiRevision


class AbstractDB(ABC):
    @abstractmethod
    def get_page_data(self, wikiid: str, page: str, revision: Optional[Union[int, str]]) -> Union[None, WikiRevision]:
        pass
