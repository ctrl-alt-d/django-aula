# This Python file uses the following encoding: utf-8

from aula.apps.missatgeria.abstract_models import AbstractMissatge,\
    AbstractDetallMissatge, AbstractDestinatari
from aula.apps.missatgeria.business_rules.missatge import missatge_pre_delete,\
    missatge_pre_save, missatge_post_save

class Missatge(AbstractMissatge):
    pass

class DetallMissatge(AbstractDetallMissatge):
    pass

class Destinatari(AbstractDestinatari):
    pass
    

# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from django.db.models.signals import post_save, pre_save, pre_delete

#incidencia
pre_delete.connect(missatge_pre_delete, sender= Missatge)
pre_save.connect(missatge_pre_save, sender = Missatge )
post_save.connect(missatge_post_save, sender = Missatge )
