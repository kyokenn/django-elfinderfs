import os, sys, glob, fnmatch
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


# Code borrowed from wxPython's setup and config files
# Thanks to Robin Dunn for the suggestion.
# I am not 100% sure what's going on, but it works!
def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)


# https://wiki.python.org/moin/Distutils/Tutorial
def find_data_files(srcdir, *wildcards, **kw):
    # get a list of all files under the srcdir matching wildcards,
    # returned in a format to be used for install_data
    def walk_helper(arg, dirname, files):
        if '.svn' in dirname:
            return
        names = []
        lst, wildcards = arg
        for wc in wildcards:
            wc_name = opj(dirname, wc)
            for f in files:
                filename = opj(dirname, f)

                if fnmatch.fnmatch(filename, wc_name) and not os.path.isdir(filename):
                    names.append(filename)
        if names:
            lst.append((dirname, names))

    file_list = []
    recursive = kw.get('recursive', True)
    if recursive:
        os.walk(srcdir, walk_helper, (file_list, wildcards))
    else:
        walk_helper((file_list, wildcards),
                    srcdir,
                    [os.path.basename(f) for f in glob.glob(opj(srcdir, '*'))])
    return file_list


data = {
    'name': 'django-elfinderfs',
    'version': '0.0.9',
    'author': 'Okami',
    'author_email': 'okami@fuzetsu.info',
    'description': (
        "django-elfinderfs is a 3rd party connector for elFinder 2.x "
        "and Django. It's a simple local file system driver which "
        "does not uses any databases."),
    'license': 'GPLv3',
    'keywords': 'django elfinder file manager',
    'url': 'https://pypi.python.org/pypi/django-elfinderfs',
    'packages': [
        'elfinderfs',
        'elfinderfs.migrations',
    ],
    'long_description': '',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Framework :: Django',
    ],
    'install_requires': [
        'Django >= 1.8',
        'Pillow >= 2.8',
        'djangorestframework >= 3.2',
    ],
    'data_files': find_data_files('elfinderfs/static', '*.*'),
    'include_package_data': True,
}

setup(**data)
