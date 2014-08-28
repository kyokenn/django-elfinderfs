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
* Django >= 1.6
* Django REST Framework >= 2.3
* PIL or Pillow


Installation
------------

* elfinderfs django app to your project. (no setup.py atm)
* Modify your project's settings.py: add 'rest_framework' and 'elfinderfs' to INSTALLED_APPS
* Add elfinderfs configuration to your project's settings.py:

For example:
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

* Add elfinderfs urls to your projec's urls.py:

For example:
```python
urlpatterns = patterns(
    '',
    ...
    url(r'^finder/', include('elfinderfs.urls', namespace='elfinderfs')),
)
```

If you need a connector only:
```python
urlpatterns = patterns(
    '',
    ...
    url(r'^finder/connector/', 'elfinderfs.views.connector'),
)
```

* Add elFinder client to your webpage or template

For example:
```html
...
<head>
    ...
 <link rel="stylesheet" type="text/css" media="screen" href="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.14/themes/smoothness/jquery-ui.css" />
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js" ></script> 
    <script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.14/jquery-ui.min.js"></script>
    <link rel="stylesheet" type="text/css" media="screen" href="/static/elfinder/css/elfinder.min.css">
    <script type="text/javascript" src="/static/elfinder/js/elfinder.min.js"></script>
    <link rel="stylesheet" type="text/css" media="screen" href="/static/elfinder/css/theme.css">
</head>
...
<body>
    ...
    <script type="text/javascript" charset="utf-8">
        $().ready(function() {
            var elf = $('#elfinder').elfinder({
                lang: 'en',
                url: '/finder/connector/'
            }).elfinder('instance');
        });
    </script>
    <div id="elfinder"></div>
    ...
</body>
...
```

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
