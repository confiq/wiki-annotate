from typing import Tuple

from wiki_annotate.types import AnnotatedText, AnnotationCharData
import diff_match_patch as dmp_module


class DiffInsertion:
    new_revision_text: str

    def __init__(self, new_revision_text: str, previous_annotation: AnnotatedText) -> None:
        self.new_revision_text = new_revision_text
        self.previous_annotation = previous_annotation

    @staticmethod
    def create_text(text: str, annotated_char_data: AnnotationCharData) -> AnnotatedText:
        return AnnotatedText(tuple((letter, annotated_char_data) for letter in text))

    def run(self, new_annotation: AnnotationCharData) -> AnnotatedText:
        dmp = dmp_module.diff_match_patch()
        diffs = dmp.diff_main(self.previous_annotation.clear_text, self.new_revision_text)
        dmp.diff_cleanupSemantic(diffs)
        pointer = 0
        return_text = []
        for diff in diffs:
            if diff[0] == dmp.DIFF_EQUAL:
                # move pointer to len of the len(diff[1])
                return_text.append(self._append_equal(pointer, diff[1]))
                pointer += len(diff[1])
            elif diff[0] == dmp.DIFF_DELETE:
                # move pointer to len of the len(diff[1])
                pass
            elif diff[0] == dmp.DIFF_INSERT:
                # move data from new_annotation to return_text
                pass
            else:
                raise NotImplemented(f"We don't know about DIFF of type '{diff[0]}'")

    def _append_equal(self, pointer: int, text: str):
        return_data = []
        for idx, letter in enumerate(text):
            return_data.append((letter, self.previous_annotation[idx + pointer][1]))
            #TODO, throw human reading error
        return return_data
