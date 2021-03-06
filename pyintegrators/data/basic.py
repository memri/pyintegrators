# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/basic.ipynb (unless otherwise specified).

__all__ = ['read_file', 'read_json', 'write_json', 'download_file', 'unzip', 'PYI_HOME', 'PYI_TESTDATA', 'HOME_DIR',
           'MODEL_DIR', 'MEMRI_S3']

# Cell
from ..imports import *
from urllib.request import urlretrieve
import requests
from tqdm import tqdm
from fastai.data.external import download_url
from fastai.basics import progress_bar
import zipfile

# Cell
Path.ls = lambda x: list(x.iterdir())
PYI_HOME = Path.cwd().parent
PYI_TESTDATA = PYI_HOME / "test" / "data"
HOME_DIR = Path.home()
MODEL_DIR = HOME_DIR / ".memri" / "models"
MEMRI_S3 = "https://memri.s3-eu-west-1.amazonaws.com"
MODEL_DIR.mkdir(parents=True, exist_ok=True)


def read_file(path):
    return open(path, "r").read()

def read_json(path):
    with open(path) as json_file:
        return json.load(json_file)

def write_json(obj, fname):
    with open(fname, 'w') as file_out:
        json.dump(obj , file_out)

def download_file(url, output_path):
    if not Path(output_path).exists():
        output_path.parent.mkdir(exist_ok=True, parents=True)
        print(f"downloading {url}", flush=True)

        # this may look overly complicated, but we want the system to first completely download and then write
        # , to prevent caching issues.
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')
        if total_length is None: # no content length header
            res = response.content
            with open(output_path, "wb") as f:
                f.write(res)
        else:
            dl = 0
            total_length = int(total_length)
            pbar = progress_bar(range(total_length), leave=False)
            pbar.update(0)
            res = b''
            for data in response.iter_content(chunk_size=1024*1024):
                dl += len(data)
                pbar.update(dl)
                res += data
            with open(output_path, "wb") as f:
                f.write(res)

def unzip(f, dest):
    with zipfile.ZipFile(str(f)) as zf:
        zf.extractall(str(dest))