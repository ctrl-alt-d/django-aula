# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('incidencies', '0001_initial'),
        ('sortides', '0003_auto_20160226_1731'),
        ('presencia', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NoHaDeSerALAula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('motiu', models.CharField(max_length=5, choices=[(b'E', 'Expulsat del centre'), (b'A', 'Activitat')])),
                ('control', models.ForeignKey(to='presencia.ControlAssistencia', on_delete=models.CASCADE)),
                ('sancio', models.ForeignKey(blank=True, to='incidencies.Sancio', null=True, on_delete=models.CASCADE)),
                ('sortida', models.ForeignKey(blank=True, to='sortides.Sortida', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Motiu no ha est\xe0 pressent',
                'verbose_name_plural': "Motius no pres\xe8ncia a l'aula",
            },
        ),
    ]
