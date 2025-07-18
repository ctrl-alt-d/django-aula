# This Python file uses the following encoding: utf-8

from django.db import models
from django.db.models.signals import post_save, pre_save  # , pre_delete

from aula.apps.alumnes.abstract_models import (
    AbstractAlumne,
    AbstractCurs,
    AbstractDadesAddicionalsAlumne,
    AbstractGrup,
    AbstractNivell,
)
from aula.utils.tools import unicode


class Nivell(AbstractNivell):
    pass


class Curs(AbstractCurs):
    pass


class Grup(AbstractGrup):
    pass


class Alumne(AbstractAlumne):
    pass


class DadesAddicionalsAlumne(AbstractDadesAddicionalsAlumne):
    pass


class AlumneGrupNomManager(models.Manager):
    def get_queryset(self):
        return (
            super(AlumneGrupNomManager, self)
            .get_queryset()
            .order_by("grup", "cognoms", "nom")
        )


class AlumneGrupNom(Alumne):
    objects = AlumneGrupNomManager()

    class Meta:
        proxy = True

    def __str__(self):
        return (
            ("És baixa: " if self.esBaixa() else "")
            + unicode(self.grup)
            + " - "
            + self.cognoms
            + ", "
            + self.nom
        )


class AlumneNomSentit(Alumne):
    class Meta:
        proxy = True

    def __str__(self):
        return (
            ("És baixa: " if self.esBaixa() else "")
            + self.cognoms
            + ", "
            + (self.nom_sentit or self.nom)
        )


class AlumneGrup(Alumne):
    class Meta:
        proxy = True

    def __str__(self):
        return (
            ("És baixa: " if self.esBaixa() else "")
            + unicode(self.grup)
            + " - "
            + self.cognoms
            + ", "
            + self.nom
        )


class AlumneNomSentitGrup(Alumne):
    class Meta:
        proxy = True

    def __str__(self):
        return (
            ("És baixa: " if self.esBaixa() else "")
            + unicode(self.grup)
            + " - "
            + self.cognoms
            + ", "
            + (self.nom_sentit or self.nom)
        )


# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #

from aula.apps.alumnes.business_rules.alumne import (  # noqa: E402
    alumne_post_save,
    alumne_pre_save,
)

pre_save.connect(alumne_pre_save, sender=Alumne)
post_save.connect(alumne_post_save, sender=Alumne)
# for customising replace by:
# from customising.business_rules.alumne import alumne_post_save
# post_save.connect(alumne_post_save, sender = Alumne )
