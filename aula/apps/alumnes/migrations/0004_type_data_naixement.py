# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0003_treure_restriccio_unique'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumne',
            name='data_neixement',
            field=models.DateField(null=True, verbose_name=b'Data naixement'),
        ),
    ]
