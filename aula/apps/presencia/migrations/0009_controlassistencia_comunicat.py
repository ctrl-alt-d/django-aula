# Generated by Django 3.2.9 on 2021-11-27 20:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("missatgeria", "0003_auto_20190331_1541"),
        ("presencia", "0008_auto_20191020_0114"),
    ]

    operations = [
        migrations.AddField(
            model_name="controlassistencia",
            name="comunicat",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                to="missatgeria.missatge",
            ),
        ),
    ]
