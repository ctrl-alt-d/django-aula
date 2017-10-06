# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sortides', '0004_auto_20160422_1721'),
    ]

    operations = [
        migrations.AddField(
            model_name='sortida',
            name='codi_de_barres',
            field=models.CharField(default='', help_text='Codi de barres pagament caixer ( el posa secretaria )', max_length=100, verbose_name='Codi de barres pagament', blank=True),
        ),
    ]
