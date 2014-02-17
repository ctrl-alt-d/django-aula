# This Python file uses the following encoding: utf-8

from django.db import models
from datetime import datetime


class AbstractFrassesIncidenciaAula(models.Model):
    frase = models.CharField("Frase",max_length=240, unique=True, help_text=u"Escriu una frase que podrà ser triada a l'hora de posar una incidència")
    class Meta:
        abstract = True
        verbose_name = u'Frase'
        verbose_name_plural = u'Frases'
    def __unicode__(self):
        return self.frase

class AbstractExpulsioDelCentre(models.Model):
    professor = models.ForeignKey('usuaris.Professor', db_index=True, help_text=u"Professor que tramita l'expulsió del centre")
    alumne = models.ForeignKey('alumnes.Alumne',  db_index=True, help_text=u"Alumne expulsat")
    data_inici = models.DateField( help_text=u"Primer dia d'expulsió")
    franja_inici = models.ForeignKey('horaris.FranjaHoraria', related_name='hora_inici_expulsio', help_text=u"Primera hora d'expulsió")
    data_fi = models.DateField(help_text=u"Darrer dia d'expulsió")
    franja_fi = models.ForeignKey('horaris.FranjaHoraria', related_name='hora_fi_expulsio', help_text=u"Darrera hora d'expulsió")
    data_carta =  models.DateField(help_text=u"Data en que se signa la carta d'expulsió")
    motiu_expulsio = models.TextField(null=True, blank=True, help_text=u"Informació adicional a la carta d'expulsió que veuran els pares")
    obra_expedient = models.BooleanField( default = False, help_text=u"Aquesta expulsió del centre ha provocat que a l'alumne se li obri un expedient" )
    comentaris_cap_d_estudis = models.TextField(blank=True, help_text=u"Comentaris interns del cap d'estudis")
    signat = models.CharField(max_length=250)
    impres = models.BooleanField(help_text=u"Un cop imprès el document d'expulsió ja no es pot modificar l'expulsió", default=False)
    relacio_familia_revisada = models.DateTimeField( null=True )    
    relacio_familia_notificada = models.DateTimeField( null=True ) 

    class Meta:
        abstract = True        
        verbose_name = u'Expulsió del Centre'
        verbose_name_plural = u'Expulsions del Centre'
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
    
    motiu_expulsio = models.TextField( help_text=u"Motiu de l'expulsió. Aquesta informació la rebran els pares. No posar dades metges ni de salut.")
    moment_comunicacio_a_tutors = models.DateTimeField(null=True, blank=True, help_text=u"Moment en que aquesta expulsió ha estat comunicada als tutors")
    tutor_contactat_per_l_expulsio = models.CharField(max_length=250, blank=True, help_text=u"Familiars o tutors legals contactats")
    tramitacio_finalitzada = models.BooleanField( help_text=u"Marca aquesta cassella quan hagis finalitzat tota la tramitació de l'expulsió. Un cop tramitada no es pot esborrar ni modificar.")
    comentaris_cap_d_estudis = models.TextField(blank=True, help_text=u"Comentaris interns del cap d'estudis.")
    
    provoca_expulsio_centre = models.ForeignKey('incidencies.ExpulsioDelCentre', blank=True, null=True, on_delete = models.PROTECT )
    
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
        return self.motiu_expulsio[:100] if self.motiu_expulsio else 'Motiu no informat.'
    
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
        return self.motiu_expulsio.replace('\n',' ') if self.motiu_expulsio else ''
    

class AbstractIncidencia(models.Model):
    professional = models.ForeignKey('usuaris.Professional',  db_index=True, help_text=u"Professor que tramita la incidència")
    alumne = models.ForeignKey('alumnes.Alumne',  db_index=True, help_text=u"Alumne al qual li posem la incidència" )
    control_assistencia = models.ForeignKey('presencia.ControlAssistencia', null=True,  blank=True)
    #dia i franja són per incidències fora d'aula.
    dia_incidencia = models.DateField( db_index=True, help_text=u"Data en que es va produir la incidència")
    franja_incidencia = models.ForeignKey('horaris.FranjaHoraria',  help_text=u"Moment en que es va produir la incidència" )
    descripcio_incidencia = models.CharField(max_length=250,help_text=u"Frase curta que descriu la incidència. Aquesta informació la veuran els pares.")
    provoca_expulsio = models.ForeignKey('incidencies.Expulsio', blank=True , null=True, on_delete = models.PROTECT )
    es_informativa = models.BooleanField( default = False, help_text=u'''Marca aquesta casella si aquesta incidència és només per tenir constància d'un fet. Per exemple: "Avui s'ha esforçat molt" ó "Ha faltat el dia de l'examen".'''  )
    es_vigent = models.BooleanField( default = True , db_index=True)
    provoca_expulsio_centre = models.ForeignKey('incidencies.ExpulsioDelCentre', blank=True, null=True, on_delete = models.PROTECT )
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
    
    def __unicode__(self):
        informativa = u'''(informativa)''' if self.es_informativa else '' 
        return u'''{0} {1}'''.format(informativa, self.descripcio_incidencia[:50])
    
    def longUnicode(self):
        informativa = u'''(informativa)''' if self.es_informativa else '' 
        return u'''{0} {1} {2}'''.format(informativa, self.alumne, self.descripcio_incidencia)    
        
