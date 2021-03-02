from typing import Tuple, List, Any, Union

from wiki_annotate.types import AnnotatedText, AnnotationCharData
from wiki_annotate.exceptions import DiffInsertionException
import diff_match_patch as dmp_module

# TODO: Make locking system, not sure it should be here but we must have lock in place


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
        try:
            dmp = dmp_module.diff_match_patch()
            diffs = dmp.diff_main(self.previous_annotation.clear_text, self.new_revision_text)
            dmp.diff_cleanupSemantic(diffs)
        except ValueError as e:
            raise DiffInsertionException(f'DMP returned the error "{e}"', self)

        return_text: list[tuple] = []
        for diff in diffs:
            if diff[0] == dmp.DIFF_EQUAL:
                return_text.append(tuple(self._append_equal(diff[1])))
                self.pointer += len(diff[1])
            elif diff[0] == dmp.DIFF_DELETE:
                self.pointer += len(diff[1])
            elif diff[0] == dmp.DIFF_INSERT:
                return_text.append(tuple((letter, new_annotation) for letter in diff[1]))
            else:
                raise NotImplemented(f"We don't know about DIFF of type '{diff[0]}'")
        merged: Tuple[Tuple[str, AnnotationCharData]] = tuple(i for sub in return_text for i in sub)
        # TODO: check if pointer is at the end of file?
        return AnnotatedText(merged)

    def _append_equal(self, text: str):
        return_data = []
        for idx, letter in enumerate(text):
            pointer = self.pointer + idx
            return_data.append((letter, self.previous_annotation[pointer][1]))
            if letter != self.previous_annotation[pointer][0]:
                raise DiffInsertionException('Our previous annotation data does not match with dmp library diff. '  # this should never happen
                                             'This is probably a result of old bad annotation revisions.', self)
        return return_data
