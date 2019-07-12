# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuaris', '__first__'),
        ('horaris', '0001_initial'),
        ('alumnes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ControlAssistencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('swaped', models.BooleanField(default=False)),
                ('relacio_familia_revisada', models.DateTimeField(null=True)),
                ('relacio_familia_notificada', models.DateTimeField(null=True)),
                ('alumne', models.ForeignKey(to='alumnes.Alumne', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': "Entrada al Control d'Assistencia",
                'verbose_name_plural': "Entrades al Control d'Assistencia",
            },
        ),
        migrations.CreateModel(
            name='EstatControlAssistencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codi_estat', models.CharField(unique=True, max_length=1)),
                ('nom_estat', models.CharField(unique=True, max_length=45)),
                ('pct_ausencia', models.IntegerField(default=0, help_text="100=Falta tota l'hora, 0=No \xe9s falta assist\xe8ncia. Aquest camp serveix per que els retrassos es puguin comptar com a falta o com un percentatge de falta.")),
            ],
            options={
                'abstract': False,
                'verbose_name': "Estat control d'assistencia",
                'verbose_name_plural': "Estats control d'assistencia",
            },
        ),
        migrations.CreateModel(
            name='Impartir',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dia_impartir', models.DateField(db_index=True)),
                ('dia_passa_llista', models.DateTimeField(null=True, blank=True)),
                ('comentariImpartir', models.TextField(default=b'', blank=True)),
                ('pot_no_tenir_alumnes', models.BooleanField(default=False)),
                ('horari', models.ForeignKey(to='horaris.Horari', on_delete=models.CASCADE)),
                ('professor_guardia', models.ForeignKey(related_name='professor_guardia', blank=True, to='usuaris.Professor', null=True, on_delete=models.CASCADE)),
                ('professor_passa_llista', models.ForeignKey(related_name='professor_passa_llista', blank=True, to='usuaris.Professor', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Impartir classe',
                'verbose_name_plural': 'Impartir classes',
            },
        ),
        migrations.AddField(
            model_name='controlassistencia',
            name='estat',
            field=models.ForeignKey(blank=True, to='presencia.EstatControlAssistencia', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='controlassistencia',
            name='estat_backup',
            field=models.ForeignKey(related_name='controlassistencia_as_bkup', blank=True, to='presencia.EstatControlAssistencia', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='controlassistencia',
            name='impartir',
            field=models.ForeignKey(to='presencia.Impartir', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='controlassistencia',
            name='professor',
            field=models.ForeignKey(blank=True, to='usuaris.Professor', null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='controlassistencia',
            name='professor_backup',
            field=models.ForeignKey(related_name='controlassistencia_as_bkup', blank=True, to='usuaris.Professor', null=True, on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='impartir',
            unique_together=set([('dia_impartir', 'horari')]),
        ),
        migrations.AlterUniqueTogether(
            name='controlassistencia',
            unique_together=set([('alumne', 'impartir')]),
        ),
    ]
