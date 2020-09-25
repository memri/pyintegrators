# Integrators
> Integrators integrate your information in the pod. They import your data from external services (gmail, whatsapp, icloud, facebook etc.), enrich your data with indexers (face recognition, spam detection, duplicate photo detection), and execute actions (sending mails, automatically share selected photo's with your family).

| Integrator | Description | Tests passing |
|------------|-------------|---------------|
|`FaceRecognitionIndexer`|Recognizes photos from faces.| ![alt text](https://raw.githubusercontent.com/dwyl/repo-badges/master/svg/build-passing.svg)|
|`GeoIndexer`|Adds Countries and Cities to items with a location.| ![alt text](https://raw.githubusercontent.com/dwyl/repo-badges/master/svg/build-passing.svg)|
|`NotesListIndexer`|Extracts lists from notes and categorizes them.| ![alt text](https://raw.githubusercontent.com/dwyl/repo-badges/master/svg/build-passing.svg)|

Integrators for Memri have a single repository per language, this repository is the one for Python, but others exist for 
[Node.js](https://gitlab.memri.io/memri/nodeintegrators) and [Rust](https://gitlab.memri.io/memri/rustintegrators). This 
repository makes use of [nbdev](https://github.com/fastai/nbdev), which means all code, documentation and tests are 
made in Jupyter Notebooks and exported to a Python package, a Jekyll documentation and unittests.

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


### nbdev
The Python integrators are written in nbdev. With nbdev, you write all code in Jupyter Notebooks, and generate the 
library, documentation and tests using the nbdev CLI. See [nbdev website](https://github.com/fastai/nbdev) for the
complete documentation, these features are most important in how we use it:
- Add `#export` flags to the cells that define functions to include in the Python modules.
- Add `#default_exp <packagename>.<modulename>` to the top of your notebook to define the Python module to export to.
- All cells that are not exported are tests by default 

When you are done writing your code in Notebooks, call `nbdev_build_lib` to convert them to the module and tests. 
Call `nbdev_build_docs` to generate the docs.

### Run tests
Every cell without the `#export` flag will be a test. So make sure that the code in notebooks runs fast and without 
errors. You can run all tests by calling.
```bash
nbdev_test_nbs
```

If you want to hide certain functionality in the docs, you can use the `#hide` flag in the top of a cell.

## Documentation

### Render documentation locally
New documentation will be deployed automatically when a new version is released to the `prod` branch. To inspect the 
documentation beforehand, you can run it local machine by [installing Jekyll](https://jekyllrb.com/docs/installation/).

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