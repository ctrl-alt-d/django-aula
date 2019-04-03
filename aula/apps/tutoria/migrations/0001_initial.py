# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0001_initial'),
        ('usuaris', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actuacio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('moment_actuacio', models.DateTimeField(help_text="Data i Hora de l'actuaci\xf3. Format: 2011-06-01 9:05")),
                ('qui_fa_actuacio', models.CharField(help_text="Qui realitza l'actuaci\xf3", max_length=1, choices=[(b'T', 'Tutor'), (b'C', "Cap d'estudis"), (b'E', 'Equip psicop.'), (b'A', 'Altres')])),
                ('amb_qui_es_actuacio', models.CharField(help_text="Sobre qui es realitza l'actuaci\xf3", max_length=1, choices=[(b'A', 'alumnes.Alumne'), (b'F', 'Familia'), (b'T', 'Altres')])),
                ('assumpte', models.CharField(help_text='Assumpte', max_length=200)),
                ('actuacio', models.TextField(help_text="Explicaci\xf3 detallada de l'actuaci\xf3 realitzada. No inclogueu dades m\xe8diques ni diagn\xf2stiques.", blank=True)),
                ('alumne', models.ForeignKey(help_text="Alumne sobre el qual es fa l'actuaci\xf3", to='alumnes.Alumne', on_delete=models.CASCADE)),
                ('professional', models.ForeignKey(blank=True, to='usuaris.Professional', help_text="Professional que fa l'actuacio", null=True, on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Actuaci\xf3',
                'verbose_name_plural': 'Actuacions',
            },
        ),
        migrations.CreateModel(
            name='CartaAbsentisme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('carta_numero', models.IntegerField(verbose_name='Av\xeds n\xfamero', editable=False)),
                ('tipus_carta', models.CharField(max_length=10, editable=False)),
                ('faltes_fins_a_data', models.DateField(verbose_name=b'Faltes fins a data', editable=False)),
                ('data_carta', models.DateField(verbose_name=b'Data de la carta')),
                ('faltes_incloses', models.TextField(verbose_name=b'Faltes incloses a la carta', editable=False, blank=True)),
                ('carta_esborrada_moment', models.DateTimeField(null=True, editable=False, blank=True)),
                ('nfaltes', models.IntegerField(verbose_name='Abs\xe8ncies injustificades', editable=False)),
                ('impresa', models.BooleanField(default=False, editable=False)),
                ('alumne', models.ForeignKey(verbose_name='Alumne', to='alumnes.Alumne', on_delete=models.CASCADE)),
                ('professor', models.ForeignKey(verbose_name=b'Professor que signa la carta', to='usuaris.Professor', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['alumne', 'carta_numero'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ResumAnualAlumne',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('curs_any_inici', models.IntegerField()),
                ('text_resum', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Resum Anual Alumne',
                'verbose_name_plural': 'Resums Anuals Alumnes',
            },
        ),
        migrations.CreateModel(
            name='SeguimentTutorial',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=240)),
                ('cognoms', models.CharField(max_length=240)),
                ('datadarreraactualitzacio', models.DateTimeField(null=True, blank=True)),
                ('data_neixement', models.DateField()),
                ('informacio_de_primaria', models.TextField(blank=True)),
                ('alumne', models.OneToOneField(null=True, to='alumnes.Alumne', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Cap\xe7alera seguiment tutorial',
                'verbose_name_plural': 'Cap\xe7aleres seguiment tutorial',
            },
        ),
        migrations.CreateModel(
            name='SeguimentTutorialPreguntes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pregunta', models.CharField(unique=True, max_length=250)),
                ('ajuda_pregunta', models.CharField(max_length=250, blank=True)),
                ('es_pregunta_oberta', models.BooleanField()),
                ('possibles_respostes', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Pregunta seguiment tutorial',
                'verbose_name_plural': 'Preguntes seguiment tutorial',
            },
        ),
        migrations.CreateModel(
            name='SeguimentTutorialRespostes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('any_curs_academic', models.IntegerField()),
                ('pregunta', models.CharField(max_length=250)),
                ('resposta', models.TextField()),
                ('ordre', models.IntegerField(default=100)),
                ('professorQueInforma', models.CharField(default=b'', max_length=200, blank=True)),
                ('seguiment_tutorial', models.ForeignKey(to='tutoria.SeguimentTutorial', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Resposta de seguiment tutorial',
                'verbose_name_plural': 'Respostes de seguiment tutorial',
            },
        ),
        migrations.CreateModel(
            name='Tutor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grup', models.ForeignKey(to='alumnes.Grup', on_delete=models.CASCADE)),
                ('professor', models.ForeignKey(to='usuaris.Professor', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Entrada taula Tutors',
                'verbose_name_plural': 'Entrades taula Tutors',
            },
        ),
        migrations.CreateModel(
            name='TutorIndividualitzat',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('alumne', models.ForeignKey(to='alumnes.Alumne', on_delete=models.CASCADE)),
                ('professor', models.ForeignKey(to='usuaris.Professor', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Entrada Tutors Individualitzats',
                'verbose_name_plural': 'Entrades Tutors Individualitzats',
            },
        ),
        migrations.AddField(
            model_name='resumanualalumne',
            name='seguiment_tutorial',
            field=models.ForeignKey(to='tutoria.SeguimentTutorial', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='tutorindividualitzat',
            unique_together=set([('professor', 'alumne')]),
        ),
        migrations.AlterUniqueTogether(
            name='tutor',
            unique_together=set([('professor', 'grup')]),
        ),
        migrations.AlterUniqueTogether(
            name='seguimenttutorialrespostes',
            unique_together=set([('seguiment_tutorial', 'any_curs_academic', 'pregunta')]),
        ),
        migrations.AlterUniqueTogether(
            name='seguimenttutorial',
            unique_together=set([('nom', 'cognoms', 'data_neixement')]),
        ),
    ]
