# This Python file uses the following encoding: utf-8
from django.db import models
from aula.apps.alumnes.models import Grup
from aula.apps.horaris.models import FranjaHoraria
from aula.utils.tools import unicode

class Franja2Aula(models.Model):
    franja_kronowin = models.CharField(u'Codi hora al kronowin(0,0=primera hora)', max_length=45, unique=True)
    franja_aula = models.ForeignKey(FranjaHoraria, null=True, blank=True, on_delete=models.CASCADE )
    class Meta:
        ordering = ['franja_kronowin']  #Ull es un camp numèric dins un camp de text.
        verbose_name = u'Mapeig Franja Horària'
        verbose_name_plural = u'Mapejos Franjes Horàries'
    def __str__(self):
        franja = unicode( self.franja_aula) if self.franja_aula else u'Sense assignar'
        return  unicode( self.franja_kronowin) + ' -> ' + franja

class Grup2Aula(models.Model):
    grup_kronowin =  models.CharField(max_length=45, unique=True)
    Grup2Aula = models.ForeignKey(Grup, null=True, related_name="grup2aulakonowin_set", on_delete=models.CASCADE)
    class Meta:
        ordering = ['Grup2Aula','grup_kronowin']
        verbose_name = u'Mapeig Grup Aula Kronowin'
        verbose_name_plural = u'Mapejos Grups Aula Kronowin'
    def __str__(self):
        grup = unicode( self.Grup2Aula) if self.Grup2Aula else u'Sense assignar'
        return  unicode( self.grup_kronowin) + ' -> ' + grup

class ParametreKronowin(models.Model):
    nom_parametre =  models.CharField(max_length=45, unique=True, help_text=u'Nom paràmetre (ex: passwd, assignatures amb professor, ...)')
    valor_parametre = models.CharField(max_length=240, blank=True)
    class Meta:
        ordering = ['nom_parametre']
        verbose_name = u'Paràmetre Kronowin'
        verbose_name_plural = u'Paràmetres Kronowin'
    def __str__(self):
        return  unicode( self.nom_parametre ) + ': ' + self.valor_parametre[0:10] + '...'


