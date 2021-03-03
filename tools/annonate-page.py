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
    title = page.title()
    latest_revision_id = page.latest_revision_id
    revision = FileSystem().get_page_data(wiki.wikiid, title, latest_revision_id)
    # this means we don't have revision for this page, lets generate
    if not revision:
        print('no revisions')
        #TODO: some revisions are deleted, do not count them!
        for idx, wiki_revision in enumerate(page.revisions(reverse=True, content=True)):

            folder = '/Users/confiq/tmp/wiki-annotate/wiki-page-data/stress-test/'
            with open(folder + str(wiki_revision.revid) + '.txt', 'w') as f:
                f.write(str(wiki_revision.text))
            if idx == 0:
                annotation_data = AnnotationCharData(revision=wiki_revision.revid, user=wiki_revision.user)
                previous_diff = DiffInsertion.create_text(wiki_revision.text, annotation_data)
                continue
            annotation_data = AnnotationCharData(revision=wiki_revision.revid, user=wiki_revision.user)
            diff = DiffInsertion(wiki_revision.text, previous_diff)
            previous_diff = diff.run(annotation_data)
            print('.', end='', flush=True)
    print(pprint.pprint([f for f in previous_diff]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get full annotation of wiki page')
    parser.add_argument('-d', dest='domain', action='store', default='https://test.wikipedia.org/',
                        help='Wiki domain to use', type=str)
    parser.add_argument('-p', dest='page', action='store', default='demo',
                        help='Wiki page to use', type=str)
    parser.add_argument("-v", "--verbose", help="modify output verbosity", action='count', default=0)
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING,
                        format='%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')

    main(args)
