# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assignatures', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipusdassignatura',
            name='capcelera',
            field=models.CharField(default='Mat\xe8ria', max_length=45),
        ),
    ]
