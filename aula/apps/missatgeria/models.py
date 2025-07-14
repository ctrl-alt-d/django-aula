# This Python file uses the following encoding: utf-8

from django.db.models.signals import post_save, pre_delete, pre_save

from aula.apps.missatgeria.abstract_models import (
    AbstractDestinatari,
    AbstractDetallMissatge,
    AbstractMissatge,
)


class Missatge(AbstractMissatge):
    pass


class DetallMissatge(AbstractDetallMissatge):
    pass


class Destinatari(AbstractDestinatari):
    pass


# ----------------------------- B U S I N E S S       R U L E S ------------------------------------ #
from aula.apps.missatgeria.business_rules.missatge import (  # noqa: E402
    missatge_post_save,
    missatge_pre_delete,
    missatge_pre_save,
)

# incidencia
pre_delete.connect(missatge_pre_delete, sender=Missatge)
pre_save.connect(missatge_pre_save, sender=Missatge)
post_save.connect(missatge_post_save, sender=Missatge)
