# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuaris', '0001_initial'),
        ('presencia', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feina',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('feina_a_fer', models.TextField(help_text='Explicar on el professor de guardia pot trobar la feina que han de fer els alumnes aquestes dies.', blank=True)),
                ('comentaris_per_al_professor_guardia', models.TextField(help_text='Comentaris per al professor que fa la gu\xe0rdia, guardia que substitueix en cas necessari.', blank=True)),
                ('comentaris_professor_guardia', models.TextField(blank=True)),
                ('impartir', models.OneToOneField(to='presencia.Impartir', on_delete=models.CASCADE)),
                ('professor_darrera_modificacio', models.ForeignKey(related_name='feina_professor_audit_set', to='usuaris.Professor', on_delete=models.CASCADE)),
                ('professor_fa_guardia', models.ForeignKey(related_name='feina_professor_guardia_set', blank=True, to='usuaris.Professor', help_text='Professor que far\xe0 la gu\xe0rdia.', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ('impartir__dia_impartir', 'impartir__horari__hora__hora_inici'),
                'abstract': False,
                'verbose_name': 'Feina baixa',
                'verbose_name_plural': 'Feines baixa',
            },
        ),
    ]
