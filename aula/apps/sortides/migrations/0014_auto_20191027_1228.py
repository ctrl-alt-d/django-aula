# Generated by Django 2.2.6 on 2019-10-27 12:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sortides", "0013_auto_20190331_1541"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sortida",
            name="tipus_de_pagament",
            field=models.CharField(
                choices=[
                    ("NO", "No cal pagament"),
                    ("EF", "En efectiu"),
                    ("ON", "Online a través del dJau"),
                    ("EB", "Al caixer de l'entitat bancària"),
                ],
                default="EB",
                help_text="Quin serà el tipus de pagament predominant",
                max_length=2,
            ),
        ),
    ]
