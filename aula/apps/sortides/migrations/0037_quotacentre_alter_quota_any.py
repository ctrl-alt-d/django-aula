# Generated by Django 5.0.4 on 2024-04-27 18:04

import aula.apps.sortides.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sortides', '0036_alter_sortida_empresa_de_transport_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuotaCentre',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=('sortides.quota',),
        ),
        migrations.AlterField(
            model_name='quota',
            name='any',
            field=models.IntegerField(default=aula.apps.sortides.models.return_any_actual, help_text="Correspon a l'any on comença el curs. Ex. curs any1/any2, seria any1."),
        ),
    ]