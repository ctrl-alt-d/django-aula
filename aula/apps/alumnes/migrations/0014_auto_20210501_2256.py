# Generated by Django 3.2 on 2021-05-01 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alumnes", "0013_alumne_observacions"),
    ]

    operations = [
        migrations.CreateModel(
            name="AlumneNomSentit",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("alumnes.alumne",),
        ),
        migrations.CreateModel(
            name="AlumneNomSentitGrup",
            fields=[],
            options={
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("alumnes.alumne",),
        ),
        migrations.AddField(
            model_name="alumne",
            name="nom_sentit",
            field=models.CharField(
                blank=True,
                help_text="És el nom amb el que l'alumne se sent identificat tot i que formalment encara els tràmits de canvi de nom no estiguin completats",
                max_length=240,
                verbose_name="Nom Sentit",
            ),
        ),
    ]
