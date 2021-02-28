from typing import Tuple

from wiki_annotate.types import AnnotatedText, AnnotationCharData
import diff_match_patch as dmp_module


class WikiAnnotate:
    new_revision_text: str

    def __init__(self, new_revision_text: str, previous_annotation: AnnotatedText):
        self.new_revision_text = new_revision_text
        self.previous_annotation = previous_annotation

    @staticmethod
    def create_text(text: str, annotated_char_data: AnnotationCharData) -> AnnotatedText:
        return AnnotatedText(tuple((letter, annotated_char_data) for letter in text))

    def run(self):
        # TODO: run diff
        dmp = dmp_module.diff_match_patch()
        diff = dmp.diff_main(self.previous_annotation.clear_text, self.new_revision_text)
        dmp.diff_
        # TODO: run through each letter in self.text and compare it with diff
        return diff
        pass
