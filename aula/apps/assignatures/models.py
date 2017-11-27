# This Python file uses the following encoding: utf-8
from aula.apps.assignatures.abstract_models import AbstractTipusDAssignatura,\
    AbstractAssignatura
from aula.apps.assignatures.business_rules.assignatura import \
    assignatura_post_save, assignatura_clean, assignatura_pre_save

class TipusDAssignatura(AbstractTipusDAssignatura):
    pass

class Assignatura(AbstractAssignatura):
    def clean(self):
        assignatura_clean(self)

# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from django.db.models.signals import post_save, pre_save, pre_delete

#Assignatura
pre_save.connect(assignatura_pre_save, sender = Assignatura )
post_save.connect(assignatura_post_save, sender = Assignatura )