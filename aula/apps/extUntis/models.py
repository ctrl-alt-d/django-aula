# This Python file uses the following encoding: utf-8
from django.db import models
from aula.apps.alumnes.models import Grup

class Agrupament(models.Model):
    grup_alumnes = models.ForeignKey(Grup, related_name="grup_alumnes", on_delete=models.CASCADE)
    grup_horari = models.ForeignKey(Grup, related_name="grup_horari", on_delete=models.CASCADE)
    class Meta:
        ordering = ['grup_alumnes','grup_horari']
        verbose_name = u'Agrupament grups alumnes i grups horari'
        verbose_name_plural = u'Agrupaments grups alumnes i grups horari'
    def __str__(self):
        return str(self.grup_alumnes) + ' -> ' + str(self.grup_horari)
