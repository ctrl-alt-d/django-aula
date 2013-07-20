# This Python file uses the following encoding: utf-8
from django.db import models
from aula.apps.alumnes.models import Grup
from aula.apps.horaris.models import FranjaHoraria

class Franja2Aula(models.Model):
    franja_kronowin = models.CharField(u'Codi hora al kronowin(0,0=primera hora)', max_length=45, unique=True)
    franja_aula = models.ForeignKey(FranjaHoraria, null=True, blank=True )
    class Meta:
        ordering = ['franja_kronowin']  #Ull es un camp numèric dins un camp de text.
        verbose_name = u'Mapeig Franja Horària DjangoAula Kronowin'
        verbose_name_plural = u'Mapejos Franjes Horàries DjangoAula Kronowin'
    def __unicode__(self):
        franja = unicode( self.franja_aula) if self.franja_aula else u'Sense assignar'
        return  unicode( self.franja_kronowin) + ' -> ' + franja

class Grup2Aula(models.Model):
    grup_kronowin =  models.CharField(max_length=45, unique=True)
    Grup2Aula = models.ForeignKey(Grup, null=True)
    class Meta:
        ordering = ['Grup2Aula','grup_kronowin']
        verbose_name = u'Mapeig Grup Aula Kronowin'
        verbose_name_plural = u'Mapejos Grups Aula Kronowin'
    def __unicode__(self):
        grup = unicode( self.Grup2Aula) if self.Grup2Aula else u'Sense assignar'
        return  unicode( self.grup_kronowin) + ' -> ' + grup

class ParametreKronowin(models.Model):
    id_parametre = models.AutoField(primary_key=True)
    nom_parametre =  models.CharField(max_length=45, unique=True, help_text=u'passwd, assignatures amb professor')
    valor_parametre = models.CharField(max_length=240, blank=True)
    class Meta:
        ordering = ['nom_parametre']
        verbose_name = u'Paràmetre Kronowin'
        verbose_name_plural = u'Paràmetres Kronowin'
    def __unicode__(self):
        return  unicode( self.nom_parametre ) + ': ' + self.valor_parametre[0:10] + '...'


