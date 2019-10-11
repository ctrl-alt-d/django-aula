# This Python file uses the following encoding: utf-8
from django.db import models
from aula.apps.alumnes.models import Curs
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

class AbstractTipusDAssignatura(models.Model):
    AMBIT_CHOICES = (
        ('G', 'Grup'),
        ('C', 'Curs'),
        ('N', 'Nivell'),
        ('I', 'Institut'),
        ('X', 'No Admet alumnes (Ex: G)'),
        ('A', 'Agrupament'),
        ('AN', 'Agrupament amb nivells'),
     )
    tipus_assignatura = models.CharField(max_length=45, unique=True)
    ambit_on_prendre_alumnes = models.CharField(max_length=45,choices=AMBIT_CHOICES, default='G', blank=False, null=False)
    capcelera = models.CharField(max_length=45, default=u"Matèria") #per a la qualitativa
    class Meta:
        abstract = True        
        verbose_name = u"Tipus d'assignatura"
        verbose_name_plural = u"Tipus d'assignatura"

    def __str__(self):
        return self.tipus_assignatura

    def delete(self):
        if self.assignatura_set.count() > 0:
            errors = {}
            errors[NON_FIELD_ERRORS] = [u'''Aquest tipus d'assignatura es fa servir, no el pots esborrar''']
            raise ValidationError(errors)
        self.save()

class AbstractAssignatura(models.Model):
    curs = models.ForeignKey(Curs, null=True, blank=True, on_delete=models.CASCADE)
    tipus_assignatura = models.ForeignKey("assignatures.TipusDAssignatura", null=True, blank=True, on_delete=models.CASCADE)
    codi_assignatura = models.CharField(max_length=45)
    nom_assignatura = models.CharField(max_length=250, blank=True)
    class Meta:
        abstract = True        
        verbose_name = u'Assignatura'
        verbose_name_plural = u'Assignatures'
    def __str__(self):        
        curs = u'({0})'.format(self.curs.nom_curs) if self.curs else ''
        return u'{0}{1}'.format(self.codi_assignatura,curs )
    

        
    def getLongName(self):
        return self.nom_assignatura.title() if self.nom_assignatura and self.codi_assignatura != self.nom_assignatura else self.codi_assignatura

