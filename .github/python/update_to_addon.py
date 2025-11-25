'''
This script updates the .github folder from the template world on
this repo to update actions and bug templates.
'''
from pathlib import Path
import json
import shutil

GH = Path("../Template/.github")
GITHUB_PATH = Path(".github")

def remove_init():
    '''
    This makes sure that the init action is deleted. The init
    action should only run on initialisation of a project but
    failed to delete for older projects.
    '''
    Path.unlink(GITHUB_PATH / 'python/init.py')
    Path.unlink(GITHUB_PATH / 'workflows/init.yml')
def main():
    # .Github
    if GITHUB_PATH.exists():
        shutil.rmtree(GITHUB_PATH)
    shutil.copytree(GH, GITHUB_PATH)

    # Apply packs
    remove_init()

if __name__ == "__main__":
    main()
