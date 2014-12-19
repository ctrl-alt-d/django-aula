# This Python file uses the following encoding: utf-8
from django.db import models
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.usuaris.models import Departament, Professor
from aula.apps.sortides.business_rules.sortida import clean_sortida
from aula.apps.alumnes.models import Alumne

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
                    ( 'TR', 'Tren',),
                    ( 'BU', 'Bus',),
                    ( 'AP', 'A peu',),
                    ( 'CO', 'Combinat',),                    
                               )
    
    ESTAT_CHOICES = (
                     ('E', u'Esborrany',),
                     ('P', u'Proposada',),
                     ('R', u'Revisada pel Coordinador',),
                     ('G', u"Gestionada pel Cap d'estudis",),                     
                     )
    

    estat = models.CharField(max_length=1, default = 'E', choices=ESTAT_CHOICES,help_text=u"Estat de la sortida. No es considera proposta de sortida fins que no passa a estat 'Proposada'") 
    
    tipus = models.CharField(max_length=1, default = 'E', choices=TIPUS_ACTIVITAT_CHOICES,help_text=u"Tipus d'activitat") 
    
    titol_de_la_sortida = models.CharField(max_length=40,help_text=u"Escriu un títol breu que serveixi per identificar aquesta sortida.Ex: exemples: Visita al Museu Dalí, Ruta al barri gòtic, Xerrada sobre drogues ")

    ambit = models.CharField(u"Àmbit", max_length=20,help_text=u"Quins alumnes hi van? Ex: 1r i 2n ESO. Ex: 1rESO grup A.")

    ciutat = models.CharField(u"Ciutat", max_length=30,help_text=u"Ciutat(s) destinació. Ex: Girona, Cendrassos")

    esta_aprovada_pel_consell_escolar = models.CharField( u'Aprovada_pel_consell_escolar?',max_length=1, choices=CONSELL_ESCOLAR_CHOICES, default='P', help_text=u"Marca si aquesta sortida ja ha estat aprovada pel consell escolar" )
    
    departament_que_organitza = models.ForeignKey(Departament, help_text=u"Indica quin departament organitza la sortida")
    
    data_inici = models.DateField( u"Presencia: Des de", help_text=u"Primer dia lectiu de la sortida", blank=True, null=True)
    franja_inici = models.ForeignKey(FranjaHoraria,verbose_name="Presencia: Des de", related_name='hora_inici_sortida',  help_text=u"Primera franja lectiva de la sortida", blank=True, null=True)
    data_fi = models.DateField(  u"Presencia: Fins a",help_text=u"Darrer dia  lectiu de la sortida", blank=True, null=True)
    franja_fi = models.ForeignKey(FranjaHoraria,verbose_name="Presencia: Fins a", related_name='hora_fi_sortida',  help_text=u"Darrera franja lectiva de la sortida que afecta a les classes", blank=True, null=True)
    
    calendari_desde = models.DateTimeField( u"Calendari: Des de",help_text=u"Es publicarà al calendari del Centre")
    calendari_finsa = models.DateTimeField( u"Calendari: Fins a",help_text=u"Es publicarà al calendari del Centre")
    
    calendari_public = models.BooleanField(u"Publicar activitat", default=True, help_text = u"Ha d'apareixer al calendari públic de la web")
    
    materia = models.CharField(max_length=50,help_text=u"Matèria que es treballa a la sortida. Escriu el nom complet.")
    
    preu_per_alumne = models.CharField(max_length=100,help_text=u"Preu per alumne, escriu el preu que apareixerà a l'autorització. Si és gratuita cal indicar-ho.")

    participacio = models.CharField(u"Participació", editable=False, default=u"N/A", max_length=100,help_text=u"Nombre d’alumnes participants sobre el total possible. Per exemple: 46 de 60")
    
    mitja_de_transport = models.CharField(max_length=2, choices=TIPUS_TRANSPORT_CHOICES,help_text=u"Tria el mitjà de transport")
    
    empresa_de_transport = models.CharField(max_length=250,help_text=u"Indica el nom de l'empresa de transports i número de contracte/pressupost.")
    
    pagament_a_empresa_de_transport = models.CharField(max_length=100,help_text=u"Indica la quantitat que ha de pagar l'institut pel lloguer del bus, o compra de bitllets. Si no ha de pagar res indica-ho, escriu 'res'.")
    
    pagament_a_altres_empreses = models.TextField(help_text=u"Indica la quantitat, l'empresa que ha de rebre els diners, el sistema de pagament, el número de contracte i el termini. Si no s'ha de pagar res indica-ho, escriu 'res'.")
    
    feina_per_als_alumnes_aula = models.TextField(help_text=u"Descriu o comenta on els professors trobaran la feina que han de fer els alumnes que es quedin a l'aula. Si no queden alumnes a l'aula indica-ho.")
    
    programa_de_la_sortida = models.TextField(help_text=u"Descriu per als pares el programa de la sortida: horaris, objectius, pagaments a empreses, recomanacions (crema solar, gorra, insecticida, ...), cal portar (boli, llibreta), altres informacions d'interès per a la família. Si no cal portar res cal indicar-ho.")
    
    comentaris_interns = models.TextField(blank=True, help_text=u"Espai per anotar allò que sigui rellevant de cares a la sortida. Si no hi ha comentaris rellevants indica-ho.")
    
    professor_que_proposa = models.ForeignKey(Professor, editable=False, help_text=u"Professor que proposa la sortida", related_name='professor_proposa_sortida')
    
    professor_responsable = models.ForeignKey(Professor,  help_text=u"Professor que proposa la sortida", related_name='professor_responsable_sortida')
    
    altres_professors_acompanyants = models.ManyToManyField(Professor, help_text=u"Professors acompanyants")
    
    alumnes_convocats = models.ManyToManyField(Alumne, help_text=u"Alumnes que ha confirmat assistència",related_name='sortides_confirmades')

    alumnes_que_no_vindran = models.ManyToManyField(Alumne, help_text=u"Alumnes que haurien de perquè estan convocats però no venen",related_name='sortides_on_ha_faltat')
    
    def clean(self):
        clean_sortida( self )
    

# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from django.db.models.signals import m2m_changed #post_save  #, pre_save, pre_delete

from aula.apps.sortides.business_rules.sortida import sortida_m2m_changed
m2m_changed.connect(sortida_m2m_changed, sender = Sortida.alumnes_convocats.through )    
m2m_changed.connect(sortida_m2m_changed, sender = Sortida.alumnes_que_no_vindran.through )    
    
    
    
     
