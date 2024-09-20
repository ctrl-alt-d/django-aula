# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-15 11:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("aules", "0002_auto_20180411_1918"),
    ]

    operations = [
        migrations.AddField(
            model_name="reservaaula",
            name="es_reserva_manual",
            field=models.BooleanField(
                default=False,
                editable=False,
                help_text="la reserva s'ha fet manualment",
            ),
        ),
        migrations.AlterField(
            model_name="aula",
            name="disponibilitat_horaria",
            field=models.ManyToManyField(
                blank=True,
                help_text="Deixar en blanc per a qualsevol hora en que hi hagi doc\xe8ncia al centre.",
                to="horaris.FranjaHoraria",
            ),
        ),
        migrations.AlterField(
            model_name="aula",
            name="horari_lliure",
            field=models.BooleanField(
                default=False, help_text="Permet reserves amb temps fraccionat"
            ),
        ),
    ]
