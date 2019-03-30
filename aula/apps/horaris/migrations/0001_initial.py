# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0001_initial'),
        ('assignatures', '0001_initial'),
        ('usuaris', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiaDeLaSetmana',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('n_dia_uk', models.IntegerField(unique=True, verbose_name='N\xfamero de dia de la setmana a UK (0=diumenge)')),
                ('n_dia_ca', models.IntegerField(unique=True, verbose_name='N\xfamero de dia de la setmana aqu\xed (0=dilluns)')),
                ('dia_2_lletres', models.CharField(unique=True, max_length=6, verbose_name=b'Dia')),
                ('dia_de_la_setmana', models.CharField(unique=True, max_length=45, verbose_name=b'Dia de la setmana')),
                ('es_festiu', models.BooleanField(verbose_name='\xc9s festiu?')),
            ],
            options={
                'ordering': ['n_dia_ca'],
                'abstract': False,
                'verbose_name': 'Dia de la Setmana',
                'verbose_name_plural': 'Dies de la Setmana',
            },
        ),
        migrations.CreateModel(
            name='Festiu',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_inici_festiu', models.DateField()),
                ('data_fi_festiu', models.DateField()),
                ('descripcio', models.CharField(max_length=45)),
                ('curs', models.ForeignKey(blank=True, to='alumnes.Curs', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['data_inici_festiu', 'franja_horaria_inici'],
                'abstract': False,
                'verbose_name': 'Entrada al calendari de festius',
                'verbose_name_plural': 'Entrades al calendari de festius',
            },
        ),
        migrations.CreateModel(
            name='FranjaHoraria',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hora_inici', models.TimeField(unique=True)),
                ('hora_fi', models.TimeField(unique=True)),
                ('nom_franja', models.CharField(max_length=45, blank=True)),
            ],
            options={
                'ordering': ['hora_inici'],
                'abstract': False,
                'verbose_name': 'Franja Hor\xe0ria',
                'verbose_name_plural': 'Franges Hor\xe0ries',
            },
        ),
        migrations.CreateModel(
            name='Horari',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom_aula', models.CharField(max_length=45, blank=True)),
                ('es_actiu', models.BooleanField()),
                ('estat_sincronitzacio', models.CharField(max_length=3, blank=True)),
                ('assignatura', models.ForeignKey(blank=True, to='assignatures.Assignatura', null=True, on_delete=models.CASCADE)),
                ('dia_de_la_setmana', models.ForeignKey(to='horaris.DiaDeLaSetmana', on_delete=models.CASCADE)),
                ('grup', models.ForeignKey(blank=True, to='alumnes.Grup', null=True, on_delete=models.CASCADE)),
                ('hora', models.ForeignKey(to='horaris.FranjaHoraria', on_delete=models.CASCADE)),
                ('professor', models.ForeignKey(blank=True, to='usuaris.Professor', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['es_actiu', 'professor', 'dia_de_la_setmana__n_dia_ca', 'hora__hora_inici'],
                'abstract': False,
                'verbose_name': "Entrada a l'Horari",
                'verbose_name_plural': "Entrades a l'Horari",
            },
        ),
        migrations.AddField(
            model_name='festiu',
            name='franja_horaria_fi',
            field=models.ForeignKey(related_name='hora_fi_festiu', to='horaris.FranjaHoraria', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='festiu',
            name='franja_horaria_inici',
            field=models.ForeignKey(related_name='hora_inici_festiu', to='horaris.FranjaHoraria', on_delete=models.CASCADE),
        ),
    ]
