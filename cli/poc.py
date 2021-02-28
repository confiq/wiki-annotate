import diff_match_patch as dmp_module
from pprint import pprint
import glob
from IPython import embed

def get_demo_content(number):
    with open(f"./data/demo{number}", 'r') as f:
        data = f.read()
    return data

demo_files = glob.glob('./data/demo*')
dmp = dmp_module.diff_match_patch()


for idx, file_name in enumerate(demo_files, 1):
    if len(demo_files) <= idx:  # skip last
        break

    diff = dmp.diff_main(get_demo_content(idx), get_demo_content(idx+1))
    print(get_demo_content(idx))
    pprint(diff)

print(get_demo_content(idx))