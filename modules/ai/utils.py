from pathlib import Path


def get_sys_prompt(filename):
    if(Path(filename).exists()):
        with open(filename,"r") as f:
            result = f.read()
            return result