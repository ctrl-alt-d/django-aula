# This Python file uses the following encoding: utf-8
from django.db import models

from aula.apps.alumnes.models import Grup
from aula.utils.tools import unicode


class Grup2Aula(models.Model):
    grup_saga = models.CharField(max_length=60, unique=True, blank=True)
    Grup2Aula = models.ForeignKey(
        Grup, null=True, related_name="grup2aulasaga_set", on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["Grup2Aula", "grup_saga"]
        verbose_name = "Mapeig Grup Aula Saga"
        verbose_name_plural = "Mapejos Grups Aula Saga"

    def __str__(self):
        grup = unicode(self.Grup2Aula) if self.Grup2Aula else "Sense assignar"
        return unicode(self.grup_saga) + " -> " + grup


class ParametreSaga(models.Model):
    nom_parametre = models.CharField(
        max_length=45, unique=True, help_text="Nom Paràmetre"
    )
    valor_parametre = models.CharField(max_length=240, blank=True)

    class Meta:
        ordering = ["nom_parametre"]
        verbose_name = "Paràmetre Saga"
        verbose_name_plural = "Paràmetres Saga"

    def __str__(self):
        return unicode(self.nom_parametre) + ": " + self.valor_parametre[0:10] + "..."
