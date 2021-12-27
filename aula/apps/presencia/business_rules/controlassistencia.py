# This Python file uses the following encoding: utf-8
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.template.defaultfilters import timesince_filter
import datetime as dt
from aula.apps.usuaris.models import User2Professor, User2Professional
from aula.apps.tutoria.models import CartaAbsentisme
from django.apps import apps
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
    nMaxDies = settings.CUSTOM_PERIODE_MODIFICACIO_ASSISTENCIA
    if isUpdate and instance.impartir.dia_impartir < ( dt.date.today() - dt.timedelta( days = nMaxDies) ):
        errors.setdefault(NON_FIELD_ERRORS, []).append( u'''Aquest controll d'assistència és massa antic per ser modificat (Té més de {0} dies)'''.format(nMaxDies) )
        
    #todo: altres controls:
    socTutor = hasattr(instance, 'professor') and instance.professor and instance.professor in tutors
    daqui_2_hores = dt.datetime.now() + dt.timedelta( hours = 2)
    daqui_15_dies = dt.datetime.now() + dt.timedelta( days = 15)
    if isUpdate and bool(instance.estat) and (not socTutor and instance.impartir.diaHora() > daqui_2_hores): 
        errors.setdefault(NON_FIELD_ERRORS, []).append( u'''Encara no es pot entrar aquesta assistència 
                                    (Falta {0} per poder-ho fer )'''.format(
                                      timesince_filter( dt.datetime.now(), instance.impartir.diaHora() - dt.timedelta( hours = 2) ) ) )
    if isUpdate and bool(instance.estat) and (socTutor and instance.impartir.diaHora() > daqui_15_dies): 
        errors.setdefault(NON_FIELD_ERRORS, []).append( u'''Encara no es pot entrar aquesta assistència 
                                    (Falta {0} per poder-ho fer )'''.format(
                                      timesince_filter( dt.datetime.now(), instance.impartir.diaHora() - dt.timedelta( days = 15) ) ) )



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


    #Només el tutor pot justificar
    if ( settings.CUSTOM_NOMES_TUTOR_POT_JUSTIFICAR and
         justificadaAra and
         not justificadaDB and
         not socTutor):
        errors.setdefault(NON_FIELD_ERRORS, []).append( u'''
                                  Només el tutor pot justificar faltes.  
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
    # Si es tracta d'una rectificació al Justificador, deixa el professor anterior.
    if not instance.swaped and instance.instanceDB and instance.instanceDB.swaped:
        instance.professor = instance.instanceDB.professor_backup    

def controlAssistencia_pre_delete( sender, instance, **kwargs):
    pass
    
def controlAssistencia_pre_save(sender, instance,  **kwargs):
    instance.clean()

def controlAssistencia_post_save(sender, instance, created, **kwargs):
  
    #si els retards provoquen incidència la posem:
    if settings.CUSTOM_RETARD_PROVOCA_INCIDENCIA:
         
        frase = settings.CUSTOM_RETARD_FRASE
         
        TipusIncidencia = apps.get_model('incidencies','TipusIncidencia')
        tipus, _ = TipusIncidencia.objects.get_or_create(  **settings.CUSTOM_RETARD_TIPUS_INCIDENCIA )

        Incidencia = apps.get_model('incidencies','Incidencia')

        abans_en_blanc = ( hasattr(instance, 'instanceDB') and
                           instance.instanceDB is not None and
                           instance.instanceDB.estat is None )

        abans_era_retard = ( not abans_en_blanc and
                             hasattr(instance, 'instanceDB') and
                             instance.instanceDB is not None and
                             instance.instanceDB.estat is not None and
                             instance.instanceDB.estat.codi_estat == 'R'  )
        ara_es_retard = ( instance.estat is not None and
                          instance.estat.codi_estat == 'R' )

        #posem incidència si arriba tard ( només si passem de res a retard )
        if ara_es_retard and not abans_era_retard :

            ja_hi_es = Incidencia.objects.filter(
                                                      alumne = instance.alumne,
                                                      control_assistencia = instance,
                                                      descripcio_incidencia = frase,
                                                      tipus= tipus ,
                                                ).exists()

            if not ja_hi_es:
                es_primera_hora = ( settings.CUSTOM_RETARD_PRIMERA_HORA_GESTIONAT_PEL_TUTOR  
                                    and instance.esPrimeraHora() )
                es_primera_hora_txt = ( Incidencia.GESTIONADA_PEL_TUTOR_RETARD_PRIMERA_HORA 
                                        if es_primera_hora 
                                        else '' )
                i = Incidencia.objects.create(
                                          professional = User2Professional( instance.professor ),
                                          alumne = instance.alumne,
                                          control_assistencia = instance,
                                          descripcio_incidencia = frase,
                                          tipus = tipus ,
                                          gestionada_pel_tutor=es_primera_hora,
                                          gestionada_pel_tutor_motiu=es_primera_hora_txt,
                                          )
                incidencia_despres_de_posar( i )

        #treiem incidència retard si arriba a l'hora
        if not ara_es_retard:
            try:
                Incidencia.objects.filter( 
                                                              alumne = instance.alumne,
                                                              control_assistencia = instance,
                                                              descripcio_incidencia = frase,
                                                              tipus = tipus,).delete()
            except:
                pass
             

    #
    #
    # --  casos en que no s'ha de passar llista
    #
    #

    NoHaDeSerALAula = apps.get_model('presencia','NoHaDeSerALAula')
  
    #-- si està expulsat del centre aquell dia ho anotem:
    Sancio = apps.get_model('incidencies','Sancio')
    sancio = Sancio.alumne_sancionat_en_data( instance.alumne,              #alumne
                                        instance.impartir.dia_impartir,     #dia
                                        instance.impartir.horari.hora       #franja
                                       )
      
    instance.nohadeseralaula_set.filter( motiu = NoHaDeSerALAula.EXPULSAT_DEL_CENTRE ).delete()
    for x in sancio:
        NoHaDeSerALAula.objects.create( control = instance, 
                                               motiu = NoHaDeSerALAula.EXPULSAT_DEL_CENTRE,
                                               sancio=x )
        
         
    #-- si té una sortida aquell dia ho anotem:
    Sortida = apps.get_model('sortides','Sortida')
    sortida = Sortida.alumne_te_sortida_en_data( instance.alumne,                   #alumne
                                                instance.impartir.dia_impartir,     #dia
                                                instance.impartir.horari.hora       #franja
                                               )
      
    instance.nohadeseralaula_set.filter( motiu = NoHaDeSerALAula.SORTIDA ).delete()
    for x in [ s for s in sortida if not s.alumnes_a_l_aula_amb_professor_titular ]:
        NoHaDeSerALAula.objects.create( control = instance, 
                                               motiu = NoHaDeSerALAula.SORTIDA,
                                               sortida=x )
        
            
    
    
    
