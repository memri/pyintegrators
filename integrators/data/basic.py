# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/basic.ipynb (unless otherwise specified).

__all__ = ['read_file', 'read_json', 'write_json', 'PYI_HOME', 'PYI_TESTDATA', 'HOME_DIR']

# Cell
from ..imports import *

# Cell
Path.ls = lambda x: list(x.iterdir())
PYI_HOME = Path.cwd().parent
PYI_TESTDATA = PYI_HOME / "test" / "data"
HOME_DIR = Path.home()

def read_file(path):
    return open(path, "r").read()

def read_json(path):
    with open(path) as json_file:
        return json.load(json_file)

def write_json(obj, fname):
    with open(fname, 'w') as file_out:
        json.dump(obj , file_out)
