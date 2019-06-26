# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0001_initial'),
        ('horaris', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Franja2Aula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('franja_kronowin', models.CharField(unique=True, max_length=45, verbose_name='Codi hora al kronowin(0,0=primera hora)')),
                ('franja_aula', models.ForeignKey(blank=True, to='horaris.FranjaHoraria', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['franja_kronowin'],
                'verbose_name': 'Mapeig Franja Hor\xe0ria',
                'verbose_name_plural': 'Mapejos Franjes Hor\xe0ries',
            },
        ),
        migrations.CreateModel(
            name='Grup2Aula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grup_kronowin', models.CharField(unique=True, max_length=45)),
                ('Grup2Aula', models.ForeignKey(related_name='grup2aulakonowin_set', to='alumnes.Grup', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['Grup2Aula', 'grup_kronowin'],
                'verbose_name': 'Mapeig Grup Aula Kronowin',
                'verbose_name_plural': 'Mapejos Grups Aula Kronowin',
            },
        ),
        migrations.CreateModel(
            name='ParametreKronowin',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom_parametre', models.CharField(help_text='Nom par\xe0metre (ex: passwd, assignatures amb professor, ...)', unique=True, max_length=45)),
                ('valor_parametre', models.CharField(max_length=240, blank=True)),
            ],
            options={
                'ordering': ['nom_parametre'],
                'verbose_name': 'Par\xe0metre Kronowin',
                'verbose_name_plural': 'Par\xe0metres Kronowin',
            },
        ),
    ]
