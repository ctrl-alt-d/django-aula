# Generated by Django 2.1.7 on 2019-03-31 15:41

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("missatgeria", "0002_missatge_tipus_de_missatge"),
    ]

    operations = [
        migrations.AlterField(
            model_name="destinatari",
            name="importancia",
            field=models.CharField(
                choices=[
                    ("VI", "Molt important"),
                    ("IN", "Informatiu"),
                    ("PI", "Poc important"),
                ],
                default="IN",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="detallmissatge",
            name="detall",
            field=models.TextField(verbose_name="detall"),
        ),
        migrations.AlterField(
            model_name="detallmissatge",
            name="tipus",
            field=models.CharField(
                choices=[("E", "Error"), ("W", "Avís"), ("I", "Info")],
                default="I",
                max_length=2,
            ),
        ),
        migrations.AlterField(
            model_name="missatge",
            name="text_missatge",
            field=models.TextField(
                help_text="Escriu el missatge", verbose_name="Missatge"
            ),
        ),
    ]
