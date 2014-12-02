import os
from setuptools import setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

data = {
    'name': 'django-elfinderfs',
    'version': '0.0.3',
    'author': 'Okami',
    'author_email': 'okami@fuzetsu.info',
    'description': (
        "django-elfinderfs is a 3rd party connector for elFinder 2.x "
        "and Django. It's a simple local file system driver which "
        "does not uses any databases."),
    'license': 'GPLv3',
    'keywords': 'django elfinder file manager',
    'url': 'http://packages.python.org/django-elfinderfs',
    'packages': ['elfinderfs'],
    'long_description': '',
    'classifiers': [
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Framework :: Django',
    ],
    'install_requires': [
        'Django >= 1.7',
        'Pillow >= 2.2.1',
        'djangorestframework >= 2.4.3',
    ],
}

setup(**data)
