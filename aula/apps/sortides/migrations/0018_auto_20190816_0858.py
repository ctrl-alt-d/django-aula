# Generated by Django 2.2 on 2019-08-16 08:58

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sortides", "0017_pagament_ordre_pagament"),
    ]

    operations = [
        migrations.AlterField(
            model_name="pagament",
            name="data_hora_pagament",
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name="pagament",
            name="pagament_realitzat",
            field=models.BooleanField(default=False, null=True),
        ),
    ]
