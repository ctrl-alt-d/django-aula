# This Python file uses the following encoding: utf-8

#from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime
from django.core.exceptions import ValidationError
from django.forms.forms import NON_FIELD_ERRORS
from django.db.models import get_model
from django.conf import settings

#-------------INCIDENCIES-------------------------------------------------------------
def incidencia_clean( instance ):
    import datetime as dt
    
        
    #
    # Pre-save
    #
         
    #incidències d'aula: dia i franja copiat de impartició
    if instance.es_incidencia_d_aula():
        instance.dia_incidencia = instance.control_assistencia.impartir.dia_impartir
        instance.franja_incidencia = instance.control_assistencia.impartir.horari.hora

    #
    # Regles:
    #

    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)
    
    if l4:
        return
    
    errors = {}

    #dia i hora sempre informats    
    if not instance.dia_incidencia:
        errors.setdefault('dia_incidencia',[]).append(u'Falten Dades: Cal dia')
        
    #dia i hora sempre informats    
    if  not instance.franja_incidencia_id:
        errors.setdefault('franja_incidencia',[]).append(u'Falten Dades: Cal franja')

    #Només es poden posar incidències més enllà dels dies indicats per CUSTOM_PERIODE_CREAR_O_MODIFICAR_INCIDENCIA    
    periode = settings.CUSTOM_PERIODE_CREAR_O_MODIFICAR_INCIDENCIA
    if instance.dia_incidencia and instance.dia_incidencia < ( dt.date.today() + dt.timedelta( days = -periode ) ):
        errors.setdefault('dia_incidencia 1',[]).append(u'''No es poden posar o modificar incidències amb més de {0} dies.'''.format(periode))

    #No incidències al futur.
    if instance.dia_incidencia and instance.franja_incidencia_id  and  instance.getDate() > datetime.now():
        errors.setdefault('dia_incidencia 2',[]).append(u'''Encara no pots posar incidències en aquesta classe. Encara no s'ha realitzat.''')
        
    #No incidencies alumne que és baixa:
    if instance.alumne.data_baixa is not None and instance.alumne.data_baixa < instance.dia_incidencia:
        errors.setdefault('dia_incidencia 3',[]).append(u'''L'alumne estava de baixa en aquesta data.''')

    if len( errors ) > 0:
        raise ValidationError(errors)

def Incidencia_pre_delete(sender, instance, **kwargs):
    import datetime as dt
    
    errors = {}

    #
    # Només es poden esborrar dels darrers 7 dies
    #
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)
    
    if l4:
        return
    
    if instance.dia_incidencia < ( dt.date.today() + dt.timedelta( days = -7) ):
        errors[NON_FIELD_ERRORS] = [u'''Aquesta incidència és massa antiga per ser esborrada (Té més d' una setmana)''']
        
    #PRECONDICIO: Només el professor que ha posat la falta o l'equip directiu la pot treure.
    if user and instance.professional.getUser().pk != user.pk:
        errors[NON_FIELD_ERRORS] = [u'''Aquesta incidència no es teva.''']
    
    if len( errors ) > 0:
        raise ValidationError(errors)
        

def incidencia_pre_save(sender, instance, **kwargs):
 
    instance.clean()

def Incidencia_post_save(sender, instance, created, **kwargs):    
    pass

def incidencia_despres_de_posar(instance):
    Missatge = get_model( 'missatgeria','Missatge')
    #Lògica de negoci: 
    if not instance.tipus.es_informativa:
        if settings.CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO:
            #Si aquest alumne ja té tres incidències cal expulsar-lo --> Envio missatge al professor.
            import datetime as t
            dia_prescriu_incidencia = instance.dia_incidencia - t.timedelta( days = settings.CUSTOM_DIES_PRESCRIU_INCIDENCIA )
            Incidencia = get_model( 'incidencies','Incidencia')
            nIncidenciesAlumneProfessor = Incidencia.objects.filter( 
                                                es_vigent = True, 
                                                tipus__es_informativa = False,
                                                professional = instance.professional, 
                                                alumne = instance.alumne,
                                                dia_incidencia__gt =  dia_prescriu_incidencia
                                            ).count()
            if nIncidenciesAlumneProfessor > 2:                
                txt = u"""A l'alumne {0} ja li has posat {1} incidències en els darrers 30 dies. 
                        Segons la normativa del Centre has de tramitar 
                        una expulsió per acumulació d'incidències.""".format( instance.alumne, nIncidenciesAlumneProfessor ) 
                
                msg = Missatge( remitent = instance.professional.getUser(), text_missatge = txt )
                msg.enllac = '/incidencies/posaExpulsioPerAcumulacio/' + str( instance.pk )
                if nIncidenciesAlumneProfessor > 5:
                    msg.importancia = 'VI'
                msg.envia_a_usuari(instance.professional)
            
        #Cal que els professors i tutors sàpiguen que aquest alumne ha tingut incidència --> Envio missatge 
        remitent = instance.professional
        text_missatge = u"""Ha posat una incidència {0}a {1} ({2}) el dia {3}. 
                            El text de la incidència és: {4}""".format(
                                    'informativa ' if instance.tipus.es_informativa else '',
                                    instance.alumne,
                                    instance.alumne.grup,
                                    instance.dia_incidencia,
                                    instance.descripcio_incidencia)
        msg1 = Missatge( remitent = remitent.getUser(), text_missatge = text_missatge )           
        #si és una unitat formativa envio a tots:
        es_unitat_formativa = False
        try:
            from aula.apps.assignatures.models import TipusDAssignatura
            uf = TipusDAssignatura.objects.get( tipus_assignatura__startswith = 'Unitat Formativa' )
            es_unitat_formativa =                                           \
                                    instance.control_assistencia and  \
                                    instance.control_assistencia.impartir.horari.assignatura.tipus_assignatura == uf
        except:
            pass
        if es_unitat_formativa: 
            Professor = get_model( 'usuaris','Professor')
            professors_que_tenen_aquest_alumne_a_classe = Professor.objects.filter( horari__impartir__controlassistencia__alumne = instance.alumne ).exclude( pk = instance.professional.pk ).distinct()
            for professor in professors_que_tenen_aquest_alumne_a_classe:
                esTutor = True if professor in instance.alumne.tutorsDeLAlumne() else False
                importancia = 'VI' if esTutor else 'PI'
                msg1.envia_a_usuari( professor.getUser(), importancia )
        else:
            professors_tutors_de_l_alumne = [ p for p in instance.alumne.tutorsDeLAlumne() ]
            for professor in professors_tutors_de_l_alumne:
                importancia = 'PI'
                msg1.envia_a_usuari( professor.getUser(), importancia )
        

