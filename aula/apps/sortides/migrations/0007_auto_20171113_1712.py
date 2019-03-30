# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sortides', '0006_sortida_info_pagament'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sortida',
            name='calendari_desde',
            field=models.DateTimeField(help_text="Horari real de l'activitat, hora de sortida, aquest horari, a m\xe9s, es publicar\xe0 al calendari del Centre", verbose_name='Horari real, desde:'),
        ),
        migrations.AlterField(
            model_name='sortida',
            name='calendari_finsa',
            field=models.DateTimeField(help_text="Horari real de l'activitat, hora de tornada, aquest horari, a m\xe9s, es publicar\xe0 al calendari del Centre", verbose_name='Horari real, fins a:'),
        ),
        migrations.AlterField(
            model_name='sortida',
            name='data_fi',
            field=models.DateField(help_text="Darrer dia  lectiu de l'activitat", null=True, verbose_name='Afecta classes: Fins a', blank=True),
        ),
        migrations.AlterField(
            model_name='sortida',
            name='data_inici',
            field=models.DateField(help_text="Primer dia lectiu afectat per l'activitat", null=True, verbose_name='Afecta classes: Des de', blank=True),
        ),
        migrations.AlterField(
            model_name='sortida',
            name='franja_fi',
            field=models.ForeignKey(related_name='hora_fi_sortida', blank=True, to='horaris.FranjaHoraria', help_text="Darrera franja lectiva afectatada per l'activitat", null=True, verbose_name='Afecta classes: fins a franja', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='sortida',
            name='franja_inici',
            field=models.ForeignKey(related_name='hora_inici_sortida', blank=True, to='horaris.FranjaHoraria', help_text="Primera franja lectiva afectada per l'activitat", null=True, verbose_name='Afecta classes: Des de franja', on_delete=models.CASCADE),
        ),
    ]
