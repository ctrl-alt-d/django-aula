from django.core.exceptions import ValidationError
from aula.apps.sortides.views import get_QuotaPagament

def quotapagament_pre_save(sender, instance, **kwargs):
    #Comprova si existeix el pagament per al mateix alumne, quota i any.
    p=get_QuotaPagament(instance.alumne, instance.quota.tipus, instance.quota.any)
    # Si no hi ha cap altre, el crea
    if not p: return
    # Si coincideix l'identificador, és tracta d'un canvi
    if instance.id and p.filter(id=instance.id): return
    # Si són fraccions i només hi ha una part, el crea
    if not p.filter(fracciona=False) and instance.fracciona and p.count()==1: return
    # En altre cas, error
    raise ValidationError(u"Ja existeix el pagament.")
