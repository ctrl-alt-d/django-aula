# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tutoria', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='actuacio',
            name='amb_qui_es_actuacio',
            field=models.CharField(help_text="Sobre qui es realitza l'actuaci\xf3", max_length=1, choices=[(b'A', 'Alumne'), (b'F', 'Familia'), (b'T', 'Altres')]),
        ),
    ]
