# Generated by Django 2.2 on 2020-10-21 10:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('avaluacioQualitativa', '0004_item_codi_agrupacio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avaluacioqualitativa',
            name='data_obrir_avaluacio',
            field=models.DateField(help_text="Data a partir de la qual els professors podran entrar l'avaluació.", verbose_name='Primer dia per entrar Qualitativa'),
        ),
        migrations.AlterField(
            model_name='avaluacioqualitativa',
            name='data_tancar_avaluacio',
            field=models.DateField(help_text='Darrer dia que tenen els professors per entrar la Qualitativa.', verbose_name='Darrer dia per entrar Qualitativa'),
        ),
    ]