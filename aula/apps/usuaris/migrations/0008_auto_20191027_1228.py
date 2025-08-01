# Generated by Django 2.2.6 on 2019-10-27 12:28

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("usuaris", "0007_merge_20191023_1150"),
    ]

    operations = [
        migrations.AlterField(
            model_name="accio",
            name="tipus",
            field=models.CharField(
                choices=[
                    ("PL", "Passar llista"),
                    ("LL", "Posar o treure alumnes a la llista"),
                    ("IN", "Posar o treur Incidència"),
                    ("EE", "Editar Expulsió"),
                    ("EC", "Expulsar del Centre"),
                    ("RE", "Recullir expulsió"),
                    ("AC", "Registre Actuació"),
                    ("AG", "Actualitza alumnes des de Saga"),
                    ("MT", "Envia missatge a tutors"),
                    ("SK", "Sincronitza Kronowin"),
                    ("JF", "Justificar Faltes"),
                    ("NF", "Notificacio Families"),
                    ("AS", "Accés a dades sensibles"),
                    ("SU", "Sincronitza Untis"),
                ],
                max_length=2,
            ),
        ),
    ]
