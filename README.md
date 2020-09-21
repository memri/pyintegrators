# Integrators
> Integrators integrate your information in the pod. They import your data from external services (gmail, whatsapp, icloud, facebook etc.), enrich your data with indexers (face recognition, spam detection, duplicate photo detection), and execute actions (sending mails, automatically share selected photo's with your family).


Integrators for memri have a single repo per language, this repo is the one for python, but other repo's exist for [node](https://gitlab.memri.io/memri/nodeintegrators) and in the future for rust. This repo is built with [nbdev](https://github.com/fastai/nbdev) and therefore all code/documentation/tests are written in one place as jupyter notebooks and exported to a python-package/jekyll-website/unit-tests.

## Install

```
pip install -e integrators
nbdev_install_git_hooks
```

This last command clears your notebooks of unnecessary metadata when making a commit.

## Build

To enable calling integrators from the [pod](https://gitlab.memri.io/memri/pod) the integrator docker containers needs to be built. *You can skip this if you are developing an indexer locally and you don't want to integrate with the pod yet.* To build, run:

```
./examples/build.sh
```

Now, the pod is able to find the integrator container when calling it.

## How to develop with nbdev

The python integrators are written in nbdev. With nbdev, you use jupyter notebooks as a single source of truth, and generate the library, documentation and tests from the notebooks. The [nbdev website](https://github.com/fastai/nbdev) contains great documentation that will help you understand how to develop with it. If you don't want to read that, the most important things to get you started are:

- Add `#export` flags to the cells that define the functions you want to include in your python modules.
- Add `#default_exp <packagename>.<modulename>` to the top of your notebook to define the python module to export to.
- All cell's that are not exported are tests by default

When you are done writing your code in notebooks, call `nbdev_build_lib` to convert the notebooks to code and tests. Call `nbdev_build_docs` to generate the docs.

### Run tests

Every cell without the `#export` flag will be a test. So make sure that the code in notebooks runs fast and without errors. You can run all tests by calling.

```
nbdev_test_nbs
```

## Docs

If you want to hide certain functionality in the docs, you can use the `#hide` flag in the top of a cell

### Render docs locally

Often you might want to check your docs locally before deploying them. To do so, first install Jekyll:

```
gem install bundler jekyll
bundle install
```


Then, run the Jekyll server:

```
cd docs
bundle exec jekyll serve
```
And thats it!
