# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from aula.apps.aules.abstract_models import AbstractAula, AbstractReservaAula
from aula.apps.aules.business_rules.reservaaula import ( reservaaula_clean, reservaaula_post_save, 
                                                         reservaaula_pre_save, reservaaula_pre_delete,
                                                         reservaaula_post_delete ,)
from aula.apps.aules.business_rules.aula import aula_clean, aula_pre_save, aula_post_save, aula_pre_delete

class Aula(AbstractAula):
    def aula(self):
        aula_clean(self)

class ReservaAula(AbstractReservaAula):
    def clean(self):
        reservaaula_clean(self)
        
        
# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from django.db.models.signals import post_save, pre_save, pre_delete, post_delete

#Aula
pre_delete.connect(aula_pre_delete, sender= Aula)
pre_save.connect(aula_pre_save, sender = Aula )
post_save.connect(aula_post_save, sender = Aula )

#ReservaAula
pre_delete.connect(reservaaula_pre_delete, sender= ReservaAula)
pre_save.connect(reservaaula_pre_save, sender = ReservaAula )
post_save.connect(reservaaula_post_save, sender = ReservaAula )
post_delete.connect(reservaaula_post_delete, sender = ReservaAula )
