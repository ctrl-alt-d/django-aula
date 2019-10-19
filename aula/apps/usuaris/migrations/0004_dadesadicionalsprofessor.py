# Generated by Django 2.2.5 on 2019-09-15 00:21

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('usuaris', '0003_auto_20190331_1541'),
    ]

    operations = [
        migrations.CreateModel(
            name='DadesAddicionalsProfessor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('clauDeCalendari', models.UUIDField(default=uuid.uuid4)),
                ('professor', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='usuaris.Professor')),
            ],
        ),
    ]