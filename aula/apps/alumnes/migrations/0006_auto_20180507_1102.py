# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-05-07 11:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("alumnes", "0005_auto_20171025_1830"),
    ]

    operations = [
        migrations.AddField(
            model_name="alumne",
            name="altres_telefons",
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name="alumne",
            name="correu",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name="alumne",
            name="rp1_correu",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name="alumne",
            name="rp1_mobil",
            field=models.CharField(blank=True, db_index=True, max_length=250),
        ),
        migrations.AddField(
            model_name="alumne",
            name="rp1_nom",
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name="alumne",
            name="rp1_telefon",
            field=models.CharField(blank=True, db_index=True, max_length=250),
        ),
        migrations.AddField(
            model_name="alumne",
            name="rp2_correu",
            field=models.CharField(blank=True, max_length=240),
        ),
        migrations.AddField(
            model_name="alumne",
            name="rp2_mobil",
            field=models.CharField(blank=True, db_index=True, max_length=250),
        ),
        migrations.AddField(
            model_name="alumne",
            name="rp2_nom",
            field=models.CharField(blank=True, max_length=250),
        ),
        migrations.AddField(
            model_name="alumne",
            name="rp2_telefon",
            field=models.CharField(blank=True, db_index=True, max_length=250),
        ),
    ]
