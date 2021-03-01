import diff_match_patch as dmp_module
import glob
from pprint import pprint
from wiki_annotate.diffInsertion import DiffInsertion
from wiki_annotate.types import AnnotationCharData
from IPython import embed
DEMO_FILES = glob.glob('./data/demo*')


def get_demo_content(number):
    with open(f"./data/demo{number}", 'r') as f:
        data = f.read()
    return data


# dmp = dmp_module.diff_match_patch()
# for idx, file_name in enumerate(demo_files, 1):
#     if len(DEMO_FILES) <= idx:  # skip last
#         break
#
#     diff = dmp.diff_main(get_demo_content(idx), get_demo_content(idx+1))
#     dmp.diff_cleanupSemantic(diff)
#     print(get_demo_content(idx))
#     pprint(diff)

revision_data = AnnotationCharData(revision=1, user='init')
previous_text = DiffInsertion.create_text(get_demo_content(1), revision_data)

# TODO
for idx, file_name in enumerate(DEMO_FILES, 2):
    if len(DEMO_FILES) <= idx:  # skip last
        break
    text = get_demo_content(idx)

    wiki = DiffInsertion(text, previous_text)
    previous_text = wiki.run(AnnotationCharData(idx, file_name))
    pprint(previous_text)
