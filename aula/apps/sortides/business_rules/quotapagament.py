from django.core.exceptions import ValidationError
from aula.apps.sortides.views import get_QuotaPagament

def quotapagament_pre_save(sender, instance, **kwargs):
    #Comprova si existeix la mateixa quota per al mateix alumne i any.
    p=get_QuotaPagament(instance.alumne, instance.quota.tipus, instance.quota.any)
    if p:
        raise ValidationError(u"Ja existeix la quota.")
