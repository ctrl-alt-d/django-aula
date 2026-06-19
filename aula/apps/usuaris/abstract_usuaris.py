# This Python file uses the following encoding: utf-8


# from django.db.models import get_model
from django.contrib.auth.models import User
from django.db import models

from aula.utils.tools import unicode

# -------------------------------------------------------------


class AbstractDepartament(models.Model):
    codi = models.CharField(max_length=4)
    nom = models.CharField(max_length=300)

    class Meta:
        abstract = True
        ordering = [
            "nom",
        ]
        verbose_name = "Departament Didàctic"
        verbose_name_plural = "Departaments Didàctics"

    def __str__(self):
        return unicode(self.nom)


# ----------------------------------------------------------------------------------------------


class AbstractAccio(models.Model):
    TIPUS_ACCIO_CHOICES = (
        ("PL", "Passar llista"),
        ("LL", "Posar o treure alumnes a la llista"),
        ("IN", "Posar o treur Incidència"),
        ("EE", "Editar Expulsió"),
        ("EC", "Expulsar del Centre"),
        ("RE", "Recullir expulsió"),
        ("AC", "Registre Actuació"),
        ("AG", "Actualitza alumnes des de Saga"),
        ("MT", "Envia missatge a tutors"),
        ("SK", "Sincronitza Kronowin"),
        ("JF", "Justificar Faltes"),
        ("NF", "Notificacio Families"),
        ("AS", "Accés a dades sensibles"),
        ("SU", "Sincronitza Untis"),
        ("DS", "Control Delivery Status Notification"),
    )
    tipus = models.CharField(max_length=2, choices=TIPUS_ACCIO_CHOICES)
    usuari = models.ForeignKey(
        User, db_index=True, related_name="usuari", on_delete=models.CASCADE
    )
    impersonated_from = models.ForeignKey(
        User,
        blank=True,
        null=True,
        related_name="impersonate_from",
        on_delete=models.CASCADE,
    )
    moment = models.DateTimeField(auto_now_add=True, db_index=True)
    l4 = models.BooleanField(default=False)
    text = models.TextField()

    class Meta:
        abstract = True
        verbose_name = "Acció d'usuari"
        verbose_name_plural = "Accions d'usuari"

    def __str__(self):
        txt_imp = (
            "({0})".format(self.impersonated_from) if self.impersonated_from else ""
        )
        return "{0} {1} {2} {3}".format(self.moment, self.tipus, self.usuari, txt_imp)


# ----------------------------------------------------------------------------------------------


class AbstractNotifUsuari(models.Model):
    usuari = models.ForeignKey(
        User, db_index=True, related_name="NotifUsuari", on_delete=models.CASCADE
    )
    alumne = models.ForeignKey(
        "alumnes.Alumne",
        db_index=True,
        related_name="NotifUsuari",
        on_delete=models.CASCADE,
    )
    moment = models.DateTimeField(auto_now_add=True, db_index=True)
    tipus = models.CharField(max_length=1, blank=True)  #  'N' Notificació o 'R' Revisió

    class Meta:
        abstract = True
        ordering = ["usuari", "-moment"]
        verbose_name = "Notificació a usuari"
        verbose_name_plural = "Notificacions als usuaris"
        indexes = [
            models.Index(fields=["usuari", "alumne", "tipus"]),
        ]


class AbstractLoginUsuari(models.Model):
    exitos = models.BooleanField()
    usuari = models.ForeignKey(
        User, db_index=True, related_name="LoginUsuari", on_delete=models.CASCADE
    )
    moment = models.DateTimeField(auto_now_add=True, db_index=True)
    ip = models.CharField(max_length=15, blank=True)

    class Meta:
        abstract = True
        ordering = ["usuari", "-moment"]
        verbose_name = "Login d'usuari"
        verbose_name_plural = "Login d'usuari"

    # cal crear index a mà: create index login_usuar_u_m_idx1 on login_usuari ( usuari_id , moment desc );


class AbstractOneTimePasswd(models.Model):
    usuari = models.ForeignKey(User, db_index=True, on_delete=models.CASCADE)
    moment_expedicio = models.DateTimeField(auto_now_add=True)
    clau = models.CharField(max_length=40)
    reintents = models.IntegerField(default=0)
    #    class Meta:                            <--- TODO: hauria de tenir abstract i no ho té.
    #        abstract = True                    <--- Caldrà arreglar-ho amb migracions.


