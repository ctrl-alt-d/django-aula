# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0002_alumne_ralc'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='alumne',
            unique_together=set([]),
        ),
    ]
