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

from functools import update_wrapper
import json

from django import forms
from django.conf.urls import url
from django.contrib import admin
from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.forms.widgets import Widget
from django.utils.safestring import mark_safe


from .models import SiteFiles
from .views import ConnectorView


class ElfinderWidget(Widget):
    def __init__(self, *args, **kwargs):
        self.options = {
            'lang': 'en',
            'commandsOptions': {
                'getfile': {
                    'onlyURL': False,
                },
            },
        }
        self.options.update(kwargs.pop('options', {}))
        self.attrs = kwargs.get('attrs', {})
        super().__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        attrs = attrs or {}
        attrs.update(self.attrs)
        output = mark_safe('''
            <input style="display: none" name="%(name)s"
                   value="%(value)s" type="text">
            <script type="text/javascript" charset="utf-8">
                function getUrlParam(paramName) {
                   var reParam = new RegExp("(?:[\?&]|&amp;)" + paramName + "=([^&]+)", "i");
                   var match = window.location.search.match(reParam);
                   return (match && match.length > 1) ? match[1] : "";
                }
                $().ready(function() {
                    // hide label in django-suit
                    $(".control-label").hide();
                    // hide label
                    $("label[for=id_%(name)s]").hide();
                    var options = %(options)s;
                    options.customData = {
                        "csrfmiddlewaretoken": $.cookie("csrftoken")
                    };
                    if (window.opener !== null && window.opener.CKEDITOR !== null) {
                        var funcNum = getUrlParam('CKEditorFuncNum');
                        options.getFileCallback = function(file) {
                            window.opener.CKEDITOR.tools.callFunction(funcNum, file.absolute_url);
                            window.close();
                        };
                    }
                    options.url = "%(url)s";
                    var elf = $("#elfinder").elfinder(options).elfinder("instance");
                });
            </script>
            <div id="elfinder-container" %(attrs)s><div id="elfinder"></div></div>
        ''' % {
            'name': name,
            'value': value,
            'options': json.dumps(self.options),
            'url': reverse('admin:elfinderfs_sitefiles_connector'),
            'attrs': ' '.join(map(lambda x: '%s="%s"' % x, attrs.items())),
        })
        return output

    class Media(object):
        css = {
            'all': (
                '/static/elfinder/css/smoothness/jquery-ui.min.css',
                '/static/elfinder/css/elfinder.min.css',
                '/static/elfinder/css/theme.css',
            ),
        }
        js = (
            '/static/elfinder/js/jquery-1.6.2.min.js',
            # jquery.cookie.js is used for obtaining a csrftoken only
            # there should be a better way to do it
            '/static/elfinder/js/jquery.cookie.js',
            '/static/elfinder/js/jquery-ui-1.11.1/jquery-ui.min.js',
            '/static/elfinder/js/elfinder.min.js',
        )


class SiteFilesForm(forms.ModelForm):
    class Meta(object):
        widgets = {
            'domain': ElfinderWidget(
                attrs={'style': 'font-size: 18px;'},
                options={'height': 650},
            ),
        }


class SiteFilesAdmin(admin.ModelAdmin):
    fields = 'domain',
    form = SiteFilesForm
    has_add_permission = lambda *x: False
    has_delete_permission = lambda *x: False

    history_view = None

    def change_view(self, request, object_id=None, form_url='', extra_context=None):
        object_id = object_id or str(Site.objects.latest('domain').id)
        return super().change_view(
            request, object_id, form_url=form_url, extra_context=extra_context)

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)
            return update_wrapper(wrapper, view)

        info = self.model._meta.app_label, self.model._meta.model_name

        urlpatterns = [
            url(r'^$', wrap(self.change_view), name='%s_%s_changelist' % info),
            url(r'^connector/$', ConnectorView.as_view(),
                name='elfinderfs_sitefiles_connector'),
        ]
        return urlpatterns

admin.site.register(SiteFiles, SiteFilesAdmin)
