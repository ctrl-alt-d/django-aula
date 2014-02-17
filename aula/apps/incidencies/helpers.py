# This Python file uses the following encoding: utf-8

from django.db.models.loading import get_model
from datetime import date, timedelta

def preescriu( ):
    fa_30_dies = date.today() - timedelta( days = 30 )
    fa_60_dies = date.today() - timedelta( days = 60 )
    
    Incidencia = get_model( 'incidencies', 'Incidencia')
    Expulsio = get_model( 'incidencies', 'Expulsio')
    
    Incidencia.objects.filter( es_vigent = True, 
                               dia_incidencia__lt = fa_30_dies).update( es_vigent = False )
    
    Expulsio.objects.filter( es_vigent = True,
                             dia_expulsio__lt = fa_60_dies ).update( es_vigent = False )        
        