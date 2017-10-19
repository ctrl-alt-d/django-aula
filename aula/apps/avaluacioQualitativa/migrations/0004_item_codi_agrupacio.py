# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaluacioQualitativa', '0003_control_notificacio_families'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='itemqualitativa',
            options={'ordering': ['codi_agrupacio', 'text'], 'verbose_name': 'Frase aval. qualitativa', 'verbose_name_plural': 'Frases aval. qualitativa'},
        ),
        migrations.AddField(
            model_name='itemqualitativa',
            name='codi_agrupacio',
            field=models.CharField(help_text="Codi per facilitar l'entrada de la qualitativa. No apareix a l'informe a les fam\xedlies.", max_length=10, verbose_name='Codi agrupaci\xf3', blank=True),
        ),
    ]
