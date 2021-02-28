from wiki_annotate.types import AnnotatedText, AnnotationCharData


class WikiAnnotate:
    def __init__(self, text: str, previous_annotation: AnnotatedText):
        self.text = text,
        self.previous_annotation = previous_annotation

    @staticmethod
    def create_text(text: str, annotated_char_data: AnnotationCharData) -> AnnotatedText:
        return AnnotatedText(tuple((letter, annotated_char_data) for letter in text))
