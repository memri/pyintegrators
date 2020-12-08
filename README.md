# pyintegrators
> Integrators integrate your information in your Pod. They import data from external services (Gmail, WhatsApp, etc.), enrich data with indexers (face recognition, spam detection, etc.), and execute actions (sending messages, uploading files, etc.).



# Overview
We start by listing the existing indexers and their functionalities, make sure to check out their pages for usage examples.





| Integrator | Description | Tests passing |
|------------|-------------|---------------|
|`EmailImporter`|Imports emails over imap| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|
|`FaceRecognitionIndexer`|Recognizes photos from faces.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|
|`GeoIndexer`|Adds Countries and Cities to items with a location.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|
|`NotesListIndexer`|Extracts lists from notes and categorizes them.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|




Integrators for Memri have a single repository per language, this repository is the one for Python, but others exist for [Node.js](https://gitlab.memri.io/memri/nodeintegrators) and [Rust](https://gitlab.memri.io/memri/rustintegrators). This repository makes use of [nbdev](https://github.com/fastai/nbdev), which means all code, documentation and tests are made in Jupyter Notebooks and exported to a Python package, a Jekyll documentation and unit tests.

## Using Docker 
Integrators are invoked by the Pod by launching a Docker container. To build the images for these containers, run:
```bash
docker build -t memri-pyintegrators .
```

## Local build
### Install
To install the Python package:
```bash
pip install -e . 
```

If you want to contribute, you have to clean the Jupyter Notebooks every time before you push code to prevent conflicts 
in the Notebooks' metadata. A script to do so can be installed using:
```bash
nbdev_install_git_hooks
```

### Jupyter Notebooks
The Python integrators are written in nbdev. With nbdev, you write all code in 
[Jupyter Notebooks](https://jupyter.readthedocs.io/en/latest/install/notebook-classic.html), and generate the library, documentation and tests using the nbdev CLI. 

### nbdev
With nbdev we create the code in Notebooks, where we specify the use off cells using special tags. See the [nbdev documentation](https://nbdev.fast.ai/) for a all functionalities and tutorials, the most important tags are listed below.

#### nbdev tags
- Notebooks that start their name with an underscore, are ignored by nbdev completely
- Add `#default_exp <packagename>.<modulename>` to the top of your notebook to define the Python module to export to
- Add `#export` to the cells that define functions to include in the Python modules.
- All cells without the `#export` tag, are tests by default
- All cells are included in the documentation, unless you add the keyword `#hide`

#### nbdev CLI 
After developing your code in Notebooks, you can use the nbdev CLI:
- `nbdev_build_lib` to convert the Notebooks to the library and tests 
- `nbdev_test_nbs` to run the tests
- `nbdev_build_docs` to generate the docs
- `nbdev_clean_nbs` to clean the Notebooks' metadata to prevent Git conflicts

### Contributing
Before you make a merge request, make sure that you used all the nbdev commands specified above, or GitLab's CI won't pass.

## Docs
Find the online docs at [pyintegrators.docs.memri.io](https://pyintegrators.memri.io/integrators/).

### Render documentation locally
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
