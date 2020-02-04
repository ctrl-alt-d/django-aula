# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models
from django.utils.datetime_safe import datetime
from aula.utils.tools import unicode


class Recurs(models.Model):
    nom_recurs = models.CharField(max_length=45, blank=True)
    descripcio_recurs = models.CharField(max_length=240, blank=True,
                                       help_text="Exemple: Armari amb 16 portàtils Windows 10. Exemple: Equip de so i vídeo")
    disponibilitat_horaria = models.ManyToManyField('horaris.FranjaHoraria', blank=True,
                                                    help_text="Deixar en blanc per a qualsevol hora en que hi hagi docència al centre.")
    horari_lliure = models.BooleanField(default=False, help_text='Permet reserves amb temps fraccionat')
    reservable = models.BooleanField(default=True)

    class Meta:
        ordering = ['nom_recurs']
        verbose_name = 'Recurs'
        verbose_name_plural = 'Recursos'

    def __str__(self):
        descripcio = u" - {0}".format(self.descripcio_recurs) if bool(self.descripcio_recurs) else u""
        nom_i_descripcio = u"{0}{1}".format(self.nom_recurs, descripcio)
        return nom_i_descripcio if nom_i_descripcio else "-"

    def getNom(self):
        return self.nom_recurs


class ReservaRecurs(models.Model):
    recurs = models.ForeignKey('material.Recurs',
                             on_delete=models.PROTECT)
    dia_reserva = models.DateField()
    hora_inici = models.TimeField()
    hora_fi = models.TimeField()
    hora = models.ForeignKey('horaris.FranjaHoraria',
                             null=True, blank=True,
                             verbose_name='Franja Horaria', on_delete=models.CASCADE)
    usuari = models.ForeignKey(User, on_delete=models.CASCADE)
    motiu = models.CharField(max_length=120,
                             blank=False,
                             help_text="""Explica el propòsit de la reserva.
                             (Ex: Projecció vídeo.)
                             (Ex: Treball online.)
                             Important: No entreu dades sensibles en aquest camp, no entreu noms d'alumnes ni noms de famílies,
                             la primera frase d'una reserva pot ser pública a tothom.""")
    es_reserva_manual = models.BooleanField(editable=False,
                                            default=False,
                                            help_text=u"la reserva s'ha fet manualment")

    class Meta:
        ordering = ['dia_reserva', 'hora']
        indexes = [
            models.Index(fields=['dia_reserva', 'hora']),
            models.Index(fields=['es_reserva_manual', 'usuari', 'dia_reserva', 'hora']),
        ]

    def __str__(self):
        return "{aula} {hora_inici}-{hora_fi} {usuari}".format(aula=self.aula, hora_inici=self.hora_inici,
                                                               hora_fi=self.hora_fi, usuari=self.usuari)

    @property
    def dia_hora_reserva(self):
        return datetime(self.dia_reserva.year,
                        self.dia_reserva.month,
                        self.dia_reserva.day,
                        self.hora_inici.hour,
                        self.hora_inici.minute,
                        self.hora_inici.second,
                        )

    @property
    def dia_hora_reserva_fi(self):
        return datetime(self.dia_reserva.year,
                        self.dia_reserva.month,
                        self.dia_reserva.day,
                        self.hora_fi.hour,
                        self.hora_fi.minute,
                        self.hora_fi.second,
                        )

    @property
    def es_del_passat(self):
        return (self.dia_hora_reserva < datetime.now())

    @property
    def associada_a_impartir(self):
        return (self.impartir_set.exists())

    @property
    def get_assignatures(self):
        imparticions_associades = self.impartir_set.all()
        resposta = u", ".join([unicode(r.horari.assignatura)
                               for r
                               in imparticions_associades])
        return resposta or u""

    @property
    def get_grups(self):
        imparticions_associades = self.impartir_set.all()
        resposta = u", ".join([unicode(r.horari.grup)
                               for r
                               in imparticions_associades])
        return resposta or u""
