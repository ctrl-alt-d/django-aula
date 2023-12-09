# This Python file uses the following encoding: utf-8

#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.apps import apps
from datetime import timedelta, tzinfo

from aula.apps.missatgeria.missatges_a_usuaris import ALUME_HA_ESTAT_SANCIONAT, tipusMissatge


def sancio_pre_delete(sender, instance, **kwargs):
    #
    # Regles:
    #
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)

        
    errors={}

    instance.instanceDB = None   #Estat a la base de dades
    if instance.pk:    
        instance.instanceDB = instance.__class__.objects.get( pk = instance.pk )

    if instance.instanceDB is not None and instance.instanceDB.impres:
        errors.setdefault('impres',[]).append(u'Aquesta sanció ja ha estat impresa. No es pot esborrar.')

    if not l4 and len( errors ) > 0:
        raise ValidationError(errors)
    
    apps.get_model(  'presencia.NoHaDeSerALAula' ).objects.filter( sancio__id = instance.pk )
        

def sancio_clean(instance):
    #
    # Regles:
    #
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)
    
    if l4:
        return
        
    errors={}

    instance.instanceDB = None   #Estat a la base de dades
    if instance.pk:    
        instance.instanceDB = instance.__class__.objects.get( pk = instance.pk )

    if instance.instanceDB is not None and instance.instanceDB.impres:
        errors.setdefault('impres',[]).append(u'Aquesta sanció ja ha estat impresa. No es pot modificar.')

    if len( errors ) > 0:
        raise ValidationError(errors)

def sancio_pre_save(sender, instance, **kwargs):
    instance.tmp__calNotificar = False
    if  instance.pk is not None:
        db_instance = instance.__class__.objects.get( pk = instance.pk )
        instance.tmp__calNotificar =  not db_instance.impres and instance.impres
        apps.get_model(  'presencia.NoHaDeSerALAula' ).objects.filter( sancio__id = instance.pk )

def sancio_post_save(sender, instance, created, **kwargs):
    # missatge pels professors que tenen aquest alumne a l'aula (exepte el professor que sanciona):
    if instance.tmp__calNotificar:
        missatge = ALUME_HA_ESTAT_SANCIONAT
        txt_msg = missatge.format( instance.alumne, instance.data_inici.strftime( '%d/%m/%Y' ), instance.data_fi.strftime( '%d/%m/%Y' ) )
        Missatge = apps.get_model( 'missatgeria','Missatge')
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge( remitent = instance.professor.getUser(), text_missatge =txt_msg, tipus_de_missatge = tipus_de_missatge)
        Professor = apps.get_model( 'usuaris','Professor' )
        professors_que_tenen_aquest_alumne_a_classe = Professor.objects.filter( horari__impartir__controlassistencia__alumne = instance.alumne ).distinct()                    
        for professor in professors_que_tenen_aquest_alumne_a_classe:
            esTutor = True if professor in instance.alumne.tutorsDeLAlumne() else False
            importancia = 'VI' if esTutor else 'PI'
            msg.envia_a_usuari( professor.getUser(), importancia )
            
    #es fa save controlAssistència per marcar com a no ha de ser present
    ControlAssistencia = apps.get_model(  'presencia.ControlAssistencia' )
    NoHaDeSerALAula = apps.get_model('presencia','NoHaDeSerALAula')
    NoHaDeSerALAula.objects.filter( sancio = instance  ).delete()
    
    dia_iterador = instance.data_inici
    totes_les_franges = list( apps.get_model(  'horaris.FranjaHoraria' ).objects.all() )
    un_dia = timedelta(days=1)
    while dia_iterador <= instance.data_fi:
        for franja in totes_les_franges:
            for control in ControlAssistencia.objects.filter( alumne = instance.alumne,
                                       impartir__dia_impartir = dia_iterador,
                                       impartir__horari__hora = franja ):
                control.save()
    
        dia_iterador += un_dia
    
    


