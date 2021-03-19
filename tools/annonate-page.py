import argparse
from argparse import Namespace
from wiki_annotate.core import Annotate
import pprint
from IPython import embed


def main(args: Namespace):
    annotate = Annotate(url=args.url)  # TODO: Fix: https://en.wikipedia.org/wiki/Giri/Haji
    foo = annotate.run()
    moo = annotate.get_ui_revisions(foo)
    embed()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get full annotation of wiki page')
    parser.add_argument('-u', dest='url', action='store', default='https://test.wikipedia.org/wiki/Demo',
                        help='Full URL to annotate', type=str)
    parser.add_argument("-v", "--verbose", help="modify output verbosity", action='count', default=0)
    args = parser.parse_args()

    main(args)
