# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractOneTimePasswd',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('moment_expedicio', models.DateTimeField(auto_now_add=True)),
                ('clau', models.CharField(max_length=40)),
                ('reintents', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Accio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipus', models.CharField(max_length=2, choices=[(b'PL', b'Passar llista'), (b'LL', b'Posar o treure alumnes a la llista'), (b'IN', b'Posar o treur Incid\xc3\xa8ncia'), (b'EE', b'Editar Expulsi\xc3\xb3'), (b'EC', b'Expulsar del Centre'), (b'RE', b'Recullir expulsi\xc3\xb3'), (b'AC', b'Registre Actuaci\xc3\xb3'), (b'AG', b'Actualitza alumnes des de Saga'), (b'MT', b'Envia missatge a tutors'), (b'SK', b'Sincronitza Kronowin'), (b'JF', b'Justificar Faltes'), (b'NF', b'Notificacio Families')])),
                ('moment', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('l4', models.BooleanField(default=False)),
                ('text', models.TextField()),
            ],
            options={
                'abstract': False,
                'verbose_name': "Acci\xf3 d'usuari",
                'verbose_name_plural': "Accions d'usuari",
            },
        ),
        migrations.CreateModel(
            name='Departament',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('codi', models.CharField(max_length=4)),
                ('nom', models.CharField(max_length=300)),
            ],
            options={
                'ordering': ['nom'],
                'abstract': False,
                'verbose_name': 'Departament Did\xe0ctic',
                'verbose_name_plural': 'Departaments Did\xe0ctics',
            },
        ),
        migrations.CreateModel(
            name='LoginUsuari',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('exitos', models.BooleanField()),
                ('moment', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('ip', models.CharField(max_length=15, blank=True)),
            ],
            options={
                'ordering': ['usuari', '-moment'],
                'abstract': False,
                'verbose_name': "Login d'usuari",
                'verbose_name_plural': "Login d'usuari",
            },
        ),
        migrations.CreateModel(
            name='AlumneUser',
            fields=[
            ],
            options={
                'ordering': ['last_name', 'first_name', 'username'],
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Professional',
            fields=[
            ],
            options={
                'ordering': ['last_name', 'first_name', 'username'],
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='Professor',
            fields=[
            ],
            options={
                'ordering': ['last_name', 'first_name', 'username'],
                'proxy': True,
            },
            bases=('auth.user',),
        ),
        migrations.CreateModel(
            name='OneTimePasswd',
            fields=[
                ('abstractonetimepasswd_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='usuaris.AbstractOneTimePasswd', on_delete=models.CASCADE)),
            ],
            bases=('usuaris.abstractonetimepasswd',),
        ),
        migrations.AddField(
            model_name='loginusuari',
            name='usuari',
            field=models.ForeignKey(related_name='LoginUsuari', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='accio',
            name='impersonated_from',
            field=models.ForeignKey(related_name='impersonate_from', blank=True, to=settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='accio',
            name='usuari',
            field=models.ForeignKey(related_name='usuari', to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='abstractonetimepasswd',
            name='usuari',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE),
        ),
    ]
