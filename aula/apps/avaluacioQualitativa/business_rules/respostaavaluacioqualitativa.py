# This Python file uses the following encoding: utf-8
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
import datetime as dt
from aula.apps.usuaris.models import User2Professor
from django.apps import apps

def respostaAvaluacioQualitativa_clean( instance ):
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)
    
    if l4: return    
    
    isUpdate = instance.pk is not None    
    #instance.instanceDB = None if not isUpdate else instance.__class__.objects.get( pk = instance.pk )
    
    errors = {}
    
    #
    # Només es poden modificar assistències 
    #
    obertaLaQualitativa =  instance.qualitativa.data_obrir_avaluacio <=  dt.date.today() <= instance.qualitativa.data_tancar_avaluacio
    if not obertaLaQualitativa:
        errors.setdefault(NON_FIELD_ERRORS, []).append( u'''No està obert el període per entrar la Qualitativa''' )
    
    if len( errors ) > 0:
        raise ValidationError(errors)


def respostaAvaluacioQualitativa_pre_delete( sender, instance, **kwargs):
    instance.clean()
    
def respostaAvaluacioQualitativa_pre_save(sender, instance,  **kwargs):
    instance.clean()
    
