# This Python file uses the following encoding: utf-8

from django.apps import apps
from datetime import date, timedelta
from django.conf import settings


def preescriu( ):
    dia_prescriu_incidencia = date.today() - timedelta( days = settings.CUSTOM_DIES_PRESCRIU_INCIDENCIA )
    dia_prescriu_expulsio = date.today() - timedelta( days = settings.CUSTOM_DIES_PRESCRIU_EXPULSIO )
    
    Incidencia = apps.get_model( 'incidencies', 'Incidencia')
    Expulsio = apps.get_model( 'incidencies', 'Expulsio')
    
    Incidencia.objects.filter( es_vigent = True, 
                               dia_incidencia__lt = dia_prescriu_incidencia).update( es_vigent = False )
    
    Expulsio.objects.filter( es_vigent = True,
                             dia_expulsio__lt = dia_prescriu_expulsio ).update( es_vigent = False )        
        