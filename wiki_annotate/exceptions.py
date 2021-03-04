from wiki_annotate.types import AnnotatedText, AnnotationCharData
import pprint
# exceptions
class WikiException(Exception):pass


class AnnotatedTextException(WikiException):
    """ Exceptions when we have AnnotatedText """
    def __init__(self, message, annotated_text: AnnotatedText):
        self.message = message
        self.annotated_text = AnnotatedText

    def __str__(self):
        party_text = []
        # TODO: make better errors
        return f"""{self.message}: TODO"""


class DiffLogicException(WikiException):
    def __init__(self, message, diff_insertion_object=object):
        self.message = message
        self.diff_insertion_object = diff_insertion_object

    def __str__(self):
        return f"{self.message}. Pointer is at '{self.diff_insertion_object.pointer}' previous_annotation: " \
               f"{self.diff_insertion_object.previous_annotation} new_revision_text: '{self.diff_insertion_object.new_revision_text}"
