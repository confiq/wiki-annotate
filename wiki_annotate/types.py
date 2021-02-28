from typing import List, Set, Dict, Tuple, Optional, Union


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
        l, _ = zip(*self.text)
        return ''.join(l)
