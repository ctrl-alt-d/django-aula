# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('usuaris', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfessorConserge',
            fields=[
            ],
            options={
                'ordering': ['last_name', 'first_name', 'username'],
                'proxy': True,
            },
            bases=('auth.user',),
        ),
    ]
