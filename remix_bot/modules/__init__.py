from os.path import dirname, basename, isfile
import glob

# This generates a list of modules in this folder to import the modules on __main__.
mod_paths = glob.glob(dirname(__file__) + "/*.py")
ALL_MODULES = [
    basename(f)[:-3]
    for f in mod_paths
    if isfile(f) and f.endswith(".py") and not f.endswith("__init__.py")
]
