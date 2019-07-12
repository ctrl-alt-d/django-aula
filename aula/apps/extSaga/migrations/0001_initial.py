# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Grup2Aula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grup_saga', models.CharField(unique=True, max_length=60, blank=True)),
                ('Grup2Aula', models.ForeignKey(related_name='grup2aulasaga_set', to='alumnes.Grup', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['Grup2Aula', 'grup_saga'],
                'verbose_name': 'Mapeig Grup Aula Saga',
                'verbose_name_plural': 'Mapejos Grups Aula Saga',
            },
        ),
        migrations.CreateModel(
            name='ParametreSaga',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom_parametre', models.CharField(help_text='Nom Par\xe0metre', unique=True, max_length=45)),
                ('valor_parametre', models.CharField(max_length=240, blank=True)),
            ],
            options={
                'ordering': ['nom_parametre'],
                'verbose_name': 'Par\xe0metre Saga',
                'verbose_name_plural': 'Par\xe0metres Saga',
            },
        ),
    ]
