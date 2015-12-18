# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sortides', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sortida',
            name='condicions_generals',
            field=models.TextField(help_text='Condicions generals. (m\xe8tode de pagament, entrepants, entrades, comentaris...', blank=True),
        ),
        migrations.AddField(
            model_name='sortida',
            name='termini_pagament',
            field=models.DateTimeField(help_text='Omplir si hi ha data l\xedmit per a realitzar el pagament.', null=True, verbose_name='Termini pagament', blank=True),
        ),
    ]
