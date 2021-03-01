from typing import Tuple

from wiki_annotate.types import AnnotatedText, AnnotationCharData
from wiki_annotate.exceptions import DiffInsertionException
import diff_match_patch as dmp_module


class DiffInsertion:
    new_revision_text: str

    def __init__(self, new_revision_text: str, previous_annotation: AnnotatedText) -> None:
        self.new_revision_text = new_revision_text
        self.previous_annotation = previous_annotation
        self.pointer = 0

    @staticmethod
    def create_text(text: str, annotated_char_data: AnnotationCharData) -> AnnotatedText:
        return AnnotatedText(tuple((letter, annotated_char_data) for letter in text))

    def run(self, new_annotation: AnnotationCharData) -> AnnotatedText:
        dmp = dmp_module.diff_match_patch()
        diffs = dmp.diff_main(self.previous_annotation.clear_text, self.new_revision_text)
        dmp.diff_cleanupSemantic(diffs)

        return_text = []
        for diff in diffs:
            if diff[0] == dmp.DIFF_EQUAL:
                return_text.append(self._append_equal(diff[1]))
            elif diff[0] == dmp.DIFF_DELETE:
                pass
            elif diff[0] == dmp.DIFF_INSERT:
                return_text.append(tuple((letter, new_annotation) for letter in diff[1]))
                pass
            else:
                raise NotImplemented(f"We don't know about DIFF of type '{diff[0]}'")
            self.pointer += len(diff[1])
        return tuple(return_text)


    def _append_insert(self, text: str, new_annotation: AnnotationCharData):
        return_data = []
        for idx, letter in enumerate(text):
            return_data.append((letter, new_annotation))
        return return_data

    def _append_equal(self, text: str):
        return_data = []
        for idx, letter in enumerate(text):
            pointer = self.pointer + idx
            return_data.append((letter, self.previous_annotation[pointer][1]))
            if letter != self.previous_annotation[pointer][0]:
                raise DiffInsertionException('Our previous annotation data does not match with dmp library diff. '  # this should never happen
                                             'This is probably a result of old bad annotation revisions.')
        return return_data
