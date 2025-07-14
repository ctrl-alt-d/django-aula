# This Python file uses the following encoding: utf-8
from django.db.models.signals import post_save, pre_save

from aula.apps.assignatures.abstract_models import (
    AbstractAssignatura,
    AbstractTipusDAssignatura,
)
from aula.apps.assignatures.business_rules.assignatura import (
    assignatura_clean,
)


class TipusDAssignatura(AbstractTipusDAssignatura):
    pass


class Assignatura(AbstractAssignatura):
    def clean(self):
        assignatura_clean(self)


# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from aula.apps.assignatures.business_rules.assignatura import (  # noqa: E402
    assignatura_post_save,
    assignatura_pre_save,
)

# Assignatura
pre_save.connect(assignatura_pre_save, sender=Assignatura)
post_save.connect(assignatura_post_save, sender=Assignatura)
