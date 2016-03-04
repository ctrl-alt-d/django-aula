# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sortides', '0002_auto_20151218_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sortida',
            name='condicions_generals',
            field=models.TextField(help_text='Condicions generals. (m\xe8tode de pagament, entrepans, entrades, comentaris...', blank=True),
        ),
    ]
