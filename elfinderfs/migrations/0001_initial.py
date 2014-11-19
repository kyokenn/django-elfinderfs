# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SiteFiles',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Site Files',
                'verbose_name_plural': 'Site Files',
            },
            bases=('sites.site',),
        ),
    ]
