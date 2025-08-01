# -*- coding: utf-8 -*-
# Generated by Django 1.11.12 on 2018-04-16 10:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("aules", "0003_auto_20180415_1128"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="reservaaula",
            options={"ordering": ["dia_reserva", "hora"]},
        ),
        migrations.AddIndex(
            model_name="reservaaula",
            index=models.Index(
                fields=["dia_reserva", "hora"], name="aules_reser_dia_res_ca4f83_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="reservaaula",
            index=models.Index(
                fields=["es_reserva_manual", "usuari", "dia_reserva", "hora"],
                name="aules_reser_es_rese_70dfd6_idx",
            ),
        ),
    ]
