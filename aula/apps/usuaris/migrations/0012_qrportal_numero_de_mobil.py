# Generated by Django 3.2.18 on 2023-04-13 00:23

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("usuaris", "0011_qrportal"),
    ]

    operations = [
        migrations.AddField(
            model_name="qrportal",
            name="numero_de_mobil",
            field=models.CharField(blank=True, max_length=40),
        ),
    ]
