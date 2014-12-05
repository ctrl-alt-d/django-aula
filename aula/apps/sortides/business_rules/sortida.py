# This Python file uses the following encoding: utf-8
from django.utils.datetime_safe import datetime
import datetime as dt
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User




def clean_sortida( instance ):
    
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)

    instance.instanceDB = None   #Estat a la base de dades
    if instance.pk:    
        instance.instanceDB = instance.__class__.objects.get( pk = instance.pk )
    
    errors = []
    
    #Per estats >= G només direcció pot tocar:
    if bool(instance.instanceDB) and instance.instanceDB.estat in [ 'G' ]:   
        if not User.objects.filter( pk=user.pk, groups__name = 'direcció').exists():
            errors.append( u"Només Direcció pot modificar una sortida que s'està gestionant." )                  

    #Per estats >= R només direcció pot tocar:
    if bool(instance.instanceDB) and instance.instanceDB.estat in [ 'R', 'G' ]:   
        if not User.objects.filter( pk=user.pk, groups__name__in = [ 'sortides', 'direcció' ] ).exists():
            errors.append( u"Només el Coordinador de Sortides i Direcció pot modificar una sortida que s'està gestionant." )                  
    
    #si passem a proposat
    if instance.estat in (  'P', 'R' ):
        if ( instance.calendari_desde < datetime.now() or
             instance.calendari_finsa < instance.calendari_desde 
             ):
            errors.append( u"Comprova les dates del calendari" )

    
    #si passem a revisada 
    if instance.estat in ( 'R', ):
        
        if not User.objects.filter( pk=user.pk, groups__name__in = [ 'sortides', 'direcció' ] ).exists():
            errors.append( u"Només el coordinador de sortides (i direcció) pot Revisar Una Sortida" )
            
        if not bool(instance.instanceDB) or instance.instanceDB.estat not in [ 'P', 'R' ]:
            errors.append( u"Només es pot Revisar una sortida ja Proposada" )

        if bool(instance.instanceDB) and instance.instanceDB.estat in [ 'G' ]:             
            errors.append( u"Aquesta sortida ja ha està sent gestionada." )
        
        if not instance.esta_aprovada_pel_consell_escolar in [ 'A', 'N' ]:
            errors.append( u"Cal que la Sortida estigui aprovada pel consell escolar per poder-la donar per revisada." )
    
    #si passem a gestionada pel cap d'estudis
    if instance.estat in ( 'G', ):

        if not User.objects.filter( pk=user.pk, groups__name = 'direcció').exists():
            errors.append( u"Només el Direcció pot Gestionar una Sortida." )
                
#         if not bool(instance.instanceDB) or instance.instanceDB.estat not in [ 'P', 'R' ]:
#             errors.append( u"Només es pot Gestionar una Sortida Revisada" )
        
    #només direcció o grup sortides pot marcar com aprovada pel CE
    if ( (not bool(instance.pk) and instance.esta_aprovada_pel_consell_escolar != 'P')
          or 
         ( bool(instance.instanceDB) and  
           instance.instanceDB.esta_aprovada_pel_consell_escolar  != instance.esta_aprovada_pel_consell_escolar)
       ):
        if not User.objects.filter( pk=user.pk, groups__name__in = [ 'sortides', 'direcció' ] ).exists():
            errors.append( u"Només Direcció o el coordinador de sortides pot marcar com aprovada pel Consell Escolar." )
    
    dades_presencia = [ bool(instance.data_inici),
                        bool(instance.franja_inici),
                        bool(instance.data_fi),
                        bool(instance.franja_fi),  ]
    if len( set( dades_presencia ) ) > 1:
        errors.append( u"Dates i franges de control de presencia cal entrar-les totes o cap" )    
    
    if l4:
        pass
    elif bool(errors):
        raise ValidationError( errors  )
    
def sortida_m2m_changed(sender, instance, action, reverse, model, pk_set, *args, **kwargs):
    if action in ( "post_remove" , "post_add" ):   
        
        alumnesQueVenen = set( [i.pk for i in instance.alumnes_convocats.all() ] )
        alumnesQueNoVenen = set( [i.pk for i in instance.alumnes_que_no_vindran.all() ] )
        
        alumnesATreure = alumnesQueNoVenen - ( alumnesQueVenen & alumnesQueNoVenen )
        
        print 'esborrar', alumnesATreure
    
        for alumne in alumnesATreure:
            instance.alumnes_que_no_vindran.remove( alumne )
        
        instance.participacio = u"{0} de {1}".format( instance.alumnes_convocats.count() - instance.alumnes_que_no_vindran.count( ) ,
                                                      instance.alumnes_convocats.count() )
        instance.__class__.objects.filter(pk=instance.pk).update( participacio = instance.participacio )
    


    