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
        for text in xte

        return f"""{self.message}: full AnnotatedText is """
