import diff_match_patch as dmp_module
from IPython import embed

def get_demo_content(number):
    with open(f"./data/demo{number}", 'r') as f:
        data = f.read()
    return data


dmp = dmp_module.diff_match_patch()
diff = dmp.diff_main(get_demo_content(1),get_demo_content(2))

embed()