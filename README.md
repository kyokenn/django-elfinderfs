django-elfinderfs
=================

elFinder is an open-source file manager for web, written in JavaScript using jQuery UI.
Creation is inspired by simplicity and convenience of Finder program used in Mac OS X
operating system.

django-elfinderfs is a 3rd party connector for elFinder 2.x and Django.
It's a simple local file system driver which does not uses any databases.


Requirements
------------

* Python >= 3.0
* Django >= 1.8
* Django REST Framework >= 3.1
* PIL or Pillow


Installation
------------

* pip install django-elfinderfs
* Modify your project's settings.py:

For example:
INSTALLED_APPS = (
    ...
    'django.contrib.sites',
    ...
    'rest_framework',
    ...
    'elfinderfs',
    ...
)

```python
ELFINDERFS = {
    'roots': {
        'Media': {
            'url': MEDIA_URL,
            'root': MEDIA_ROOT,
            'thumbnails_prefix': '.thumbnails',
        },
        'TMP': {
            'url': '/tmp/',
            'root': '/tmp/',
            'thumbnails_prefix': '.thumbnails',
        },
    },
    'default_root': 'Media',
}
```

* File management is available in your django admin at the url /admin/elfinderfs/sitefiles/.
Files are the same for each domain.


Not implemented commands
------------------------

* ls
* tmb
* size
* dim
* archive
* extract
* info
* netmount

Most of this commands are not used in default configuration of the elFinder.


Not implemented features
------------------------

* Archive management (packing, unpacking).
* Symlinks (symlinks are hidden to prevent data corruption).


Screenshots
-----------

* Default Django Admin

![Default Django Admin](/defaultadmin.png)

* Django Suit

![Django Suit](/suitadmin.png)
