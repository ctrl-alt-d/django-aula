# Generated by Django 4.0.2 on 2022-07-17 13:05

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("alumnes", "0016_merge_20210830_1954"),
    ]

    operations = [
        migrations.AddField(
            model_name="nivell",
            name="preexclusiva",
            field=models.BooleanField(
                default=False, verbose_name="Matrícula exclusiva de Preinscripció"
            ),
        ),
    ]
