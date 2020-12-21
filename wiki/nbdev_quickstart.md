# nbdev quickstart
With nbdev we create the code in Notebooks, where we specify the use off cells using special tags. We list the most widely used tags here to get you started quickly

## Tags
When you create a new notebook, add `#default_exp <packagename>.<modulename>` to the top of your notebook to define the Python module to export to. For example, if you have a notebook file `nbs/data.email.ipynb`, with as first line:
```
#default_exp data.email
```
The notebook will write to a file called `integrators/data/email.py` when nbdev is commanded to sync using `nbdev_build_lib`.

All cells `#export` will be converted to code in the outputfile, e.g.
```
# export
def times_two(i): return i*2
```
Will be written to the file specified in #default_exp. All cells without the `#export` tag, will be converted to tests by default. 

By default, all cells are included in the documentation, unless you add the keyword `#hide`, e.g.
```
# hide
for i in range(1000000):
    print(i)
```

Will not appear in the documentation. Lastly, Notebooks with a name that start with an underscore, are ignored by nbdev completely. Nbdev has many other functionalities, see the [nbdev docs](https://nbdev.fast.ai/) for more information.


## CLI 
After developing your code in Notebooks, you can use the nbdev CLI:
- `nbdev_build_lib` to convert the Notebooks `/nbs` to the library in `/integrators`
- `nbdev_test_nbs` to run the tests (all cells without #export tags)
- `nbdev_build_docs` to generate the docs in `/docs`
- `nbdev_clean_nbs` to clean the Notebooks' metadata to prevent Git conflicts, if you followed the normal installation, this is not necessary.
- `nbdev_fix_merge` to fix notebook files (make them readable) when they contain a merge conflict.