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
            name='AvaluacioQualitativa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom_avaluacio', models.CharField(help_text='Ex: Avaluaci\xf3 qualitativa 1ra Avaluaci\xf3', unique=True, max_length=120, verbose_name='Avaluaci\xf3 Qualitativa')),
                ('data_obrir_avaluacio', models.DateField(help_text="Data a partir de la qual els professors podran entrar l'avaluaci\xf3.", unique=True, verbose_name='Primer dia per entrar Qualitativa')),
                ('data_tancar_avaluacio', models.DateField(help_text='Darrer dia que tenen els professors per entrar la Qualitativa.', unique=True, verbose_name='Darrer dia per entrar Qualitativa')),
                ('grups', models.ManyToManyField(help_text='Tria els grups a avaluar.', to='alumnes.Grup')),
            ],
            options={
                'ordering': ['data_obrir_avaluacio'],
                'abstract': False,
                'verbose_name': 'Avaluaci\xf3 Qualitativa',
                'verbose_name_plural': 'Avaluacions Qualitatives',
            },
        ),
        migrations.CreateModel(
            name='ItemQualitativa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(help_text="Important: No canvieu mai el significat d'una frase! Canviarieu els resultats de l'avaulaci\xf3.", unique=True, max_length=120, verbose_name='Item de la Qualitativa')),
                ('nivells', models.ManyToManyField(help_text='Tria els nivells on aquesta frase pot apar\xe8ixer.', to='alumnes.Nivell')),
            ],
            options={
                'ordering': ['text'],
                'abstract': False,
                'verbose_name': 'Frase aval. qualitativa',
                'verbose_name_plural': 'Frases aval. qualitativa',
            },
        ),
        migrations.CreateModel(
            name='RespostaAvaluacioQualitativa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frase_oberta', models.CharField(help_text='Frase oberta', max_length=120, verbose_name='Frase oberta', blank=True)),
                ('alumne', models.ForeignKey(to='alumnes.Alumne', on_delete=models.CASCADE)),
                ('assignatura', models.ForeignKey(to='assignatures.Assignatura', on_delete=models.CASCADE)),
                ('item', models.ForeignKey(blank=True, to='avaluacioQualitativa.ItemQualitativa', null=True, on_delete=models.CASCADE)),
                ('professor', models.ForeignKey(to='usuaris.Professor', on_delete=models.CASCADE)),
                ('qualitativa', models.ForeignKey(to='avaluacioQualitativa.AvaluacioQualitativa', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['qualitativa', 'assignatura', 'alumne'],
                'abstract': False,
                'verbose_name': 'Resposta aval. Qualitativa',
                'verbose_name_plural': 'Respostes aval. Qualitative',
            },
        ),
        migrations.AlterUniqueTogether(
            name='respostaavaluacioqualitativa',
            unique_together=set([('qualitativa', 'assignatura', 'alumne', 'professor', 'item')]),
        ),
    ]
