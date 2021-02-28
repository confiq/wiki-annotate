import diff_match_patch as dmp_module
import glob
from pprint import pprint
from lib.wikiAnnotate import WikiAnnotate
from lib.types import AnnotationCharData
from IPython import embed


def get_demo_content(number):
    with open(f"./data/demo{number}", 'r') as f:
        data = f.read()
    return data


demo_files = glob.glob('./data/demo*')

# dmp = dmp_module.diff_match_patch()
# for idx, file_name in enumerate(demo_files, 1):
#     if len(demo_files) <= idx:  # skip last
#         break
#
#     diff = dmp.diff_main(get_demo_content(idx), get_demo_content(idx+1))
#     dmp.diff_cleanupSemantic(diff)
#     print(get_demo_content(idx))
#     pprint(diff)

revision_data = AnnotationCharData(revision=1, user='init')
previous_text = WikiAnnotate.create_text(1, revision_data)
# TODO
for idx, file_name in enumerate(demo_files, 2):
    text = get_demo_content(idx)

    foo = WikiAnnotate()
