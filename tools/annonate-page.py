import argparse
from argparse import Namespace
from wiki_annotate.wiki import Wiki
from wiki_annotate.db.file_system import FileSystem
from wiki_annotate.diffInsertion import DiffInsertion, AnnotationCharData
from wiki_annotate.core import Annotate
import logging
import pprint
from IPython import embed


def main(args: Namespace):
    annotate = Annotate(url=args.url)
    foo = annotate.run()
    embed()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get full annotation of wiki page')
    parser.add_argument('-u', dest='url', action='store', default='https://test.wikipedia.org/wiki/Demo',
                        help='Full URL to annotate', type=str)
    parser.add_argument("-v", "--verbose", help="modify output verbosity", action='count', default=0)
    args = parser.parse_args()

    main(args)
