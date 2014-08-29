# Copyright (C) 2014 Okami, okami@fuzetsu.info
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 3
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe

from .models import SiteFiles
from .views import ConnectorView


class ElfinderWidget(Widget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs = kwargs.get('attrs', {})

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs.update(self.attrs)
        print(' '.join(map(lambda x: '%s="%s"' % x,
                                  (attrs or {}).items())))
        output = mark_safe((
            '<script type="text/javascript" charset="utf-8">'
            '    $().ready(function() {'
            '        var elf = $("#elfinder").elfinder({'
            '            lang: "en",'
            '            url: "%(url)s"'
            '        }).elfinder("instance");'
            '    });'
            '</script>'
            '<div id="elfinder-container" %(attrs)s><div id="elfinder"></div></div>'
            '<input style="display: none" name="%(name)s" '
            'value="%(value)s" type="text">') % {
            'name': name,
            'value': value,
            'attrs': ' '.join(map(lambda x: '%s="%s"' % x,
                                  (attrs or {}).items())),
            'url': reverse('admin:elfinderfs_sitefiles_connector'),
        })
        return output

    class Media(object):
        css = {
            'all': (
                'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.14/themes/smoothness/jquery-ui.css',
                '/static/elfinder/css/elfinder.min.css',
                '/static/elfinder/css/theme.css',
            ),
        }
        js = (
            'https://ajax.googleapis.com/ajax/libs/jquery/1.6.2/jquery.min.js',
            'https://ajax.googleapis.com/ajax/libs/jqueryui/1.8.14/jquery-ui.min.js',
            '/static/elfinder/js/elfinder.min.js',
        )


class SiteFilesForm(forms.ModelForm):
    class Meta(object):
        widgets = {
            'domain': ElfinderWidget(
                attrs={'style': 'font-size: 18px;'},
            ),
        }


class SiteFilesAdmin(admin.ModelAdmin):
    fields = 'domain',
    form = SiteFilesForm

    def get_urls(self):
        return [
            url(r'^/connector/$', ConnectorView.as_view(),
                name='elfinderfs_sitefiles_connector'),
        ] + super().get_urls()


admin.site.register(SiteFiles, SiteFilesAdmin)
