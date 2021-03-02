import argparse
from argparse import Namespace
from wiki_annotate.wiki import Wiki
from wiki_annotate.db.file_system import FileSystem
from wiki_annotate.diffInsertion import DiffInsertion, AnnotationCharData
import logging
import pprint
from IPython import embed


def main(args: Namespace):
    # parse page/lang/latest_revision
    # check if latest revision matches the DB
    # if not, generate latest page
    wiki = Wiki(url=args.domain)
    page = wiki.get_page(args.page)
    # TODO: make class Revisions  that will use the driver instead of directly calling it
    revision = FileSystem().get_page_data(wiki.wikiid, page.title(), page.latest_revision_id)

    # this means we don't have revision for this page, lets generate
    if not revision:
        for idx, wiki_revision in enumerate(page.revisions(reverse=True, content=True)):
            if idx == 0:
                annotation_data = AnnotationCharData(revision=wiki_revision.revid, user=wiki_revision.user)
                previous_diff = DiffInsertion.create_text(wiki_revision.text, annotation_data)
                continue
            annotation_data = AnnotationCharData(revision=wiki_revision.revid, user=wiki_revision.user)
            diff = DiffInsertion(wiki_revision.text, previous_diff)
            previous_diff = diff.run(annotation_data)
    print(pprint.pprint([f for f in previous_diff]))



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get full annotation of wiki page')
    parser.add_argument('-d', dest='domain', action='store', default='https://test.wikipedia.org/',
                        help='Wiki domain to use', type=str)
    parser.add_argument('-p', dest='page', action='store', default='demo',
                        help='Wiki page to use', type=str)
    parser.add_argument("-v", "--verbose", help="modify output verbosity", action='count', default=0)

    main(parser.parse_args())
