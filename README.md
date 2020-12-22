# pyintegrators
> Integrators connect the information in your Pod. They <b>import your data from external services</b> using <i>Importers</i> (Gmail, WhatsApp, etc.), <b>connect new data to the existing data</b> using <i>indexers</i> (face recognition, spam detection, object detection), and <b>execute actions</b> (sending messages, uploading files).


[![Gitlab pipeline status (self-hosted)](https://img.shields.io/gitlab/pipeline/memri/pyintegrators/dev?gitlab_url=https%3A%2F%2Fgitlab.memri.io&label=CI&logo=gitlab&style=plastic)](https://gitlab.memri.io/memri/pyintegrators/-/pipelines/latest)
[![GitHub last commit](https://img.shields.io/github/last-commit/memri/pyintegrators?logo=gitlab&label=Last%20commit)](https://gitlab.memri.io/memri/pyintegrators/-/commits/dev)
[![Discourse status](https://img.shields.io/discourse/status?color=00A850&label=Discourse&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAACAAAAAhCAYAAAC4JqlRAAAEhUlEQVR42r2XA5RjyxqFM7Y90ymd6uCNbdu2bdu2bdu2bdu27dmvUtfpk9zu5K6utXZU+Pb/l3IsISlCiFiCiBKS0m4GpdMNxpa5JCmbZFDeQTKWR0oZyfJfF8l5IQVdr6DfDcrwL3qnDM3knKf2GyysIoMacKcSfNAvg7AllNIkvrDDCMJ6uQZRgj9S2Xjpmppgk1MlShRNULrcD6iZvhqM1QkOP5xqvMnTQIFKJQlHZ6WhAQJDrALtrFz/JoNjhLHaXumqwRizjjYlF/S4gt5PZuAst+Fk9lS4UDg9LhRJj9O502B3quTowARs3k18Vusqo/lKJ7yiWafsCrwtwMA9BT6eISWe106DtzUF3jV04kP/Avg0tQo+z6iGj0OK4nXzzDhSMRtyO6Q3E3ftdnuMf8CTJ08eUVXccG+ck3KcVPArARL3q2XS4A/dc+DboT7Ah2XA11X/1JeV+HFxFB6Pr4Y6xTJ4McF7/jP1lLZ3b+RQ2quivqrgz2upqOtIfN3YVkPcwKa6cmwASlXO7vGsMAwjoYar/RFe/fDIvVF/K9dpf1g9A97WDcT3k4NNQN7V52B3JM+R0dSEIKz3n6ece2VypYvJBI5nTKXT/m1755DCtZ68W4hMi1pABDqCmiDs2u/p5yPcK+sSHT1e1EmDj4MK+wL/U0V3tQBp1R2mu4sQoQywPe4Vo6wcp6RdR68WlV8Gep/tDT57CLg9RdBpoLS6y8BD94qFAQKncqfF+/aZ/lx0vmrejRGwL2uJBJXbmmSB9nMZ+OxesUoZuFwqo9rjlf2Bay25NQpyTX3E6LbQbB1MsZjNzXSrwNVymfB1XSu/DYy/MhBsdW1EGnfILAPzTA30JBwX1EHydUt7vw00PtYRtlWNEHHSCbMMTDY1kJcwfex+WdnML/ivrythXVcN9sVdEGnM/iAcyVgfbcBMa41AfJhYyS8Da++OhWVpacSbOR8xuswxux2reDRQmnBcq5UT+LzCJ/hX1S/VljoIWF0DlpUvkLB8syAMIQTxaCA/5bhcMSt+vV3ik4FWx7vo6BPMnoqwi+6bnIb0vEUVjwaaE4EXE2v4BO9+uqeG25a1hWXVa8Sr3cvsLujs1cC0XGnw8+bEEIHvv12A4nuaa7h9RUtYVjxB5JG7Ibh0j/65lDKmVwNbmxX/x+A/v6zCroeTsPX+BLz7uPTP31+9X4z1d8eh7pH2iLS8HKIsLw86b7CK/CUiTjwG7kxttvrbargnA4FKN1d21YAjj6ei9f4+SL+0M6yzh4HMHq73dZxVlRB1RXkdbfhlZcFW14FY0BfhF17QaY/RbQG4zWn2L/kyYyyyVwNZUjoxeHpHFOrVGLJuQyQpVA3WTHkhpB0sZQbEbjEG4WddRvhF55QuqVX+REPDLnqA6L2WICBncc8PLYT8T4PdDPgkki4HkuUpg6QFKsGaOR+ECPTW/ofBWBkN9cGAXxKUfZCMldbAUDdA2D1JaVoNC10D+mlo7J/bLfQM0PuSsMH6mA1OUS6n+iNB+UQF7a8+15aEJLeEsPwfm4dbxw/8yD4AAAAASUVORK5CYII=&server=https%3A%2F%2Fdiscourse.memri.io)](https://discourse.memri.io) 
[![Twitter URL](https://img.shields.io/twitter/url?label=%40YourMemri&logo=twitter&style=plastic&url=https%3A%2F%2Ftwitter.com%2FYourMemri)](https://twitter.com/YourMemri)

Integrators for Memri have a single repository per language, this is the repository for Python integrators. Memri also has [Node.js integrators](https://gitlab.memri.io/memri/nodeintegrators). This repository is built with [nbdev](https://github.com/fastai/nbdev), which means that the repo structure has a few differences compared to a standard python repo. The documentation for this repo is hosted on [https://pyintegrators.memri.io/integrators/](https://pyintegrators.memri.io/integrators/).

# Installing
Pyintegrators can be installed for two purposes: 1) For local development we recommend to install using pip 2) For deployment we recommend to install using docker. **Currently, the only way to call integrators from the [memri](https://gitlab.memri.io/memri/browser-application) [clients](https://gitlab.memri.io/memri/ios-application)  is using docker, this will change soon.**

## Install with pip
To install the Python package, and correctly setup nbdev for development run:
```bash
pip install -e . && nbdev_install_git_hooks
```
The last command configures git to automatically clean metadata from your notebooks before a commit.

## Install with Docker 
The normal flow to run an integrator is from the client, by calling the [pods](https://gitlab.memri.io/memri/pod) `run_integrator` api. Subsequently, the Integrator is invoked by the Pod by launching a Docker container. To build the image for this container, run:
```bash
docker build -t memri-pyintegrators .
```

## Overview
Pyintegrators currently provides the following integrators. Make sure to check out the documentation for tutorials and usage instructions.





| Integrator | Description | Tests passing |
|------------|-------------|---------------|
|`EmailImporter`|Imports emails over imap.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|
|`FaceClusteringIndexer`|Clusters faces on photos.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|
|`GeoIndexer`|Adds Countries and Cities to items with a location.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|
|`NotesListIndexer`|Extracts lists from notes and categorizes them.| ![Build passing](https://gitlab.memri.io/memri/pyintegrators/-/raw/prod/assets/build-passing.svg "Build passing")|




## Nbdev & Jupyter Notebooks
The Python integrators are written in [nbdev](https://nbdev.fast.ai/) ([video](https://www.youtube.com/watch?v=9Q6sLbz37gk&t=1301s)). With nbdev, it is encouraged to write code in 
[Jupyter Notebooks](https://jupyter.readthedocs.io/en/latest/install/notebook-classic.html). Nbdev syncs all the notebooks in `/nbs` with the python code in `/integrators`. Tests are written side by side with the code in the notebooks, and documentation is automatically generated from the code and markdown in the notebooks and exported into the `/docs` folder. Check out the [nbdev quickstart](wiki/nbdev_quickstart.md) for an introduction, **watch the video linked above**, or see the [nbdev documentation](https://nbdev.fast.ai/) for a all functionalities and tutorials.

### Contributing
When you make a merge request, make sure that you used all the nbdev commands specified in the [quickstart](wiki/nbdev_quickstart.md).

## Render documentation locally
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
