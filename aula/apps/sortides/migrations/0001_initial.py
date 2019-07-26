# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alumnes', '0001_initial'),
        ('horaris', '0001_initial'),
        ('usuaris', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificaSortida',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('relacio_familia_revisada', models.DateTimeField(null=True)),
                ('relacio_familia_notificada', models.DateTimeField(null=True)),
                ('alumne', models.ForeignKey(to='alumnes.Alumne', on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='Sortida',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('estat', models.CharField(default=b'E', help_text="Estat de l'activitat. No es considera proposta d'activitat fins que no passa a estat 'Proposada'", max_length=1, choices=[(b'E', 'Esborrany'), (b'P', 'Proposada'), (b'R', 'Revisada pel Coordinador'), (b'G', "Gestionada pel Cap d'estudis")])),
                ('tipus', models.CharField(default=b'E', help_text="Tipus d'activitat", max_length=1, choices=[(b'E', 'Excursi\xf3 - sortida'), (b'X', 'Xerrada'), (b'P', 'Parlament Verd'), (b'A', 'Altres (especificar-ho al t\xedtol)')])),
                ('titol_de_la_sortida', models.CharField(help_text='Escriu un t\xedtol breu que serveixi per identificar aquesta activitat.Ex: exemples: Visita al Museu Dal\xed, Ruta al barri g\xf2tic, Xerrada sobre drogues ', max_length=40)),
                ('ambit', models.CharField(help_text='Quins alumnes hi van? Ex: 1r i 2n ESO. Ex: 1r ESO A.', max_length=20, verbose_name='\xc0mbit')),
                ('ciutat', models.CharField(help_text='Ciutat(s) destinaci\xf3. Ex: Girona, Cendrassos', max_length=30, verbose_name='Ciutat')),
                ('esta_aprovada_pel_consell_escolar', models.CharField(default=b'P', help_text='Marca si aquesta activitat ja ha estat aprovada pel consell escolar', max_length=1, verbose_name='Aprovada_pel_consell_escolar?', choices=[(b'P', 'Pendent'), (b'A', 'Aprovada'), (b'R', 'Rebutjada'), (b'N', 'No necessita aprovaci\xf3')])),
                ('comentari_organitza', models.CharField(help_text="En cas de no ser organitzat per un departament cal informar qui organitza l'activitat.", max_length=50, blank=True)),
                ('data_inici', models.DateField(help_text="Primer dia lectiu de l'activitat", null=True, verbose_name='Presencia: Des de', blank=True)),
                ('data_fi', models.DateField(help_text="Darrer dia  lectiu de l'activitat", null=True, verbose_name='Presencia: Fins a', blank=True)),
                ('calendari_desde', models.DateTimeField(help_text='Es publicar\xe0 al calendari del Centre', verbose_name='Calendari: Des de')),
                ('calendari_finsa', models.DateTimeField(help_text='Es publicar\xe0 al calendari del Centre', verbose_name='Calendari: Fins a')),
                ('calendari_public', models.BooleanField(default=True, help_text="Ha d'apareixer al calendari p\xfablic de la web", verbose_name='Publicar activitat')),
                ('materia', models.CharField(help_text="Mat\xe8ria que es treballa a l'activitat. Escriu el nom complet.", max_length=50)),
                ('preu_per_alumne', models.CharField(help_text="Preu per alumne, escriu el preu que apareixer\xe0 a l'autoritzaci\xf3. Si \xe9s gratuita cal indicar-ho.", max_length=100)),
                ('participacio', models.CharField(default='N/A', help_text='Nombre d\u2019alumnes participants sobre el total possible. Per exemple: 46 de 60', max_length=100, editable=False, verbose_name='Participaci\xf3')),
                ('mitja_de_transport', models.CharField(help_text='Tria el mitj\xe0 de transport', max_length=2, choices=[(b'TR', 'Tren'), (b'BU', 'Bus'), (b'AP', 'A peu'), (b'CO', 'Combinat'), (b'ND', 'No cal despla\xe7ament')])),
                ('empresa_de_transport', models.CharField(help_text="Indica el nom de l'empresa de transports i n\xfamero de contracte/pressupost.", max_length=250)),
                ('pagament_a_empresa_de_transport', models.CharField(help_text="Indica la quantitat que ha de pagar l'institut pel lloguer del bus, o compra de bitllets. Si no ha de pagar res indica-ho, escriu 'res'.", max_length=100)),
                ('pagament_a_altres_empreses', models.TextField(help_text="Indica la quantitat, l'empresa que ha de rebre els diners, el sistema de pagament, el n\xfamero de contracte i el termini. Si no s'ha de pagar res indica-ho, escriu 'res'.")),
                ('feina_per_als_alumnes_aula', models.TextField(help_text="Descriu o comenta on els professors trobaran la feina que han de fer els alumnes que es quedin a l'aula. Si no queden alumnes a l'aula indica-ho.")),
                ('programa_de_la_sortida', models.TextField(help_text="Descriu per als pares el programa de l'activitat: horaris, objectius, pagaments a empreses, recomanacions (crema solar, gorra, insecticida, ...), cal portar (boli, llibreta), altres informacions d'inter\xe8s per a la fam\xedlia. Si no cal portar res cal indicar-ho.", verbose_name="Descripci\xf3 de l'activitat")),
                ('comentaris_interns', models.TextField(help_text="Espai per anotar all\xf2 que sigui rellevant de cares a l'activitat. Si no hi ha comentaris rellevants indica-ho.", blank=True)),
                ('altres_professors_acompanyants', models.ManyToManyField(help_text='Professors acompanyants', to='usuaris.Professor', verbose_name='Professors acompanyants', blank=True)),
                ('alumnes_convocats', models.ManyToManyField(help_text='Alumnes convocats. Per seleccionar un grup sencer, clica una sola vegada damunt el nom del grup.', related_name='sortides_confirmades', to='alumnes.Alumne', blank=True)),
                ('alumnes_justificacio', models.ManyToManyField(help_text="Alumnes que no venen i disposen de justificaci\xf3 per no assistir al Centre el dia de l'activitat.", related_name='sortides_falta_justificat', to='alumnes.Alumne', blank=True)),
                ('alumnes_que_no_vindran', models.ManyToManyField(help_text="Alumnes que haurien d'assistir-hi perqu\xe8 estan convocats per\xf2 sabem que no venen.", related_name='sortides_on_ha_faltat', to='alumnes.Alumne', blank=True)),
                ('departament_que_organitza', models.ForeignKey(blank=True, to='usuaris.Departament', help_text="Indica quin departament organitza l'activitat", null=True, on_delete=models.CASCADE)),
                ('franja_fi', models.ForeignKey(related_name='hora_fi_sortida', blank=True, to='horaris.FranjaHoraria', help_text="Darrera franja lectiva de l'activitat que afecta a les classes", null=True, verbose_name=b'Presencia: Fins a', on_delete=models.CASCADE)),
                ('franja_inici', models.ForeignKey(related_name='hora_inici_sortida', blank=True, to='horaris.FranjaHoraria', help_text="Primera franja lectiva de l'activitat", null=True, verbose_name=b'Presencia: Des de', on_delete=models.CASCADE)),
                ('professor_que_proposa', models.ForeignKey(related_name='professor_proposa_sortida', editable=False, to='usuaris.Professor', help_text="Professor que proposa l'activitat", on_delete=models.CASCADE)),
                ('professors_responsables', models.ManyToManyField(help_text="Professors responsables de l'activitat", related_name='professors_responsables_sortida', verbose_name='Professors que organitzen', to='usuaris.Professor', blank=True)),
                ('tutors_alumnes_convocats', models.ManyToManyField(related_name='tutors_sortida', editable=False, to='usuaris.Professor', blank=True, help_text='Tutors dels alumnes', verbose_name='Tutors dels alumnes')),
            ],
        ),
        migrations.AddField(
            model_name='notificasortida',
            name='sortida',
            field=models.ForeignKey(to='sortides.Sortida', on_delete=models.CASCADE),
        ),
    ]
