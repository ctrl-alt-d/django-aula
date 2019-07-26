# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ToDo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateTimeField(default=django.utils.timezone.now, db_index=True)),
                ('tasca', models.CharField(help_text='Tasca a realitzar', max_length=100)),
                ('informacio_adicional', models.TextField(help_text='Informaci\xf3 adicional', verbose_name=b'Informaci\xc3\xb3 adicional')),
                ('estat', models.CharField(default=b'P', max_length=2, choices=[(b'P', b'Pendent'), (b'R', b'Realitzat')])),
                ('prioritat', models.CharField(blank=True, max_length=2, choices=[(b'V', b'Molt Important'), (b'P', b'Poc Inportant')])),
                ('enllac', models.URLField(blank=True)),
                ('propietari', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['-data'],
                'verbose_name': 'Llista de tasques',
                'verbose_name_plural': 'Llista de tasques',
            },
        ),
    ]
