# Generated by Django 3.0.6 on 2020-06-30 22:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sortides', '0026_auto_20200630_2134'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagament',
            name='dataLimit',
            field=models.DateField(null=True),
        ),
    ]
