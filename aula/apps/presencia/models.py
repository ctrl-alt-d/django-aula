# This Python file uses the following encoding: utf-8

from django.db.models.signals import post_delete, post_save, pre_delete, pre_save

from aula.apps.presencia.abstract_models import (
    AbstractControlAssistencia,
    AbstractEstatControlAssistencia,
    AbstractImpartir,
    AbstractNoHaDeSerALAula,
)
from aula.apps.presencia.business_rules.controlassistencia import (
    controlAssistencia_clean,
)
from aula.apps.presencia.business_rules.estatcontrolassistencia import (
    estatControlAssistencia_clean,
)
from aula.apps.presencia.business_rules.impartir import (
    impartir_clean,
)


class Impartir(AbstractImpartir):
    def clean(self):
        impartir_clean(self)


class EstatControlAssistencia(AbstractEstatControlAssistencia):
    def clean(self):
        estatControlAssistencia_clean(self)


class ControlAssistencia(AbstractControlAssistencia):
    def clean(self):
        controlAssistencia_clean(self)


class NoHaDeSerALAula(AbstractNoHaDeSerALAula):
    pass


# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from aula.apps.presencia.business_rules.controlassistencia import (  # noqa: E402
    controlAssistencia_post_save,
    controlAssistencia_pre_delete,
    controlAssistencia_pre_save,
)
from aula.apps.presencia.business_rules.estatcontrolassistencia import (  # noqa: E402
    estatControlAssistencia_post_save,
    estatControlAssistencia_pre_delete,
    estatControlAssistencia_pre_save,
)
from aula.apps.presencia.business_rules.impartir import (  # noqa: E402
    impartir_post_delete,
    impartir_post_save,
    impartir_pre_delete,
    impartir_pre_save,
)

# Impartir
pre_delete.connect(impartir_pre_delete, sender=Impartir)
pre_save.connect(impartir_pre_save, sender=Impartir)
post_save.connect(impartir_post_save, sender=Impartir)
post_delete.connect(impartir_post_delete, sender=Impartir)

# ControlAssistencia
pre_delete.connect(controlAssistencia_pre_delete, sender=ControlAssistencia)
pre_save.connect(controlAssistencia_pre_save, sender=ControlAssistencia)
post_save.connect(controlAssistencia_post_save, sender=ControlAssistencia)

# expulsio del centre
pre_delete.connect(estatControlAssistencia_pre_delete, sender=EstatControlAssistencia)
pre_save.connect(estatControlAssistencia_pre_save, sender=EstatControlAssistencia)
post_save.connect(estatControlAssistencia_post_save, sender=EstatControlAssistencia)
