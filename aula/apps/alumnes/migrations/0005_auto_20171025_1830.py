# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0004_type_data_naixement'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumne',
            name='periodicitat_faltes',
            field=models.IntegerField(default=1, help_text='Interval de temps m\xednim entre dues notificacions', choices=[(0, b'No notificar'), (1, b'Un dia'), (2, b'Dos dies'), (3, b'Tres dies'), (7, b'Una setmana')]),
        ),
        migrations.AlterField(
            model_name='alumne',
            name='periodicitat_incidencies',
            field=models.BooleanField(default=True, help_text='Periodicitat en la notificaci\xf3 de les incid\xe8ncies.', choices=[(False, b'No notificar.'), (True, b'Notificar-les totes.')]),
        ),
    ]
