import diff_match_patch as dmp_module
import wiki_annotate.config as config
import logging
import glob
from pywikibot.i18n import translate
from wiki_annotate.diff import DiffLogic
from wiki_annotate.types import AnnotationCharData
from IPython import embed
DEMO_FILES = glob.glob('./data/demo*')

log = logging.getLogger(__name__)

def get_demo_content(number):
    with open(f"./data/demo{number}", 'r') as f:
        data = f.read()
    return data


revision_data = AnnotationCharData(revid=1, user='init')
previous_text = DiffLogic.init_text(get_demo_content(1), revision_data)

# TODO
for idx, _ in enumerate(DEMO_FILES, 2):
    if len(DEMO_FILES) < idx:  # skip last
        break
    text = get_demo_content(idx)

    wiki = DiffLogic(text, previous_text)
    previous_text = wiki.run(AnnotationCharData(idx, f'demo{idx}'))
    log.debug('yes')
