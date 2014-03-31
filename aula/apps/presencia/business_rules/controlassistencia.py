# This Python file uses the following encoding: utf-8
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
import datetime as dt
from aula.apps.usuaris.models import User2Professor, User2Professional
from aula.apps.tutoria.models import CartaAbsentisme
from django.db.models import get_model
from aula.apps.incidencies.business_rules.incidencia import incidencia_despres_de_posar
from datetime import timedelta
from django.conf import settings

#-------------ControlAssistencia-------------------------------------------------------------      

def controlAssistencia_clean( instance ):
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)
    
    if l4: return    
    
    isUpdate = instance.pk is not None    
    instance.instanceDB = None if not isUpdate else instance.__class__.objects.get( pk = instance.pk )
    
    errors = {}
    
    tutors = [ tutor for tutor in instance.alumne.tutorsDeLAlumne() ]
    if user: instance.professor = User2Professor( user )

    #
    # Només es poden modificar assistències 
    #
    nMaxDies = 30*3
    if isUpdate and instance.impartir.dia_impartir < ( dt.date.today() - dt.timedelta( days = nMaxDies) ):
        errors.setdefault(NON_FIELD_ERRORS, []).append( u'''Aquest controll d'assistència és massa antic per ser modificat (Té més de {0} dies)'''.format(nMaxDies) )
        
    #todo: altres controls:
    daqui_2_hores = dt.datetime.now() + dt.timedelta( hours = 2)
    if isUpdate and instance.impartir.diaHora() > daqui_2_hores :
        errors.setdefault(NON_FIELD_ERRORS, []).append( u'''Encara no es pot entrar aquesta assistència 
                                    (Falta {0} per poder-ho fer )'''.format(
                                       instance.impartir.diaHora()  - daqui_2_hores ) )

    #Una falta justificada pel tutor no pot ser matxacada per un professor
    socTutor = hasattr(instance, 'professor') and instance.professor and instance.professor in tutors    
    justificadaDB = instance.instanceDB and instance.instanceDB.estat and instance.instanceDB.estat.codi_estat.upper() == 'J'
    justificadaAra = instance.estat and instance.estat.codi_estat.upper() == 'J'
    posat_pel_tutor = instance.instanceDB and instance.instanceDB.professor and instance.instanceDB.professor in tutors
    
    if not socTutor and justificadaDB and posat_pel_tutor and not justificadaAra:
        errors.setdefault(NON_FIELD_ERRORS, []).append( u'''
                                  La falta d'en {0} no es pot modificar. El tutor Sr(a) {1} ha justificat la falta.  
                                                            '''.format(
                                       instance.alumne, instance.instanceDB.professor ) )
        
    #No es poden justificar faltes si s'ha enviat una carta.
    if not justificadaDB and justificadaAra:
        data_control_mes_3 = instance.impartir.dia_impartir + timedelta( days = 3 )
        dins_ambit_carta = ( CartaAbsentisme
                             .objects
                             .exclude( carta_esborrada_moment__isnull = False )
                             .filter( alumne = instance.alumne,
                                      data_carta__gte = data_control_mes_3
                                     )
                             .exists()
                            )
        if dins_ambit_carta:
            errors.setdefault(NON_FIELD_ERRORS, []).append( u'''
                                  La falta d'en {0} no es pot modificar. El tutor ha inclòs la falta en una Carta.  
                                                            '''.format(
                                       instance.alumne ) )
                
    #Només el tutor, el professor de guardia o el professor titular pot modificar un control d'assistència:
    if user:
        professors_habilitats = tutors
        if instance.professor: professors_habilitats.append( instance.professor.pk )
        if instance.impartir.horari.professor: professors_habilitats.append( instance.impartir.horari.professor.pk )
        if instance.impartir.professor_guardia: professors_habilitats.append( instance.impartir.professor_guardia.pk )
        if user.pk not in professors_habilitats:
            errors.setdefault(NON_FIELD_ERRORS, []).append( u'''Només el professor de l'assignatura, 
                                            el professor de guardia que ha passat llista o el tutor poden variar una assistència. 
                                                            ''' )         
    
    if len( errors ) > 0:
        raise ValidationError(errors)

    #Justificada: si el tutor l'havia justificat deixo al tutor com el que ha desat la falta:
    if justificadaDB and posat_pel_tutor:
        instance.professor = instance.instanceDB.professor
    

def controlAssistencia_pre_delete( sender, instance, **kwargs):
    pass
    
def controlAssistencia_pre_save(sender, instance,  **kwargs):
    instance.clean()

def controlAssistencia_post_save(sender, instance, created, **kwargs):
    frase = settings.CUSTOM_RETART_FRASE
    
    TipusIncidencia = get_model('incidencies','TipusIncidencia')
    tipus, _ = TipusIncidencia.objects.get_or_create(  **settings.CUSTOM_RETART_TIPUS_INCIDENCIA )

    Incidencia = get_model('incidencies','Incidencia')
    if instance.estat and instance.estat.codi_estat == 'R':
        
        ja_hi_es = Incidencia.objects.filter( 
                                                          alumne = instance.alumne,
                                                          control_assistencia = instance,
                                                          descripcio_incidencia = frase,
                                                          tipus= tipus ,).exists()

        if not ja_hi_es:
            try:
                i = Incidencia.objects.create(    
                                          professional = User2Professional( instance.professor ),
                                          alumne = instance.alumne,
                                          control_assistencia = instance,
                                          descripcio_incidencia = frase,
                                          tipus = tipus ,)
                incidencia_despres_de_posar( i )                                       #TODO: Passar-ho a post-save!!!!
            except:
                pass
            
    else:
        try:
            Incidencia.objects.filter( 
                                                          alumne = instance.alumne,
                                                          control_assistencia = instance,
                                                          descripcio_incidencia = frase,
                                                          tipus = tipus,).delete()
        except:
            pass
            
 
