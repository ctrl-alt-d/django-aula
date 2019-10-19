# Generated by Django 2.2.3 on 2019-09-22 20:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuaris', '0004_dadesadicionalsprofessor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accio',
            name='tipus',
            field=models.CharField(choices=[('PL', 'Passar llista'), ('LL', 'Posar o treure alumnes a la llista'), ('IN', 'Posar o treur Incidència'), ('EE', 'Editar Expulsió'), ('EC', 'Expulsar del Centre'), ('RE', 'Recullir expulsió'), ('AC', 'Registre Actuació'), ('AG', 'Actualitza alumnes des de Saga'), ('MT', 'Envia missatge a tutors'), ('SK', 'Sincronitza Kronowin'), ('JF', 'Justificar Faltes'), ('NF', 'Notificacio Families'), ('SU', 'Sincronitza Untis')], max_length=2),
        ),
    ]