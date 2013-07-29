# This Python file uses the following encoding: utf-8

from django.db import models
from datetime import datetime

class AbstractImpartir(models.Model):
    horari = models.ForeignKey('horaris.Horari', db_index=True)
    professor_guardia = models.ForeignKey('usuaris.Professor', null=True,  blank=True, related_name='professor_guardia')
    professor_passa_llista = models.ForeignKey('usuaris.Professor', null=True,  blank=True, db_index=True, related_name='professor_passa_llista')
    dia_impartir = models.DateField(db_index=True)
    dia_passa_llista = models.DateTimeField(null=True, blank=True)
    comentariImpartir = models.TextField(null=False, blank=True, default='')
    pot_no_tenir_alumnes = models.BooleanField(default=False)
    class Meta:
        abstract = True
        verbose_name = u'Impartir classe'
        verbose_name_plural = u'Impartir classes'
        unique_together = (("dia_impartir","horari"))
    def __unicode__(self):
        return (  self.dia_impartir.strftime( "%d/%m/%Y") +
                  ': ' + unicode( self.horari) )
        
    def esFutur(self):
        data = datetime( year = self.dia_impartir.year, 
                         month = self.dia_impartir.month, 
                         day = self.dia_impartir.day,
                         hour =  self.horari.hora.hora_inici.hour, 
                         minute = self.horari.hora.hora_inici.minute,
                         second = 0 )
        return data > datetime.now()

    def esAvui(self):
        from datetime import date
        data = date( year = self.dia_impartir.year, 
                         month = self.dia_impartir.month, 
                         day = self.dia_impartir.day,
                          )
        return data == date.today()
    
    def diaHora(self):
        diaHora = None
        try:
            diaHora =  datetime(  
                            year = self.dia_impartir.year, 
                            month = self.dia_impartir.month, 
                            day = self.dia_impartir.day, 
                            hour = self.horari.hora.hora_inici.hour,  
                            minute = self.horari.hora.hora_inici.minute,  
                        )
        except:
            pass
        return diaHora
    
    def resum(self):
        nAlumnes = self.controlassistencia_set.count()
        nIncidencies = self.controlassistencia_set.filter( incidencia__isnull = False   ).count()
        nExpulsions = self.controlassistencia_set.filter( expulsio__isnull = False   ).count()
        return u'Al:{0} In:{1} Ex:{2}'.format(nAlumnes,  nIncidencies, nExpulsions )
    
    def hi_ha_nulls(self):
        return self.controlassistencia_set.filter( estat__isnull = True   ).count() >0 
    
    def color(self):
        if self.dia_passa_llista:
            if self.hi_ha_nulls():
                return u'warning'
            else:
                return u'success'
        elif self.pot_no_tenir_alumnes:
            return u'success'
        elif self.esAvui():
            return u'info' 
        elif self.esFutur():
            return u'inverse' 
        else:
            return u'important'

class AbstractEstatControlAssistencia(models.Model):
    codi_estat = models.CharField( max_length=1, unique=True)
    nom_estat = models.CharField(max_length=45, unique=True)
    pct_ausencia = models.IntegerField(  default=0, null=False, blank=False, help_text=u"100=Falta tota l'hora, 0=No és falta assistència. Aquest camp serveix per que els retrassos es puguin comptar com a falta o com un percentatge de falta." )
    
    class Meta:
        abstract = True
        verbose_name = u"Estat control d'assistencia"
        verbose_name_plural = u"Estats control d'assistencia"
        
    def __unicode__(self):
        return self.nom_estat    
    

class AbstractControlAssistencia(models.Model):
    alumne = models.ForeignKey(to = 'alumnes.Alumne',  db_index=True)
    estat = models.ForeignKey('presencia.EstatControlAssistencia',  db_index=True, null=True, blank=True)
    impartir = models.ForeignKey('presencia.Impartir', db_index=True)
    professor = models.ForeignKey('usuaris.Professor', null=True, blank=True)
    
    swaped = models.BooleanField(default=False)
    estat_backup = models.ForeignKey('presencia.EstatControlAssistencia', related_name='controlassistencia_as_bkup', db_index=True, null=True, blank=True)
    professor_backup = models.ForeignKey('usuaris.Professor', related_name='controlassistencia_as_bkup', null=True, blank=True)
    
    relacio_familia_revisada = models.DateTimeField( null=True )    
    relacio_familia_notificada = models.DateTimeField( null=True ) 
    
    class Meta:
        abstract = True
        verbose_name = u'Entrada al Control d\'Assistencia'
        verbose_name_plural = u'Entrades al Control d\'Assistencia'
        unique_together = (("alumne", "impartir"))
        
    def __unicode__(self):
        return unicode(self.alumne) + u' -> '+ unicode(self.estat)    




