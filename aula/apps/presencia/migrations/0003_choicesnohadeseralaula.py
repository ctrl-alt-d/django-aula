# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presencia', '0002_nohadeseralaula'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nohadeseralaula',
            name='motiu',
            field=models.CharField(max_length=5, choices=[(b'E', 'Expulsat del centre'), (b'A', 'Activitat'), (b'L', 'Classe Anul\xb7lada')]),
        ),
    ]
