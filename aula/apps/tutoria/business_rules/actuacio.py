# This Python file uses the following encoding: utf-8

#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

#-------------ACTUACIONS-------------------------------------------------------------      

def actuacio_clean( instance ):
    import datetime as dt

    #
    # Només es poden esborrar dels darrers 7 dies
    #
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)    
    if l4:
        return
        
    errors={}    
    
    
    if instance.pk and instance.moment_actuacio < ( dt.datetime.now() + dt.timedelta( days = -365) ):
        errors[NON_FIELD_ERRORS] = [u'''Aquesta actuació és massa antiga per ser editada (Té més d' un any)''']
        
    #PRECONDICIO: Només el professor que ha posat la falta o l'equip directiu la pot treure.    
    if user and user.pk !=  instance.professional.pk :
        errors[NON_FIELD_ERRORS] = [u'''Només el professional que posa la actuació la pot modificar''']
    
    #PRECONDICIO: Només l'equip directiu pot treure faltes de més de X dies.
    #TODO.
   
    #todo: altres controls:
    #   el professor que esborra la incidència és qui l'ha posat o bé és admin.
        
    if len( errors ) > 0:
        raise ValidationError(errors)

def actuacio_pre_save(sender, instance,  **kwargs):
    actuacio_clean(instance)

def actuacio_post_save(sender, instance, created, **kwargs):
    pass

def actuacio_pre_delete( sender, instance, **kwargs):
    import datetime as dt
    
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)    
    if l4:
        return
        
    errors={}  
    
    #
    # Només es poden esborrar dels darrers 7 dies
    #
    
    if instance.moment_actuacio < ( dt.datetime.now() + dt.timedelta( days = -7) ):
        errors[NON_FIELD_ERRORS] = [u'''Aquesta actuació és massa antiga per ser esborrada (Té més d' una setmana)''']
        
    #PRECONDICIO: Només el professor que ha posat la falta o l'equip directiu la pot treure.    
    if user and user.pk !=  instance.professional.pk :
        errors[NON_FIELD_ERRORS] = [u'''Només el professional que posa la actuació la pot esborrar''']
    
    #PRECONDICIO: No es poden esborrar si tenen contingut.    
    if user and instance.actuacio :
        errors[NON_FIELD_ERRORS] = [u'''Hi ha text al motiu de l'actuació. Edita l'actuació i esborrar el contingut. Aquest control es realitza per evitar esborrats involuntaris d'informació''']
        
    if len( errors ) > 0:
        raise ValidationError(errors)
