# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignatura',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codi_assignatura', models.CharField(max_length=45)),
                ('nom_assignatura', models.CharField(max_length=250, blank=True)),
                ('curs', models.ForeignKey(blank=True, to='alumnes.Curs', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Assignatura',
                'verbose_name_plural': 'Assignatures',
            },
        ),
        migrations.CreateModel(
            name='TipusDAssignatura',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipus_assignatura', models.CharField(unique=True, max_length=45)),
                ('ambit_on_prendre_alumnes', models.CharField(default=b'G', max_length=45, choices=[(b'G', b'Grup'), (b'C', b'Curs'), (b'N', b'Nivell'), (b'I', b'Institut'), (b'X', b'No Admet alumnes (Ex: G)')])),
            ],
            options={
                'abstract': False,
                'verbose_name': "Tipus d'assignatura",
                'verbose_name_plural': "Tipus d'assignatura",
            },
        ),
        migrations.AddField(
            model_name='assignatura',
            name='tipus_assignatura',
            field=models.ForeignKey(blank=True, to='assignatures.TipusDAssignatura', null=True, on_delete=models.CASCADE),
        ),
    ]
