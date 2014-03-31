# This Python file uses the following encoding: utf-8

from django.db import models
from datetime import datetime


class AbstractFrassesIncidenciaAula(models.Model):
#tipusIncidencia
    tipus = models.ForeignKey('incidencies.TipusIncidencia', on_delete = models.PROTECT )

    frase = models.CharField("Frase",max_length=240, unique=True, help_text=u"Escriu una frase que podrà ser triada a l'hora de posar una incidència")
    class Meta:
        abstract = True
        verbose_name = u'Frase'
        verbose_name_plural = u'Frases'
    def __unicode__(self):
        return self.frase

class AbstractTipusSancio(models.Model):
    tipus = models.CharField("Tipus", max_length=50, unique=True, help_text=u"Tipus de sanció")
    carta_slug = models.SlugField(max_length=10, help_text=u"Sufix del nom del fitxer amb la plantilla de la carta")
    justificar = models.BooleanField(help_text=u"[Funcionalitat encara no implementada] Justificar assistència durant la sanció")
    class Meta:
        abstract = True
        verbose_name = u'Tipus de sancions'
        verbose_name_plural = u'Tipus de sancions'
    def __unicode__(self):
        abstract = True        
        return self.tipus

class AbstractSancio(models.Model):
    professor = models.ForeignKey('usuaris.Professor', db_index=True, help_text=u"Professor que tramita la sanció")
    alumne = models.ForeignKey('alumnes.Alumne',  db_index=True, help_text=u"Alumne sancionat")
    tipus = models.ForeignKey('incidencies.TipusSancio', on_delete = models.PROTECT )
    data_inici = models.DateField( help_text=u"Primer dia de sanció")
    franja_inici = models.ForeignKey('horaris.FranjaHoraria', related_name='hora_inici_sancio', help_text=u"Primera hora de sanció")
    data_fi = models.DateField(help_text=u"Darrer dia d'expulsió")
    franja_fi = models.ForeignKey('horaris.FranjaHoraria', related_name='hora_fi_sancio', help_text=u"Darrera hora de sanció")
    data_carta =  models.DateField(help_text=u"Data en que se signa la carta de sanció")
    motiu = models.TextField(null=True, blank=True, help_text=u"Informació adicional a la carta de sanció que veuran els pares")
    obra_expedient = models.BooleanField( default = False, help_text=u"Aquesta sanció ha provocat que a l'alumne se li obri un expedient" )
    comentaris_cap_d_estudis = models.TextField(blank=True, help_text=u"Comentaris interns del cap d'estudis")
    signat = models.CharField(max_length=250)
    impres = models.BooleanField(help_text=u"Un cop imprès el document ja no pot modificar-se la sanció", default=False)
    relacio_familia_revisada = models.DateTimeField( null=True )    
    relacio_familia_notificada = models.DateTimeField( null=True ) 

    class Meta:
        abstract = True        
        verbose_name = u'Sanció'
        verbose_name_plural = u'Sancions'
        ordering = ['alumne']    

class AbstractExpulsio(models.Model):
    ESTAT_CHOICES = (
            ( 'ES','Esborrany'),
            ( 'AS', 'Assignada'),
            ( 'TR', 'Tramitada')
                    ) 
        
    estat = models.CharField(max_length=2, choices=ESTAT_CHOICES, default = 'ES')    
    professor_recull = models.ForeignKey('usuaris.Professor', 
                                         db_index=True, help_text=u"Professor que recull l'expulsió",
                                         related_name='expulsions_recollides')
    professor = models.ForeignKey('usuaris.Professor',  db_index=True, help_text=u"Professor que expulsa", blank=True, null=True)
    control_assistencia = models.ForeignKey('presencia.ControlAssistencia', null=True,  blank=True)
    alumne = models.ForeignKey('alumnes.Alumne',  db_index=True, help_text=u"Alumne al qual s'expulsa")
    
    #si no és expulsio d'aula cal dia i franja:
    dia_expulsio = models.DateField(blank=True, help_text=u"Dia en que l'alumne ha estat expulsat")
    franja_expulsio = models.ForeignKey('horaris.FranjaHoraria', help_text=u"Franja en que l'alumne ha estat expulsat" )
    
    motiu = models.TextField( help_text=u"Motiu de l'expulsió. Aquesta informació la rebran els pares. No posar dades metges ni de salut.")
    moment_comunicacio_a_tutors = models.DateTimeField(null=True, blank=True, help_text=u"Moment en que aquesta expulsió ha estat comunicada als tutors")
    tutor_contactat_per_l_expulsio = models.CharField(max_length=250, blank=True, help_text=u"Familiars o tutors legals contactats")
    tramitacio_finalitzada = models.BooleanField( help_text=u"Marca aquesta cassella quan hagis finalitzat tota la tramitació de l'expulsió. Un cop tramitada no es pot esborrar ni modificar.")
    comentaris_cap_d_estudis = models.TextField(blank=True, help_text=u"Comentaris interns del cap d'estudis.")
 
    provoca_sancio = models.ForeignKey('incidencies.Sancio', blank=True, null=True, on_delete = models.PROTECT )

    es_expulsio_per_acumulacio_incidencies = models.BooleanField( default=False )
    es_vigent = models.BooleanField( default=True , db_index=True)

    relacio_familia_revisada = models.DateTimeField( null=True )    
    relacio_familia_notificada = models.DateTimeField( null=True )    

    class Meta:
        abstract = True
        verbose_name = u'Expulsió'
        verbose_name_plural = u'Expulsions'
    
    def es_expulsio_d_aula(self):
        return self.control_assistencia != None

    def mini_motiu(self):
        return self.motiu[:100] if self.motiu else 'Motiu no informat.'
    
    def __unicode__(self):
        return u'''El professor {0} ha expulsat l'alumne {1} el dia {2}.'''.format( self.professor, 
                                                              self.alumne,
                                                              self.dia_expulsio,
                                                              self.franja_expulsio )        
    def longUnicode(self):
        return u'''El professor {0} ha expulsat l'alumne {1} 
                el dia {2} a la franja horària {3}. (expulsió
                recollida pel professor {4})'''.format( self.professor, 
                                                              self.alumne,
                                                              self.dia_expulsio,
                                                              self.franja_expulsio,
                                                              self.professor_recull )    
    def getDate(self):
        data = None
        try:
            data = datetime(
                        year = self.dia_expulsio.year,
                        month = self.dia_expulsio.month,
                        day = self.dia_expulsio.day,
                        hour = self.franja_expulsio.hora_inici.hour,
                        minute = self.franja_expulsio.hora_inici.minute,
                    )
        except:
            pass
        return data
    
    def getMotiuWithOutCR(self):
        return self.motiu.replace('\n',' ') if self.motiu else ''
    
    def totalExpulsionsVigents(self):
        return self.alumne.expulsio_set.exclude( estat = 'ES ').filter(es_vigent = True ).count()

#tipusIncidencia
class AbstractTipusIncidencia(models.Model):
    tipus = models.CharField("Tipus", max_length=50, unique=True, help_text=u"Tipus d'incidència")
    es_informativa = models.BooleanField( default = False, help_text=u'''Marca aquesta casella si les incidències d'aquest tipus son només informatives i no implicaràn mesures disciplinàries. Per exemple: "Avui s'ha esforçat molt" ó "Ha faltat el dia de l'examen".'''  )
    class Meta:
        abstract = True        
        verbose_name = u"Tipus d'incidència"
        verbose_name_plural = u"Tipus d'incidències"
    def __unicode__(self):
        return self.tipus

class AbstractIncidencia(models.Model):
    professional = models.ForeignKey('usuaris.Professional',  db_index=True, help_text=u"Professor que tramita la incidència")
    alumne = models.ForeignKey('alumnes.Alumne',  db_index=True, help_text=u"Alumne al qual li posem la incidència" )
    tipus = models.ForeignKey('incidencies.TipusIncidencia', on_delete = models.PROTECT )
    control_assistencia = models.ForeignKey('presencia.ControlAssistencia', null=True,  blank=True)
    #dia i franja són per incidències fora d'aula.
    dia_incidencia = models.DateField( db_index=True, help_text=u"Data en que es va produir la incidència")
    franja_incidencia = models.ForeignKey('horaris.FranjaHoraria',  help_text=u"Moment en que es va produir la incidència" )
    descripcio_incidencia = models.CharField(max_length=250,help_text=u"Frase curta que descriu la incidència. Aquesta informació la veuran els pares.")
    provoca_expulsio = models.ForeignKey('incidencies.Expulsio', blank=True , null=True, on_delete = models.PROTECT )

#tipusIncidencia
# Aquest camp es mou a TipusIncidencia
#    es_informativa = models.BooleanField( default = False, help_text=u'''Marca aquesta casella si aquesta incidència és només per tenir constància d'un fet. Per exemple: "Avui s'ha esforçat molt" ó "Ha faltat el dia de l'examen".'''  )

    es_vigent = models.BooleanField( default = True , db_index=True)
    provoca_sancio = models.ForeignKey('incidencies.Sancio', blank=True, null=True, on_delete = models.PROTECT  )
    relacio_familia_revisada = models.DateTimeField( null=True )    
    relacio_familia_notificada = models.DateTimeField( null=True ) 
    
    
    def es_incidencia_d_aula(self):
        return ( self.control_assistencia is not None) 
    
    class Meta:        
        abstract = True
        verbose_name = u'Incidència'
        verbose_name_plural = u'Incidències'
        
    def getDate(self):
        data = None
        try:
            data = datetime(
                        year = self.dia_incidencia.year,
                        month = self.dia_incidencia.month,
                        day = self.dia_incidencia.day,
                        hour = self.franja_incidencia.hora_inici.hour,
                        minute = self.franja_incidencia.hora_inici.minute,
                    )
        except:
            pass
        return data
    
#tipusIncidencia
    def __unicode__(self):
        informativa = u'''(informativa)''' if self.tipus.es_informativa else '' 
        return u'''{0} {1}'''.format(informativa, self.descripcio_incidencia[:50])
    
    def longUnicode(self):
        informativa = u'''(informativa)''' if self.tipus.es_informativa else '' 
        return u'''{0} {1} {2}'''.format(informativa, self.alumne, self.descripcio_incidencia)    
        
