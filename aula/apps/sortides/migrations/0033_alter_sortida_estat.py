# Generated by Django 3.2.18 on 2024-02-09 17:57

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("sortides", "0032_rename_titol_de_la_sortida_sortida_titol"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sortida",
            name="estat",
            field=models.CharField(
                choices=[
                    ("E", "Esborrany"),
                    ("P", "Proposat/da"),
                    ("R", "Revisat/da pel Coordinador"),
                    ("G", "Gestionat/da pel Cap d'estudis"),
                ],
                default="E",
                help_text="Estat de l'activitat. No es considera proposta d'activitat fins que no passa a estat 'Proposada'",
                max_length=1,
            ),
        ),
    ]
