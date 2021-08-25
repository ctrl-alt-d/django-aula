# This Python file uses the following encoding: utf-8
from django.db import models
from aula.apps.alumnes.models import Nivell

class Preinscripcio(models.Model):
    nom=models.CharField('Nom', max_length=50, null=True, blank=True)
    cognoms=models.CharField('Cognoms', max_length=100, null=True, blank=True)
    ralc=models.CharField('Identificació RALC', max_length=20, null=True, blank=True)
    codiestudis=models.CharField('Codi ensenyament', max_length=50, null=True, blank=True)
    nomestudis=models.CharField('Nom ensenyament', max_length=100, null=True, blank=True)
    codimodalitat=models.CharField('Codi modalitat', max_length=50, null=True, blank=True)
    nommodalitat=models.CharField('Modalitat', max_length=100, null=True, blank=True)
    curs=models.CharField('Curs', max_length=50, null=True, blank=True)
    regim=models.CharField('Règim', max_length=50, null=True, blank=True)
    torn=models.CharField('Torn', max_length=50, null=True, blank=True)
    identificador=models.CharField('DNI-NIE-PASS', max_length=50, null=True, blank=True)
    tis=models.CharField('TIS', max_length=50, null=True, blank=True)
    naixement=models.DateField('Data naixement', null=True, blank=True)
    sexe=models.CharField('Sexe', max_length=10, null=True, blank=True)
    nacionalitat=models.CharField('Nacionalitat', max_length=50, null=True, blank=True)
    paisnaixement=models.CharField('País naixement', max_length=100, null=True, blank=True)
    adreça=models.CharField('Adreça', max_length=300, null=True, blank=True)
    provincia=models.CharField('Província residència', max_length=50, null=True, blank=True)
    municipi=models.CharField('Municipi residència', max_length=100, null=True, blank=True)
    localitat=models.CharField('Localitat residència', max_length=100, null=True, blank=True)
    cp=models.CharField('CP', max_length=50, null=True, blank=True)
    paisresidencia=models.CharField('País residència', max_length=50, null=True, blank=True)
    telefon=models.CharField('Telèfon', max_length=50, null=True, blank=True)
    correu=models.EmailField('Correu electrònic', null=True, blank=True)
    tdoctut1=models.CharField('Tipus doc. tutor 1', max_length=50, null=True, blank=True)
    doctut1=models.CharField('Núm. doc. tutor 1', max_length=50, null=True, blank=True)
    nomtut1=models.CharField('Nom tutor 1', max_length=50, null=True, blank=True)
    cognomstut1=models.CharField('Cognoms tutor 1', max_length=1000, null=True, blank=True)
    tdoctut2=models.CharField('Tipus doc. tutor 2', max_length=50, null=True, blank=True)
    doctut2=models.CharField('Núm. doc. tutor 2', max_length=50, null=True, blank=True)
    nomtut2=models.CharField('Nom tutor 2', max_length=50, null=True, blank=True)
    cognomstut2=models.CharField('Cognoms tutor 2', max_length=100, null=True, blank=True)
    codicentreprocedencia=models.CharField('Codi centre proc.', max_length=50, null=True, blank=True)
    centreprocedencia=models.CharField('Nom centre proc.', max_length=100, null=True, blank=True)
    codiestudisprocedencia=models.CharField('Codi ensenyament proc.', max_length=50, null=True, blank=True)
    estudisprocedencia=models.CharField('Nom ensenyament proc.', max_length=100, null=True, blank=True)
    cursestudisprocedencia=models.CharField('Curs proc.', max_length=50, null=True, blank=True)
    centreassignat=models.CharField('Centre assignat', max_length=50, null=True, blank=True)
    estat=models.CharField('Estat sol·licitud', max_length=50, null=True, blank=True)
    any=models.IntegerField('Any')

    class Meta:
        ordering = ['codiestudis','cognoms','nom']
        
    def __str__(self):
        return str(self.cognoms) + ', ' + str(self.nom) + ': ' + str(self.codiestudis) + ' ' + str(self.curs)

class Nivell2Aula(models.Model):
    nivellgedac =  models.CharField(max_length=60, unique=True, blank=True)
    nivellDjau = models.ForeignKey(Nivell, null=True, related_name="nivell2djau_set", on_delete=models.CASCADE)
    class Meta:
        ordering = ['nivellDjau','nivellgedac']
        verbose_name = u'Mapeig Nivell Aula Gedac'
        verbose_name_plural = u'Mapejos Nivells Aula Gedac'
    def __str__(self):
        return  self.nivellgedac + ' -> ' + self.nivellDjau.nom_nivell if self.nivellDjau else 'Sense assignar'
