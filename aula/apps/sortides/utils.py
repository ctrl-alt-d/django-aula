# This Python file uses the following encoding: utf-8

import django.utils.timezone

from aula.apps.sortides.models import (
    QuotaPagament,
)

# helpers


def get_QuotaPagament(alumne, tipus, nany=None):
    """
    alumne del que volem la quota
    tipus de quota a escollir
    nany que correspon a la quota, si None utilitza any actual
    Retorna queryset amb la quota que correspon a l'alumne, tipus de quota i any indicats.
    """

    if not nany:
        nany = django.utils.timezone.now().year
    return QuotaPagament.objects.filter(
        alumne=alumne, quota__tipus=tipus, quota__any=nany
    )
