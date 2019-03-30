# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0001_initial'),
        ('horaris', '0001_initial'),
        ('presencia', '0001_initial'),
        ('usuaris', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Expulsio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('estat', models.CharField(default=b'ES', max_length=2, choices=[(b'ES', b'Esborrany'), (b'AS', b'Assignada'), (b'TR', b'Tramitada')])),
                ('dia_expulsio', models.DateField(help_text="Dia en que l'alumne ha estat expulsat", blank=True)),
                ('motiu', models.TextField(help_text="Motiu de l'expulsi\xf3. Aquesta informaci\xf3 la rebran els pares. No posar dades metges ni de salut.")),
                ('moment_comunicacio_a_tutors', models.DateTimeField(help_text='Moment en que aquesta expulsi\xf3 ha estat comunicada als tutors', null=True, blank=True)),
                ('tutor_contactat_per_l_expulsio', models.CharField(help_text='Familiars o tutors legals contactats', max_length=250, blank=True)),
                ('tramitacio_finalitzada', models.BooleanField(default=False, help_text="Marca aquesta cassella quan hagis finalitzat tota la tramitaci\xf3 de l'expulsi\xf3. Un cop tramitada no es pot esborrar ni modificar.")),
                ('comentaris_cap_d_estudis', models.TextField(help_text="Comentaris interns del cap d'estudis.", blank=True)),
                ('es_expulsio_per_acumulacio_incidencies', models.BooleanField(default=False)),
                ('es_vigent', models.BooleanField(default=True, db_index=True)),
                ('relacio_familia_revisada', models.DateTimeField(null=True)),
                ('relacio_familia_notificada', models.DateTimeField(null=True)),
                ('alumne', models.ForeignKey(help_text="Alumne al qual s'expulsa", to='alumnes.Alumne', on_delete=models.CASCADE)),
                ('control_assistencia', models.ForeignKey(blank=True, to='presencia.ControlAssistencia', null=True, on_delete=models.CASCADE)),
                ('franja_expulsio', models.ForeignKey(help_text="Franja en que l'alumne ha estat expulsat", to='horaris.FranjaHoraria', on_delete=models.CASCADE)),
                ('professor', models.ForeignKey(blank=True, to='usuaris.Professor', help_text='Professor que expulsa', null=True, on_delete=models.CASCADE)),
                ('professor_recull', models.ForeignKey(related_name='expulsions_recollides', to='usuaris.Professor', help_text="Professor que recull l'expulsi\xf3", on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Expulsi\xf3',
                'verbose_name_plural': 'Expulsions',
            },
        ),
        migrations.CreateModel(
            name='FrassesIncidenciaAula',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('frase', models.CharField(help_text="Escriu una frase que podr\xe0 ser triada a l'hora de posar una incid\xe8ncia", unique=True, max_length=240, verbose_name=b'Frase')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Frase',
                'verbose_name_plural': 'Frases',
            },
        ),
        migrations.CreateModel(
            name='Incidencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dia_incidencia', models.DateField(help_text='Data en que es va produir la incid\xe8ncia', db_index=True)),
                ('descripcio_incidencia', models.CharField(help_text='Frase curta que descriu la incid\xe8ncia. Aquesta informaci\xf3 la veuran els pares.', max_length=250)),
                ('es_vigent', models.BooleanField(default=True, db_index=True)),
                ('relacio_familia_revisada', models.DateTimeField(null=True)),
                ('relacio_familia_notificada', models.DateTimeField(null=True)),
                ('alumne', models.ForeignKey(help_text='Alumne al qual li posem la incid\xe8ncia', to='alumnes.Alumne', on_delete=models.CASCADE)),
                ('control_assistencia', models.ForeignKey(blank=True, to='presencia.ControlAssistencia', null=True, on_delete=models.CASCADE)),
                ('franja_incidencia', models.ForeignKey(help_text='Moment en que es va produir la incid\xe8ncia', to='horaris.FranjaHoraria', on_delete=models.CASCADE)),
                ('professional', models.ForeignKey(help_text='Professor que tramita la incid\xe8ncia', to='usuaris.Professional', on_delete=models.CASCADE)),
                ('provoca_expulsio', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='incidencies.Expulsio', null=True)),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Incid\xe8ncia',
                'verbose_name_plural': 'Incid\xe8ncies',
            },
        ),
        migrations.CreateModel(
            name='Sancio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data_inici', models.DateField(help_text='Primer dia de sanci\xf3')),
                ('data_fi', models.DateField(help_text="Darrer dia d'expulsi\xf3")),
                ('data_carta', models.DateField(help_text='Data en que se signa la carta de sanci\xf3')),
                ('motiu', models.TextField(help_text='Informaci\xf3 adicional a la carta de sanci\xf3 que veuran els pares', null=True, blank=True)),
                ('obra_expedient', models.BooleanField(default=False, help_text="Aquesta sanci\xf3 ha provocat que a l'alumne se li obri un expedient")),
                ('comentaris_cap_d_estudis', models.TextField(help_text="Comentaris interns del cap d'estudis", blank=True)),
                ('signat', models.CharField(max_length=250)),
                ('impres', models.BooleanField(default=False, help_text='Un cop impr\xe8s el document ja no pot modificar-se la sanci\xf3')),
                ('relacio_familia_revisada', models.DateTimeField(null=True)),
                ('relacio_familia_notificada', models.DateTimeField(null=True)),
                ('alumne', models.ForeignKey(help_text='Alumne sancionat', to='alumnes.Alumne', on_delete=models.CASCADE)),
                ('franja_fi', models.ForeignKey(related_name='hora_fi_sancio', to='horaris.FranjaHoraria', help_text='Darrera hora de sanci\xf3', on_delete=models.CASCADE)),
                ('franja_inici', models.ForeignKey(related_name='hora_inici_sancio', to='horaris.FranjaHoraria', help_text='Primera hora de sanci\xf3', on_delete=models.CASCADE)),
                ('professor', models.ForeignKey(help_text='Professor que tramita la sanci\xf3', to='usuaris.Professor', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['alumne'],
                'abstract': False,
                'verbose_name': 'Sanci\xf3',
                'verbose_name_plural': 'Sancions',
            },
        ),
        migrations.CreateModel(
            name='TipusIncidencia',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipus', models.CharField(help_text="Tipus d'incid\xe8ncia", unique=True, max_length=50, verbose_name=b'Tipus')),
                ('es_informativa', models.BooleanField(default=False, help_text='Marca aquesta casella si les incid\xe8ncies d\'aquest tipus son nom\xe9s informatives i no implicar\xe0n mesures disciplin\xe0ries. Per exemple: "Avui s\'ha esfor\xe7at molt" \xf3 "Ha faltat el dia de l\'examen".')),
                ('notificar_equip_directiu', models.BooleanField(default=False, help_text="Notifica a tots els membres de l'equip directiu quan se'n crea una")),
            ],
            options={
                'abstract': False,
                'verbose_name': "Tipus d'incid\xe8ncia",
                'verbose_name_plural': "Tipus d'incid\xe8ncies",
            },
        ),
        migrations.CreateModel(
            name='TipusSancio',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tipus', models.CharField(help_text='Tipus de sanci\xf3', unique=True, max_length=50, verbose_name=b'Tipus')),
                ('carta_slug', models.SlugField(help_text='Sufix del nom del fitxer amb la plantilla de la carta', max_length=10)),
                ('justificar', models.BooleanField(help_text='[Funcionalitat encara no implementada] Justificar assist\xe8ncia durant la sanci\xf3')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'Tipus de sancions',
                'verbose_name_plural': 'Tipus de sancions',
            },
        ),
        migrations.AddField(
            model_name='sancio',
            name='tipus',
            field=models.ForeignKey(to='incidencies.TipusSancio', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='incidencia',
            name='provoca_sancio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='incidencies.Sancio', null=True),
        ),
        migrations.AddField(
            model_name='incidencia',
            name='tipus',
            field=models.ForeignKey(to='incidencies.TipusIncidencia', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='frassesincidenciaaula',
            name='tipus',
            field=models.ForeignKey(to='incidencies.TipusIncidencia', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AddField(
            model_name='expulsio',
            name='provoca_sancio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, blank=True, to='incidencies.Sancio', null=True),
        ),
    ]
