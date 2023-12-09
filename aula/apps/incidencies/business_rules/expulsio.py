# This Python file uses the following encoding: utf-8

#from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from datetime import datetime
from django.apps import apps

from aula.apps.missatgeria.missatges_a_usuaris import HAS_RECOLLIT_EXPULSIO, tipusMissatge, CAL_TRAMITAR_EXPULSIO
from aula.utils.tools import unicode


def expulsio_clean( instance ):
    
    #
    # Pre-save
    #
    
    if instance.provoca_sancio:
        instance.es_vigent = False

    #dia i franja són per incidències fora d'aula.
    if instance.es_expulsio_d_aula():
        instance.dia_expulsio = instance.control_assistencia.impartir.dia_impartir
        instance.franja_expulsio = instance.control_assistencia.impartir.horari.hora
        
    if instance.tramitacio_finalitzada:
        instance.estat = 'TR' 
        
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

    if instance.instanceDB is not None and instance.instanceDB.tramitacio_finalitzada:
        errors.setdefault('tramitacio_finalitzada',[]).append(u'Aquesta expulsió ja ha estat tramitada. No es pot modificar.')
    
    if instance.estat == 'AS' and instance.professor is None:
        errors.setdefault('professor',[]).append(u'Falten Dades: professor que expulsa.')

    #comprovar que hi ha dia i franja
    if instance.dia_expulsio is None or instance.franja_expulsio_id is None:
        errors.setdefault('dia_expulsio',[]).append(u'Falten Dades: Cal dia i franja.')
        errors.setdefault('franja_expulsio',[]).append(u'Falten Dades: Cal dia i franja.')
    
    #si tramitacio_finalitzada cal que hi hagi professor informat
    if instance.tramitacio_finalitzada and instance.professor_id is None:
        errors.setdefault('professor',[]).append(u'Falten Dades: professor que expulsa.')
    
    #si tramitacio_finalitzada cal que hi hagi tutor contactat
    if instance.tramitacio_finalitzada and not instance.tutor_contactat_per_l_expulsio:
        errors.setdefault('tutor_contactat_per_l_expulsio',[]).append( u'Falten Dades: tutor contactat.' )
    
    #si tramitacio_finalitzada cal que hi hagi moment contactat
    if instance.tramitacio_finalitzada and not instance.moment_comunicacio_a_tutors:
        errors.setdefault('moment_comunicacio_a_tutors',[]).append(u'Falten Dades: moment de contacte.')

    #si tramitacio_finalitzada la data ha de ser inferior a ara
    if instance.tramitacio_finalitzada and instance.moment_comunicacio_a_tutors \
             and instance.moment_comunicacio_a_tutors > datetime.now():
        errors.setdefault('moment_comunicacio_a_tutors',[]).append(u'Comprova la data de contacte.')

    #Comprovació que és propietari de l'expulsió: ull, en el procés d'assignació pot estar sense propietari.
    estat_superior_a_ES = instance.estat != 'ES' and  \
                            ( instance.instanceDB.estat != 'ES' if instance.instanceDB else True )
    correspon_usuari =  instance.professor.pk == user.pk if user and instance.professor else True 
    if  estat_superior_a_ES and not correspon_usuari:
        errors[NON_FIELD_ERRORS] = [u'''Aquesta expulsió està gestionada per un altre professor. Necessites accés de Nivell 4 (UAT) per modificar-la.''']
    
    if len( errors ) > 0:
        raise ValidationError( errors )

    #Anoto canvis d'estat
    if instance.instanceDB is not None:
        instance.canviEstat = (instance.instanceDB.estat,  instance.estat)
        
    

def expulsio_pre_save(sender, instance, **kwargs):

    instance.clean()

def expulsio_post_save(sender, instance, created, **kwargs):
    pass


def expulsio_pre_delete( sender, instance, **kwargs):
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)
    if l4:
        for incidencia in instance.incidencia_set.all():
            incidencia.credentials = instance.credentials if hasattr( instance, 'credentials') else (None,None,)
            incidencia.es_vigent = True
            incidencia.provoca_expulsio = None
            incidencia.save()
    else:            
        errors={}
        if  user:
            errors[NON_FIELD_ERRORS] = [u'''No es poden esborrar expulsions.''']   
        
        if len( errors ) > 0:
            raise ValidationError( errors )    
        


    
def expulsio_despres_de_posar(instance):
    professor_recull = instance.professor_recull
    professor_expulsa = instance.professor

    Missatge = apps.get_model( 'missatgeria','Missatge')
    # missatge pel professor que recull la incidència:    
    if professor_recull != professor_expulsa:
        missatge = HAS_RECOLLIT_EXPULSIO
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge( remitent = professor_recull.getUser(),
                        text_missatge = missatge.format( unicode( instance ) ), tipus_de_missatge = tipus_de_missatge )
        msg.envia_a_usuari(instance.professor_recull.getUser(), 'PI')

    # missatge pel professor que expulsa:
    missatge = CAL_TRAMITAR_EXPULSIO
    tipus_de_missatge = tipusMissatge(missatge)
    msg = Missatge( remitent = professor_recull.getUser(),
                    text_missatge =  missatge.format( unicode( instance ) ),
                    enllac = '/incidencies/editaExpulsio/{0}/'.format( instance.pk ),
                    tipus_de_missatge = tipus_de_missatge)
    msg.envia_a_usuari(instance.professor.getUser(), 'VI')

    # missatge pels professors que tenen aquest alumne a l'aula (exepte el professor que expulsa):
    msg = Missatge( remitent = professor_recull.getUser(), text_missatge = unicode( instance ),
                    tipus_de_missatge = 'INFORMATIVES_DISCIPLINA')
    Professor = apps.get_model( 'usuaris','Professor')
    professors_que_tenen_aquest_alumne_a_classe = Professor.objects.filter( horari__impartir__controlassistencia__alumne = instance.alumne ).exclude( pk = instance.professor.pk ).distinct()                    
    for professor in professors_que_tenen_aquest_alumne_a_classe:
        esTutor = True if professor in instance.alumne.tutorsDeLAlumne() else False
        importancia = 'VI' if esTutor else 'PI'
        msg.envia_a_usuari( professor.getUser(), importancia )





            
