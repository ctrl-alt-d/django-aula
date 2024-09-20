# Generated by Django 2.2.6 on 2020-02-16 23:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sortides", "0020_merge_20200216_2333"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sortida",
            name="ciutat",
            field=models.CharField(
                help_text="On es fa l'activitat. Ex. Sala polivalent, Aula 201, Teatre el Jardí, Barcelona,,...",
                max_length=30,
                verbose_name="Lloc",
            ),
        ),
        migrations.AlterField(
            model_name="sortida",
            name="tipus_de_pagament",
            field=models.CharField(
                choices=[
                    ("NO", "No cal pagament"),
                    ("EF", "En efectiu"),
                    ("ON", "Online a través del djAu"),
                ],
                default="ON",
                help_text="Quin serà el tipus de pagament predominant",
                max_length=2,
            ),
        ),
    ]
