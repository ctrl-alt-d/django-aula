# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sortides', '0005_sortida_codi_de_barres'),
    ]

    operations = [
        migrations.AddField(
            model_name='sortida',
            name='informacio_pagament',
            field=models.TextField(default='', help_text='Instruccions de pagament: entitat, concepte, import, ... ( el posa secretaria / coordinador(a) activitats )', verbose_name='Informaci\xf3 pagament', blank=True),
        ),
        migrations.AlterField(
            model_name='sortida',
            name='codi_de_barres',
            field=models.CharField(default='', help_text='Codi de barres pagament caixer ( el posa secretaria / coordinador(a) activitats )', max_length=100, verbose_name='Codi de barres pagament', blank=True),
        ),
        migrations.AlterField(
            model_name='sortida',
            name='condicions_generals',
            field=models.TextField(help_text='Aquesta informaci\xf3 arriba a les fam\xedlies. Condicions generals. (m\xe8tode de pagament, entrepans, entrades, comentaris...', blank=True),
        ),
        migrations.AlterField(
            model_name='sortida',
            name='programa_de_la_sortida',
            field=models.TextField(help_text="Aquesta informaci\xf3 arriba a les fam\xedlies. Descriu per als pares el programa de l'activitat: horaris, objectius, pagaments a empreses, recomanacions (crema solar, gorra, insecticida, ...), cal portar (boli, llibreta), altres informacions d'inter\xe8s per a la fam\xedlia. Si no cal portar res cal indicar-ho.", verbose_name="Descripci\xf3 de l'activitat"),
        ),
    ]
