import argparse
from argparse import Namespace
import pywikibot
import logging
import pprint
from IPython import embed


def main(args: Namespace):
    # parse page/lang/latest_revision
    # check if latest revision matches the DB
    # if not, generate latest page
    pprint.pprint(args)
    embed()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get full annotation of wiki page')
    parser.add_argument('-d', dest='domain', action='store', default='https://test.wikipedia.org/',
                        help='Wiki domain to use', type=str)
    parser.add_argument('-p', dest='page', action='store', default='demo',
                        help='Wiki page to use', type=str)
    parser.add_argument("-v", "--verbose", help="modify output verbosity", action='count', default=0)

    main(parser.parse_args())
