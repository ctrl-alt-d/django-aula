# Generated by Django 2.2 on 2020-05-24 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("alumnes", "0012_alumne_primer_responsable"),
    ]

    operations = [
        migrations.AddField(
            model_name="alumne",
            name="observacions",
            field=models.TextField(
                blank=True,
                help_text="Informació visible pels seus professors/es",
                max_length=150,
                null=True,
            ),
        ),
    ]
