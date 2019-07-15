# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sortides', '0003_auto_20160226_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='sortida',
            name='alumnes_a_l_aula_amb_professor_titular',
            field=models.BooleanField(default=False, help_text="Els alumnes seran a l'aula i el professor de l'hora corresponent passar\xe0 llista com fa habitualment.", verbose_name='Passar llista com normalment?'),
        ),
        migrations.AddField(
            model_name='sortida',
            name='estat_sincronitzacio',
            field=models.CharField(default='N', help_text="Per passar els alumnes a 'no han de ser a l'aula' ", max_length=1, editable=False, choices=[('N', 'No sincronitzada'), ('x', ''), ('Y', '')]),
        ),
    ]
