# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidencies', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='incidencia',
            name='gestionada_pel_tutor',
            field=models.BooleanField(default=False, help_text='Aquesta incid\xe8ncia no la gestiona el professor que la posa, ser\xe0 gestionada directament pel tutor.".', verbose_name='Incid\xe8ncia gestionada pel tutor'),
        ),
    ]
