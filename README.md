# pyintegrators
> Integrators integrate your information in your Pod. They import data from external services (Gmail, WhatsApp, etc.), enrich data with indexers (face recognition, spam detection, etc.), and execute actions (sending messages, uploading files, etc.).


Integrators for Memri have a single repository per language, this repository is for Python integrators. Memri also has [Node.js integrators](https://gitlab.memri.io/memri/nodeintegrators). This repository makes use of [nbdev](https://github.com/fastai/nbdev), which means that the repo structure is different from a normal python project, the documentation for this repo is hosted on [https://pyintegrators.memri.io/integrators/](https://pyintegrators.memri.io/integrators/).

# Installing
Pyintegrators can be installed in two ways: 1) For local development we recommend to install using pip 2) For deployment we recommend to install using docker. **Currently, the only way to call integrators from the [memri](https://gitlab.memri.io/memri/browser-application) [clients](https://gitlab.memri.io/memri/ios-application)  is using docker, this will change soon.**

## Install with pip
To install the Python package, and correctly setup nbdev for development run:
```bash
pip install -e . && nbdev_install_git_hooks
```

## Install with Docker 
Integrators are invoked by the Pod by launching a Docker container. To build the image for this container, run:
```bash
docker build -t memri-pyintegrators .
```


# Overview
We start by listing the existing indexers and their functionalities, make sure to check out their pages for usage examples.





| Integrator | Description | Tests passing |
|------------|-------------|---------------|
|`EmailImporter`|Imports emails over imap.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|
|`FaceClusteringIndexer`|Clusters faces on photos.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|
|`GeoIndexer`|Adds Countries and Cities to items with a location.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|
|`NotesListIndexer`|Extracts lists from notes and categorizes them.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|




# Nbdev & Jupyter Notebooks
The Python integrators are written in [nbdev](https://nbdev.fast.ai/) ([video](https://www.youtube.com/watch?v=9Q6sLbz37gk&t=1301s)). With nbdev, all code is written in 
[Jupyter Notebooks](https://jupyter.readthedocs.io/en/latest/install/notebook-classic.html). Therefore all the notebooks in `/nbs` and the python code in `/integrators` are synced, tests are written side by side with the code in the notebooks, and documentation is automatically generated from the notebooks in the `/docs` folder. Check out the [nbdev quickstart](wiki/nbdev_quickstart) for an introduction, or see the [nbdev documentation](https://nbdev.fast.ai/) for a all functionalities and tutorials.

## Contributing
When you make a merge request, make sure that you used all the nbdev commands specified in the [quickstart](wiki/nbdev_quickstart).

# Render documentation locally
New documentation will be deployed automatically when a new version is released to the `prod`  branch. To inspect the documentation beforehand, you can run it local machine by [installing Jekyll](https://jekyllrb.com/docs/installation/).

To build the documentation:
```bash
cd docs
gem update --system 
bundle install
```

To serve the documentation:
```bash
bundle exec jekyll serve
```
