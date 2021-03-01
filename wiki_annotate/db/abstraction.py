from abc import ABC, abstractmethod
from typing import List, Set, Dict, Tuple, Optional, Union
from wiki_annotate.types import WikiPage


class AbstractDB(ABC):
    @abstractmethod
    def get_page_data(self, domain: str, page: str, revision: Optional[Union[int, str]]) -> Union[None, WikiPage]:
        pass
