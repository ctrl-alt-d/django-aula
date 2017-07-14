# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='alumne',
            name='ralc',
            field=models.CharField(db_index=True, max_length=100, blank=True),
        ),
    ]
