from typing import Set, Any

import pywikibot


def get_wikipedia_langs() -> set[Any]:
    # url can be any URL, just to get all wikipedia languages
    pws = pywikibot.Site(url='https://en.wikipedia.org/wiki/Murphy\'s_law')
    return set([f.split('.')[0] for _, f in pws.family.langs.items()])
