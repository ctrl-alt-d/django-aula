# Generated by Django 2.2.3 on 2019-10-14 11:18

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("extUntis", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="agrupament",
            options={
                "ordering": ["grup_alumnes", "grup_horari"],
                "verbose_name": "Agrupament grups alumnes i grups horari",
                "verbose_name_plural": "Agrupaments grups alumnes i grups horari",
            },
        ),
    ]
