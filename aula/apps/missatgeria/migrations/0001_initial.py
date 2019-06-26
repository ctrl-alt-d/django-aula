# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Destinatari',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('importancia', models.CharField(default=b'IN', max_length=2, choices=[(b'VI', b'Molt important'), (b'IN', b'Informatiu'), (b'PI', b'Poc important')])),
                ('moment_lectura', models.DateTimeField(db_index=True, null=True, blank=True)),
                ('followed', models.BooleanField(default=False)),
                ('destinatari', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Lectura de missatge',
                'verbose_name_plural': 'Lectures de missatges',
            },
        ),
        migrations.CreateModel(
            name='DetallMissatge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('detall', models.TextField(verbose_name=b'detall')),
                ('tipus', models.CharField(default=b'I', max_length=2, choices=[(b'E', b'Error'), (b'W', b'Av\xc3\xads'), (b'I', b'Info')])),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Detall del missatge',
                'verbose_name_plural': 'Detalls del missatge',
            },
        ),
        migrations.CreateModel(
            name='Missatge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('text_missatge', models.TextField(help_text='Escriu el missatge', verbose_name=b'Missatge')),
                ('enllac', models.URLField(blank=True)),
                ('remitent', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Missatge',
                'verbose_name_plural': 'Missatges',
            },
        ),
        migrations.AddField(
            model_name='detallmissatge',
            name='missatge',
            field=models.ForeignKey(to='missatgeria.Missatge', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='destinatari',
            name='missatge',
            field=models.ForeignKey(to='missatgeria.Missatge', on_delete=models.CASCADE),
        ),
    ]
