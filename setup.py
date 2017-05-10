import os
import glob
from distutils.core import setup
import py2exe


def find_data_files(source,target,patterns):
    """Locates the specified data-files and returns the matches
    in a data_files compatible format.

    source is the root of the source data tree.
        Use '' or '.' for current directory.
    target is the root of the target data tree.
        Use '' or '.' for the distribution directory.
    patterns is a sequence of glob-patterns for the
        files you want to copy.
    """
    if glob.has_magic(source) or glob.has_magic(target):
        raise ValueError("Magic not allowed in src, target")
    ret = {}
    for pattern in patterns:
        pattern = os.path.join(source,pattern)
        for filename in glob.glob(pattern):
            if os.path.isfile(filename):
                targetpath = os.path.join(target,os.path.relpath(filename,source))
                path = os.path.dirname(targetpath)
                ret.setdefault(path,[]).append(filename)
    return sorted(ret.items())

# Example:
setup(
    name="Sample",
    version="1.0",
    description="A sample app",
    author="MizardX",
    windows=['main.py'],
    data_files=find_data_files('data','data',[
        'img/*',
        'lvl/*',
        'msc/*',
        'snd/*'
    ]), requires=['pygame']
)

# Will copy data/README to dist/README, and all files in data/images/ to dist/images/
# (not checking any subdirectories of data/images/)