# This Python file uses the following encoding: utf-8
from aula.apps.incidencies.abstract_models import AbstractFrassesIncidenciaAula,\
    AbstractExpulsioDelCentre, AbstractExpulsio, AbstractIncidencia
from aula.apps.incidencies.business_rules.expulsiodelcentre import expulsioDelCentre_pre_delete,\
    expulsioDelCentre_post_save, expulsioDelCentre_pre_save,\
    expulsioDelCentre_clean
from aula.apps.incidencies.business_rules.incidencia import Incidencia_post_save,\
    incidencia_pre_save, Incidencia_pre_delete, incidencia_clean
from aula.apps.incidencies.business_rules.expulsio import expulsio_pre_delete,\
    expulsio_post_save, expulsio_pre_save, expulsio_clean

class FrassesIncidenciaAula(AbstractFrassesIncidenciaAula):
    pass

class ExpulsioDelCentre(AbstractExpulsioDelCentre):
    def clean(self):
        expulsioDelCentre_clean(self)

class Expulsio(AbstractExpulsio):
    def clean(self):
        expulsio_clean(self)

class Incidencia(AbstractIncidencia):
    def clean(self):
        incidencia_clean(self)
        
# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from django.db.models.signals import post_save, pre_save, pre_delete

#incidencia
pre_delete.connect(Incidencia_pre_delete, sender= Incidencia)
pre_save.connect(incidencia_pre_save, sender = Incidencia )
post_save.connect(Incidencia_post_save, sender = Incidencia )

#expulsio del centre
pre_save.connect(expulsioDelCentre_pre_save, sender = ExpulsioDelCentre )
post_save.connect(expulsioDelCentre_post_save, sender = ExpulsioDelCentre )
pre_delete.connect(expulsioDelCentre_pre_delete, sender = ExpulsioDelCentre )
       
#expulsio
pre_delete.connect(expulsio_pre_delete, sender= Expulsio)
pre_save.connect(expulsio_pre_save, sender = Expulsio )
post_save.connect(expulsio_post_save, sender = Expulsio )
pre_delete.connect(expulsio_pre_delete, sender = ExpulsioDelCentre )




