# This Python file uses the following encoding: utf-8
from django.db import models
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.usuaris.models import Departament, Professor
from aula.apps.sortides.business_rules.sortida import clean_sortida
from aula.apps.alumnes.models import Alumne
from django.apps import apps
from django.db.models import Q
from six import python_2_unicode_compatible
from django.conf import settings

from aula.settings import CUSTOM_SORTIDES_PAGAMENT_ONLINE, CUSTOM_SORTIDES_PAGAMENT_CAIXER
from aula.utils.tools import unicode


@python_2_unicode_compatible
class Sortida(models.Model):

    TIPUS_ACTIVITAT_CHOICES = (
                    (  'E',u'Excursió - sortida'),
                    (  'X',u'Xerrada'),
                    (  'P',u'Parlament Verd'),
                    (  'A',u'Altres (especificar-ho al títol)'),
                   )

    CONSELL_ESCOLAR_CHOICES = (
                    (  'P',u'Pendent'),
                    (  'A',u'Aprovada'),
                    (  'R',u'Rebutjada' ) ,
                    (  'N',u'No necessita aprovació' ) ,
                    )

    TIPUS_TRANSPORT_CHOICES = (
                    ( 'TR', u'Tren',),
                    ( 'BU', u'Bus',),
                    ( 'AP', u'A peu',),
                    ( 'CO', u'Combinat',),
                    ( 'ND', u'No cal desplaçament',),
                               )

    ESTAT_CHOICES = (
                     ('E', u'Esborrany',),
                     ('P', u'Proposada',),
                     ('R', u'Revisada pel Coordinador',),
                     ('G', u"Gestionada pel Cap d'estudis",),
                     )

    TIPUS_PAGAMENT_CHOICES = [
        ('NO', u'No cal pagament',),
        ('EF', u'En efectiu',),
        ('ON', u'Online a través del djAu',),
        ('EB', u'''Al caixer de l'entitat bancària''',),
        ]

    NO_SINCRONITZADA = 'N'
    SINCRONITZANT_SE = 'x'
    YES_SINCRONITZADA = 'Y'
    ESTAT_SYNC_CHOICES = (
                     ( NO_SINCRONITZADA,u'No sincronitzada'),
                     ( SINCRONITZANT_SE,u''),
                     ( YES_SINCRONITZADA,u''),
                         )


    estat = models.CharField(max_length=1, default = 'E', choices=ESTAT_CHOICES,help_text=u"Estat de l'activitat. No es considera proposta d'activitat fins que no passa a estat 'Proposada'")

    estat_sincronitzacio = models.CharField(max_length=1, default = NO_SINCRONITZADA, choices=ESTAT_SYNC_CHOICES, editable = False, help_text=u"Per passar els alumnes a 'no han de ser a l'aula' ")

    tipus = models.CharField(max_length=1, default = 'E', choices=TIPUS_ACTIVITAT_CHOICES,help_text=u"Tipus d'activitat")

    titol_de_la_sortida = models.CharField(max_length=40,help_text=u"Escriu un títol breu que serveixi per identificar aquesta activitat.Ex: exemples: Visita al Museu Dalí, Ruta al barri gòtic, Xerrada sobre drogues ")

    ambit = models.CharField(u"Àmbit", max_length=20,help_text=u"Quins alumnes hi van? Ex: 1r i 2n ESO. Ex: 1r ESO A.")

    ciutat = models.CharField(u"Lloc", max_length=30,help_text=u"On es fa l'activitat. Ex. Sala polivalent, Aula 201, Teatre el Jardí, Barcelona,,...")

    esta_aprovada_pel_consell_escolar = models.CharField( u'Aprovada_pel_consell_escolar?',max_length=1, choices=CONSELL_ESCOLAR_CHOICES, default='P', help_text=u"Marca si aquesta activitat ja ha estat aprovada pel consell escolar" )

    departament_que_organitza = models.ForeignKey(Departament, help_text=u"Indica quin departament organitza l'activitat", blank=True, null=True, on_delete=models.CASCADE)
    comentari_organitza = models.CharField(max_length=50,help_text=u"En cas de no ser organitzat per un departament cal informar qui organitza l'activitat.", blank = True )

    alumnes_a_l_aula_amb_professor_titular =  models.BooleanField(u"Passar llista com normalment?", default=False, help_text = u"Els alumnes seran a l'aula i el professor de l'hora corresponent passarà llista com fa habitualment.")
    data_inici = models.DateField( u"Afecta classes: Des de", help_text=u"Primer dia lectiu afectat per l'activitat", blank=True, null=True)
    franja_inici = models.ForeignKey(FranjaHoraria,verbose_name=u"Afecta classes: Des de franja", related_name='hora_inici_sortida',  help_text=u"Primera franja lectiva afectada per l'activitat", blank=True, null=True, on_delete=models.CASCADE)
    data_fi = models.DateField(  u"Afecta classes: Fins a",help_text=u"Darrer dia  lectiu de l'activitat", blank=True, null=True)
    franja_fi = models.ForeignKey(FranjaHoraria,verbose_name=u"Afecta classes: fins a franja", related_name='hora_fi_sortida',  help_text=u"Darrera franja lectiva afectatada per l'activitat", blank=True, null=True, on_delete=models.CASCADE)

    calendari_desde = models.DateTimeField( u"Horari real, des de:",
                                            help_text=u"Horari real de l'activitat, hora de sortida, aquest horari, a més, es publicarà al calendari del Centre")
    calendari_finsa = models.DateTimeField( u"Horari real, fins a:",
                                            help_text=u"Horari real de l'activitat, hora de tornada, aquest horari, a més, es publicarà al calendari del Centre")

    calendari_public = models.BooleanField(u"Publicar activitat", default=True, help_text = u"Ha d'apareixer al calendari públic de la web")

    materia = models.CharField(max_length=50,help_text=u"Matèria que es treballa a l'activitat. Escriu el nom complet.")

    tipus_de_pagament = models.CharField(max_length=2, choices=TIPUS_PAGAMENT_CHOICES,
                                         help_text=u"Quin serà el tipus de pagament predominant", default="NO",
                                         null=False)

    preu_per_alumne = models.DecimalField(max_digits=5, blank=True, null=True, decimal_places=2, help_text=u"Preu per alumne. Indica el preu que apareixerà a l'autorització ( el posa secretaria / coordinador(a) activitats )")

    codi_de_barres = models.CharField(u"Codi de barres pagament", blank=True, default=u"", max_length=100,help_text=u"Codi de barres pagament caixer ( el posa secretaria / coordinador(a) activitats )")

    informacio_pagament = models.TextField(u"Informació pagament", blank=True,
                                           default=u"",
                                           help_text=u"Instruccions de pagament: entitat, concepte, import, ... ( el posa secretaria / coordinador(a) activitats )")

    termini_pagament = models.DateTimeField( u"Termini pagament", blank=True, null=True, help_text=u"Omplir si hi ha data límit per a realitzar el pagament.")

    programa_de_la_sortida = models.TextField(verbose_name=u"Descripció de l'activitat",
                                              help_text=u"Aquesta informació arriba a les famílies. Descriu per als pares el programa de l'activitat: horaris, objectius, pagaments a empreses, recomanacions (crema solar, gorra, insecticida, ...), cal portar (boli, llibreta), altres informacions d'interès per a la família. Si no cal portar res cal indicar-ho.")

    condicions_generals = models.TextField(blank=True, help_text=u"Aquesta informació arriba a les famílies. Condicions generals. (mètode de pagament, entrepans, entrades, comentaris...")

    participacio = models.CharField(u"Participació", editable=False, default=u"N/A", max_length=100,help_text=u"Nombre d’alumnes participants sobre el total possible. Per exemple: 46 de 60")

    mitja_de_transport = models.CharField(max_length=2, choices=TIPUS_TRANSPORT_CHOICES,help_text=u"Tria el mitjà de transport")

    empresa_de_transport = models.CharField(max_length=250,help_text=u"Indica el nom de l'empresa de transports i número de contracte/pressupost.")

    pagament_a_empresa_de_transport = models.CharField(max_length=100,help_text=u"Indica la quantitat que ha de pagar l'institut pel lloguer del bus, o compra de bitllets. Si no ha de pagar res indica-ho, escriu 'res'.")

    pagament_a_altres_empreses = models.TextField(help_text=u"Indica la quantitat, l'empresa que ha de rebre els diners, el sistema de pagament, el número de contracte i el termini. Si no s'ha de pagar res indica-ho, escriu 'res'.")

    feina_per_als_alumnes_aula = models.TextField(help_text=u"Descriu o comenta on els professors trobaran la feina que han de fer els alumnes que es quedin a l'aula. Si no queden alumnes a l'aula indica-ho.")

    comentaris_interns = models.TextField(blank=True, help_text=u"Espai per anotar allò que sigui rellevant de cares a l'activitat. Si no hi ha comentaris rellevants indica-ho.")

    professor_que_proposa = models.ForeignKey(Professor, editable=False, help_text=u"Professor que proposa l'activitat", related_name='professor_proposa_sortida', on_delete=models.CASCADE)

    professors_responsables = models.ManyToManyField(Professor, blank=True, verbose_name=u"Professors que organitzen", help_text=u"Professors responsables de l'activitat", related_name='professors_responsables_sortida')

    altres_professors_acompanyants = models.ManyToManyField(Professor, verbose_name=u"Professors acompanyants", help_text=u"Professors acompanyants", blank=True )

    tutors_alumnes_convocats = models.ManyToManyField(Professor, editable=False, verbose_name=u"Tutors dels alumnes", help_text=u"Tutors dels alumnes", blank=True, related_name='tutors_sortida' )

    alumnes_convocats = models.ManyToManyField(Alumne, blank=True, help_text=u"Alumnes convocats. Per seleccionar un grup sencer, clica una sola vegada damunt el nom del grup.",related_name='sortides_confirmades')

    alumnes_que_no_vindran = models.ManyToManyField(Alumne, blank=True, help_text=u"Alumnes que haurien d'assistir-hi perquè estan convocats però sabem que no venen.",related_name='sortides_on_ha_faltat')

    alumnes_justificacio = models.ManyToManyField(Alumne, blank=True, help_text=u"Alumnes que no venen i disposen de justificació per no assistir al Centre el dia de l'activitat.",related_name='sortides_falta_justificat')

    pagaments = models.ManyToManyField(Alumne, through='Pagament')
    @property
    def n_acompanyants(self):
        return self.altres_professors_acompanyants.count()

    @property
    def nom_acompanyants(self):
        nom_acompanyants = u", ".join( [ unicode(u) for u in self.altres_professors_acompanyants.all() ] )
        n_acompanyants = self.altres_professors_acompanyants.count()
        txt_acompanyants = u"({0}) {1}".format( n_acompanyants, nom_acompanyants) if n_acompanyants else "Sense acompanyants"
        return txt_acompanyants

    def clean(self):
        clean_sortida( self )

    def __str__(self):
        return self.titol_de_la_sortida


    @staticmethod
    def alumne_te_sortida_en_data( alumne, dia, franja ):
        Sortida = apps.get_model('sortides','Sortida')

        #auxiliar: tornen el mateix dia?
        q_mateix_dia = Q( data_inici = dia, data_fi = dia )

        #condicio 1 ( no tornen el mateix dia )
        q_entre_dates = Q( data_inici__lt = dia, data_fi__gt = dia )
        q_primer_dia = Q( data_inici = dia, franja_inici__hora_inici__lte = franja.hora_inici )
        q_darrer_dia = Q( data_fi = dia, franja_fi__hora_inici__gte = franja.hora_inici )
        q_c1 = ~q_mateix_dia & (  q_entre_dates | q_primer_dia |  q_darrer_dia )

        #condicio 2 ( tornen el mateix dia )
        q_entre_hores = Q( franja_inici__hora_inici__lte = franja.hora_inici, franja_fi__hora_inici__gte = franja.hora_inici  )
        q_c2 = q_mateix_dia & q_entre_hores

        #condicio 3 ( estat de la sortida revisada o gestionada )
        q_revisada = Q( estat = 'R' )
        q_gestionada = Q( estat = 'G' )

        sortides_de_laulumne = set( alumne.sortides_confirmades.values_list( 'id', flat=True) )
        sortides_de_laulumne_no_hi_va = set( alumne.sortides_on_ha_faltat.values_list( 'id', flat=True) )
        sortides =  sortides_de_laulumne - sortides_de_laulumne_no_hi_va

        l =  ( Sortida
                 .objects
                 .filter( id__in = sortides )
                 .filter( q_c1 | q_c2)
                 .filter( q_revisada | q_gestionada )
                 .all()
                )

        #print 'revisant {0} {1} {2} sortides: {3}'.format( alumne, dia, franja, l)

        return l

@python_2_unicode_compatible
class Pagament(models.Model):
    alumne = models.ForeignKey(Alumne, on_delete=models.PROTECT)
    sortida = models.ForeignKey(Sortida, on_delete=models.PROTECT)
    data_hora_pagament = models.CharField(max_length=50, null=True)
    pagament_realitzat = models.BooleanField(null=True, default=False )
    ordre_pagament = models.CharField(max_length=12, unique=True, null=True)

    def __str__(self):
        return u"Pagament de la sortida {}, realitzat per l'alumne {}: {}".format( self.sortida, self.alumne, self.pagament_realitzat if self.pagament_realitzat else 'No indicat' )
    
@python_2_unicode_compatible
class NotificaSortida( models.Model):
    alumne = models.ForeignKey( Alumne, on_delete=models.CASCADE )
    sortida = models.ForeignKey(Sortida, on_delete=models.CASCADE )
    relacio_familia_revisada = models.DateTimeField( null=True )    
    relacio_familia_notificada = models.DateTimeField( null=True )

    def __str__(self):
        return u"{} {}".format( self.alumne, self.sortida )

# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from django.db.models.signals import m2m_changed #post_save  #, pre_save, pre_delete

from aula.apps.sortides.business_rules.sortida import sortida_m2m_changed
m2m_changed.connect(sortida_m2m_changed, sender = Sortida.alumnes_convocats.through )    
m2m_changed.connect(sortida_m2m_changed, sender = Sortida.alumnes_que_no_vindran.through )
m2m_changed.connect(sortida_m2m_changed, sender = Sortida.alumnes_justificacio.through )      
m2m_changed.connect(sortida_m2m_changed, sender = Sortida.professors_responsables.through )    
m2m_changed.connect(sortida_m2m_changed, sender = Sortida.altres_professors_acompanyants.through )    


