# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('usuaris', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alumne',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(max_length=240, verbose_name=b'Nom')),
                ('cognoms', models.CharField(max_length=240, verbose_name=b'Cognoms')),
                ('data_neixement', models.DateField(null=True)),
                ('estat_sincronitzacio', models.CharField(blank=True, max_length=3, choices=[(b'PRC', b'En proc\xc3\xa9s de sincronitzaci\xc3\xb3'), (b'S-I', b'Sincronitzat Insert'), (b'S-U', b'Sincronitzat Update'), (b'DEL', b'Alumne donat de baixa'), (b'MAN', b"Alumne donat d'alta manualment")])),
                ('correu_tutors', models.CharField(max_length=240, blank=True)),
                ('correu_relacio_familia_pare', models.EmailField(help_text='Correu de notificacions de un tutor', max_length=254, verbose_name='1r Correu Notifi. Tutors', blank=True)),
                ('correu_relacio_familia_mare', models.EmailField(help_text="Correu de notificacions de l'altre tutor (opcional)", max_length=254, verbose_name='2n Correu Notifi. Tutors', blank=True)),
                ('motiu_bloqueig', models.CharField(max_length=250, blank=True)),
                ('tutors_volen_rebre_correu', models.BooleanField()),
                ('centre_de_procedencia', models.CharField(max_length=250, blank=True)),
                ('localitat', models.CharField(max_length=240, blank=True)),
                ('telefons', models.CharField(db_index=True, max_length=250, blank=True)),
                ('tutors', models.CharField(max_length=250, blank=True)),
                ('adreca', models.CharField(max_length=250, blank=True)),
                ('data_alta', models.DateField(default=django.utils.timezone.now)),
                ('data_baixa', models.DateField(null=True, blank=True)),
                ('relacio_familia_darrera_notificacio', models.DateTimeField(null=True, blank=True)),
                ('periodicitat_faltes', models.IntegerField(default=3, help_text='Interval de temps m\xednim entre dues notificacions', choices=[(0, b'No notificar'), (1, b'Un dia'), (2, b'Dos dies'), (3, b'Tres dies'), (7, b'Una setmana')])),
                ('periodicitat_incidencies', models.BooleanField(default=True, help_text='Periodicitat en la notificaci\xf3 de les incid\xe8ncies.', choices=[(False, b'No notificar.'), (True, b'Notificar-les totes.')])),
            ],
            options={
                'ordering': ['grup', 'cognoms', 'nom'],
                'abstract': False,
                'verbose_name': 'Alumne',
                'verbose_name_plural': 'Alumnes',
            },
        ),
        migrations.CreateModel(
            name='Curs',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom_curs', models.CharField(help_text='Un n\xfamero que representa el curs (Ex: 3)', max_length=45, verbose_name=b'Nom curs')),
                ('nom_curs_complert', models.CharField(help_text='Dades que es mostraran (Ex: 1r ESO)', unique=True, max_length=45, blank=True)),
                ('data_inici_curs', models.DateField(help_text='Dia que comencen les classes (cal informar aquest cap per poder fer control de pres\xe8ncia)', null=True, verbose_name=b'Comencen', blank=True)),
                ('data_fi_curs', models.DateField(help_text="Dia que finalitzen les classes (es poden posar dies festius a l'apartat corresponent)", null=True, verbose_name=b'Acaben', blank=True)),
            ],
            options={
                'ordering': ['nivell', 'nom_curs'],
                'abstract': False,
                'verbose_name': 'Curs',
                'verbose_name_plural': 'Cursos',
            },
        ),
        migrations.CreateModel(
            name='Grup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom_grup', models.CharField(help_text="Aix\xf2 normalment ser\xe0 una lletra. Ex 'A' ", max_length=45)),
                ('descripcio_grup', models.CharField(max_length=240, blank=True)),
                ('curs', models.ForeignKey(to='alumnes.Curs', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['curs', 'curs__nivell__nom_nivell', 'curs__nom_curs', 'nom_grup'],
                'abstract': False,
                'verbose_name': 'Grup',
                'verbose_name_plural': 'Grups',
            },
        ),
        migrations.CreateModel(
            name='Nivell',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom_nivell', models.CharField(unique=True, max_length=45, verbose_name=b'Nom nivell')),
                ('ordre_nivell', models.IntegerField(help_text="S'utilitza per mostrar un nivell abans que un altre (Ex: ESO=0, CFSI=1000)", null=True, blank=True)),
                ('descripcio_nivell', models.CharField(max_length=240, blank=True)),
                ('anotacions_nivell', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['ordre_nivell'],
                'abstract': False,
                'verbose_name': 'Nivell',
                'verbose_name_plural': 'Nivells',
            },
        ),
        migrations.AddField(
            model_name='curs',
            name='nivell',
            field=models.ForeignKey(to='alumnes.Nivell', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='alumne',
            name='grup',
            field=models.ForeignKey(to='alumnes.Grup', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='alumne',
            name='user_associat',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='usuaris.AlumneUser'),
        ),
        migrations.CreateModel(
            name='AlumneGrup',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('alumnes.alumne',),
        ),
        migrations.CreateModel(
            name='AlumneGrupNom',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('alumnes.alumne',),
        ),
        migrations.AlterUniqueTogether(
            name='curs',
            unique_together=set([('nivell', 'nom_curs')]),
        ),
        migrations.AlterUniqueTogether(
            name='alumne',
            unique_together=set([('nom', 'cognoms', 'data_neixement')]),
        ),
    ]
