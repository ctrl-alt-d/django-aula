# This Python file uses the following encoding: utf-8

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ToDo(models.Model):

    ESTAT_CHOICES = (
        ('P', 'Pendent'),
        ('R', 'Realitzat' ),
                     )

    PRIORITAT_CHOICES = (
        ('V', 'Molt Important'),
        ('P', 'Poc Inportant' ),
                     )
    
    propietari = models.ForeignKey( User, db_index = True, on_delete=models.CASCADE ) 
    data = models.DateTimeField( default = timezone.now, db_index = True )   
    tasca = models.CharField(max_length=100, help_text=u"Tasca a realitzar")
    informacio_adicional = models.TextField("Informació adicional", help_text=u"Informació adicional")
    estat = models.CharField(max_length=2, choices=ESTAT_CHOICES, default = 'P')
    prioritat = models.CharField(max_length=2, choices=PRIORITAT_CHOICES,  blank=True )
    enllac = models.URLField( blank = True )

    class Meta:
        verbose_name = u'Llista de tasques'
        verbose_name_plural = u'Llista de tasques'
        ordering = ['-data']
    def __str__(self):
        return (  self.tasca )