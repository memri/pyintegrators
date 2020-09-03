# Integrators
> Integrators integrate your information in the pod. They import your data from external services (gmail, whatsapp, icloud, facebook etc.), enrich your data with indexers (face recognition, spam detection, duplicate photo detection), and execute actions (sending mails, automatically share selected photo's with your family).


Integrators for memri have a single repo per language, this repo the one for python, but other repo's exist for [node](https://gitlab.memri.io/memri/nodeintegrators) and in the future for rust. This repo is built with [nbdev](https://github.com/fastai/nbdev) and therefore all code/documentation/tests are written in one place as jupyter notebooks and exported to a python-package/jekyll-website/unit-tests.

## Install

`pip install -e integrators`

`nbdev_install_git_hooks`

This last command clears your notebooks of unnecessary metadata when making a commit.

## How to develop with nbdev

The [nbdev website](https://github.com/fastai/nbdev) obviously contains great docs that will help you understand how to develop with it. If you don't want to read that, the most important things to get you started are:

- Add `#export` flags to the cells that define the functions you want to include in your python modules.
- Add `#default_exp <packagename>.<modulename>` to the top of your notebook to define the python module to export to.

When you are done writing your code in notebooks, call `nbdev_build_lib` to convert the notebooks to code and tests.

### Run tests

Every cell without the `#export` flag will be a test. So make sure that the code in notebooks runs fast and without errors. You can run all tests by calling.

`nbdev_test_nbs`

## Docs

If you want to hide certain functionality in the docs, you can use the `# hide` flag in the top of a cell

### Render docs locally

First install Jekyll:

`gem install bundler jekyll`

`bundle install`

Then, run the Jekyll server:

`cd docs`

`bundle exec jekyll serve`
