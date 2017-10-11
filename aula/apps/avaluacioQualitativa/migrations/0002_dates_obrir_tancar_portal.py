# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaluacioQualitativa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='avaluacioqualitativa',
            name='data_obrir_portal_families',
            field=models.DateField(help_text='Els pares podran veure els resultats al portal fam\xedlies a partir de la data aqu\xed introdu\xefda.', null=True, verbose_name='Primer dia per veure els resultats al portal fam\xedlies', blank=True),
        ),
        migrations.AddField(
            model_name='avaluacioqualitativa',
            name='data_tancar_tancar_portal_families',
            field=models.DateField(help_text='Els pares podran veure els resultats al portal fam\xedlies fins a la data aqu\xed introdu\xefda.', null=True, verbose_name='Darrer dia per veure els resultats al portal fam\xedlies', blank=True),
        ),
    ]
