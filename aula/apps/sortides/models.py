# This Python file uses the following encoding: utf-8
from django.db import models
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.usuaris.models import Departament, Professor
from aula.apps.sortides.business_rules.sortida import clean_sortida

class Sortida(models.Model):
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
    
    titol_de_la_sortida = models.CharField(max_length=250,help_text=u"Escriu un títol breu que serveixi per identificar aquesta sortida. Ex: 1rESO Sant Climent.")

    esta_aprovada_pel_consell_escolar = models.CharField( u'Aprovada_pel_consell_escolar?',max_length=1, choices=CONSELL_ESCOLAR_CHOICES, default='P', help_text=u"Marca si aquesta sortida ja ha estat aprovada pel consell escolar" )
    
    departament_que_organitza = models.ForeignKey(Departament, help_text=u"Indica quin departament organitza la sortida")
    
    data_inici = models.DateField( help_text=u"Primer dia d'expulsió")
    franja_inici = models.ForeignKey(FranjaHoraria, related_name='hora_inici_sortida',  help_text=u"Primera hora de la sortida")
    data_fi = models.DateField(help_text=u"Darrer dia de la sortida")
    franja_fi = models.ForeignKey(FranjaHoraria, related_name='hora_fi_sortida',  help_text=u"Darrera hora de la sortida")
    
    materia = models.CharField(max_length=250,help_text=u"Matèria que es treballa a la sortida. Escriu el nom complet.")
    
    preu_per_alumne = models.CharField(max_length=100,help_text=u"Preu per alumne, escriu el preu que apareixerà a l'autorització. Si és gratuita cal indicar-ho.")
    
    mitja_de_transport = models.CharField(max_length=2, choices=TIPUS_TRANSPORT_CHOICES,help_text=u"Tria el mitjà de transport")
    
    empresa_de_transport = models.CharField(max_length=250,help_text=u"Indica el nom de l'empresa de transports.")
    
    pagament_a_empresa_de_transport = models.CharField(max_length=100,help_text=u"Indica la quantitat que ha de pagar l'institut pel lloguer del bus, o compra de bitllets. Si no ha de pagar res indica-ho, escriu 'res'.")
    
    pagament_a_altres_empreses = models.TextField(help_text=u"Indica la quantitat, l'empresa que ha de rebre els diners, el sistema de pagament i el termini. Si no s'ha de pagar res indica-ho, escriu 'res'.")
    
    feina_per_als_alumnes_aula = models.TextField(help_text=u"Descriu o comenta on els professors trobaran la feina que han de fer els alumnes que es quedin a l'aula. Si no queden alumnes a l'aula indica-ho.")
    
    programa_de_la_sortida = models.TextField(help_text=u"Descriu per als pares el programa de la sortida: objectius, horaris, recomanacions (crema solar, gorra, insecticida, ...), cal portar (boli, llibreta), altres informacions d'interès per a la família. Si no cal portar res cal indicar-ho.")
    
    comentaris_interns = models.TextField(blank=True, help_text=u"Espai per anotar allò que sigui rellevant de cares a la sortida. Si no hi ha comentaris rellevants indica-ho.")
    
    professor_que_proposa = models.ForeignKey(Professor, editable=False, help_text=u"Professor que proposa la sortida")
    
    
    def clean(self):
        clean_sortida( self )
    

    
    
    
    
     
