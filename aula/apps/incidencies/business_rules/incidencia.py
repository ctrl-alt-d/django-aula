# This Python file uses the following encoding: utf-8

#from django.contrib.auth.models import User
from datetime import datetime
from django.core.exceptions import ValidationError
from django.forms.forms import NON_FIELD_ERRORS
from django.apps import apps
from django.conf import settings

#-------------INCIDENCIES-------------------------------------------------------------
from aula.apps.alumnes.named_instances import Cursa_nivell
from aula.apps.missatgeria.missatges_a_usuaris import EXPULSIO_PER_ACUMULACIO_INCIDENCIES, tipusMissatge, \
    EXPULSIO_PER_ACUMULACIO_INCIDENCIES_FORA_AULA, INCIDENCIA_INFORMATIVA, HE_POSAT_INCIDENCIA_EN_NOM_TEU, \
    HE_POSAT_INCIDENCIA_EN_NOM_DALGU
from aula.apps.usuaris.models import User2Professor


def incidencia_clean( instance ):
    import datetime as dt
    Incidencia = instance.__class__

    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,None,)

    #
    # Pre-save
    #

    # incidències d'aula: dia i franja copiat de impartició
    if instance.es_incidencia_d_aula():
        instance.dia_incidencia = instance.control_assistencia.impartir.dia_impartir
        instance.franja_incidencia = instance.control_assistencia.impartir.horari.hora

    # si la posa el profe de guàrdia -> la gestiona el tutor
    if instance.es_incidencia_d_aula() and not instance.gestionada_pel_tutor:
        professor = instance.control_assistencia.professor
        if user is not None and User2Professor(user) is not None:
            professor = User2Professor(user)
        la_posa_el_professor_de_guardia = ( (professor is not None)
                                            and
                                           ( professor != instance.control_assistencia.impartir.horari.professor )
                                          )
        if la_posa_el_professor_de_guardia:
            instance.gestionada_pel_tutor = True
            instance.gestionada_pel_tutor_motiu = Incidencia.GESTIONADA_PEL_TUTOR_GUARDIA

    # si no és d'aula -> la gestiona el tutor
    if not instance.es_incidencia_d_aula() and not instance.gestionada_pel_tutor:
        instance.gestionada_pel_tutor = True
        instance.gestionada_pel_tutor_motiu = Incidencia.GESTIONADA_PEL_TUTOR_FORA_AULA

    if instance.gestionada_pel_tutor and  instance.tipus != None and instance.tipus.es_informativa:
        instance.gestionada_pel_tutor = False
        instance.gestionada_pel_tutor_motiu = ""


    #
    # Regles:
    #


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
        errors.setdefault('dia_incidencia',[]).append(u'''No es poden posar o modificar incidències amb més de {0} dies.'''.format(periode))

    #No incidències al futur.
    if instance.dia_incidencia and instance.franja_incidencia_id  and  instance.getDate() > datetime.now():
        errors.setdefault('dia_incidencia',[]).append(u'''Encara no pots posar incidències en aquesta classe. Encara no s'ha realitzat.''')
        
    #No incidencies alumne que és baixa:
    if instance.alumne.data_baixa is not None and instance.alumne.data_baixa < instance.dia_incidencia:
        errors.setdefault('dia_incidencia',[]).append(u'''L'alumne estava de baixa en aquesta data.''')

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
    
    if instance.dia_incidencia < ( dt.date.today() + dt.timedelta( days = -30) ):
        errors[NON_FIELD_ERRORS] = [u'''Aquesta incidència és massa antiga per ser esborrada (Té més d' una setmana)''']
        
    #PRECONDICIO: Només el professor que ha posat la falta o l'equip directiu la pot treure.
    es_meva = user and instance.professional.getUser().pk == user.pk
    es_meva = es_meva or ( user
                           and instance.gestionada_pel_tutor 
                           and  instance.professional.getUser().pk in instance.alumne.tutorsDeLAlumne() )
    if user and not es_meva:
        errors[NON_FIELD_ERRORS] = [u'''No tens permisos per esborrar aquesta incidència.''']
    
    if len( errors ) > 0:
        raise ValidationError(errors)
        

def incidencia_pre_save(sender, instance, **kwargs):
 
    instance.clean()

def Incidencia_post_save(sender, instance, created, **kwargs):    
    pass

def incidencia_despres_de_posar(instance):
    Missatge = apps.get_model( 'missatgeria','Missatge')
    #Lògica de negoci: 
    if not instance.tipus.es_informativa:
        if settings.CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO:
            # Si aquest alumne ja té tres incidències cal expulsar-lo --> Envio missatge al professor.
            Incidencia = apps.get_model('incidencies', 'Incidencia')
            nIncidenciesAlumneProfessor = Incidencia.objects.filter(
                es_vigent=True,
                tipus__es_informativa=False,
                professional=instance.professional,
                alumne=instance.alumne,
                gestionada_pel_tutor=False,
            ).count()
            if nIncidenciesAlumneProfessor > 2:
                missatge = EXPULSIO_PER_ACUMULACIO_INCIDENCIES
                txt = missatge.format(instance.alumne,
                                        nIncidenciesAlumneProfessor,
                                        settings.CUSTOM_DIES_PRESCRIU_INCIDENCIA)

                tipus_de_missatge = tipusMissatge(missatge)
                msg = Missatge(remitent=instance.professional.getUser(), text_missatge=txt, tipus_de_missatge = tipus_de_missatge)
                msg.enllac = '/incidencies/posaExpulsioPerAcumulacio/' + str(instance.pk)
                if nIncidenciesAlumneProfessor > 5:
                    msg.importancia = 'VI'
                msg.envia_a_usuari(instance.professional)

        if instance.gestionada_pel_tutor and settings.CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO:
            # Si aquest alumne ja té tres incidències cal expulsar-lo --> Envio missatge al tutor.
            Incidencia = apps.get_model('incidencies', 'Incidencia')
            nIncidenciesAlumneProfessor = Incidencia.objects.filter(
                es_vigent=True,
                tipus__es_informativa=False,
                alumne=instance.alumne,
                gestionada_pel_tutor=True,
            ).count()
            if nIncidenciesAlumneProfessor > 2:
                missatge = EXPULSIO_PER_ACUMULACIO_INCIDENCIES_FORA_AULA
                txt = missatge.format(instance.alumne,
                                        nIncidenciesAlumneProfessor,
                                        settings.CUSTOM_DIES_PRESCRIU_INCIDENCIA)

                tipus_de_missatge = tipusMissatge(missatge)
                msg = Missatge(remitent=instance.professional.getUser(), text_missatge=txt, tipus_de_missatge = tipus_de_missatge)
                msg.enllac = '/incidencies/posaExpulsioPerAcumulacio/' + str(instance.pk)
                if nIncidenciesAlumneProfessor > 5:
                    msg.importancia = 'VI'
                for professional in instance.alumne.tutorsDeLAlumne():
                    msg.envia_a_usuari(professional)
        
        if bool(instance.professional_inicia):
            #
            remitent = instance.professional_inicia
            missatge = HE_POSAT_INCIDENCIA_EN_NOM_TEU
            text_missatge = missatge.format(
                                        u"Incidència de Retard d'entrada al centre",
                                        instance.alumne,
                                        instance.alumne.grup,
                                        instance.dia_incidencia,
                                        instance.descripcio_incidencia)
            tipus_de_missatge = tipusMissatge(missatge)
            msg1 = Missatge( remitent = remitent.getUser(), 
                             text_missatge = text_missatge,
                             tipus_de_missatge = tipus_de_missatge)
            importancia = 'VI'
            msg1.envia_a_usuari( instance.professional.getUser(), importancia )           
            
            #
            remitent = instance.professional_inicia
            missatge = HE_POSAT_INCIDENCIA_EN_NOM_DALGU
            text_missatge = missatge.format(
                                        u"Incidència de Retard d'entrada al centre",
                                        instance.alumne,
                                        instance.alumne.grup,
                                        instance.dia_incidencia,
                                        instance.descripcio_incidencia,
                                        instance.professional,)
            tipus_de_missatge = tipusMissatge(missatge)
            msg1 = Missatge( remitent = remitent.getUser(), text_missatge = text_missatge, tipus_de_missatge = tipus_de_missatge)
            importancia = 'PI'
            msg1.envia_a_usuari( remitent.getUser(), importancia )    
            msg1.destinatari_set.filter(destinatari = remitent.getUser()).update(moment_lectura=datetime.now())
            
        #Cal que els professors i tutors sàpiguen que aquest alumne ha tingut incidència --> Envio missatge
        remitent = instance.professional
        missatge = INCIDENCIA_INFORMATIVA
        text_missatge = missatge.format(
                                    'informativa ' if instance.tipus.es_informativa else '',
                                    instance.alumne,
                                    instance.alumne.grup,
                                    instance.dia_incidencia,
                                    instance.descripcio_incidencia)
        tipus_de_missatge = tipusMissatge(missatge)
        msg1 = Missatge( remitent = remitent.getUser(), text_missatge = text_missatge, tipus_de_missatge = tipus_de_missatge )
        #si és una unitat formativa envio a tots:
        # if Cursa_nivell( u"CICLES", instance.alumne):
        #     Professor = apps.get_model( 'usuaris','Professor')
        #     professors_que_tenen_aquest_alumne_a_classe = Professor.objects.filter( horari__impartir__controlassistencia__alumne = instance.alumne ).exclude( pk = instance.professional.pk ).distinct()
        #     for professor in professors_que_tenen_aquest_alumne_a_classe:
        #         esTutor = True if professor in instance.alumne.tutorsDeLAlumne() else False
        #         importancia = 'VI' if esTutor else 'PI'
        #         msg1.envia_a_usuari( professor.getUser(), importancia )
        # else:
        #     professors_tutors_de_l_alumne = [ p for p in instance.alumne.tutorsDeLAlumne() ]
        #     for professor in professors_tutors_de_l_alumne:
        #         importancia = 'PI'
        #         msg1.envia_a_usuari( professor.getUser(), importancia )

        professors_tutors_de_l_alumne = [p for p in instance.alumne.tutorsDeLAlumne()]
        for professor in professors_tutors_de_l_alumne:
            importancia = 'PI'
            msg1.envia_a_usuari(professor.getUser(), importancia)

        if instance.tipus.notificar_equip_directiu:
            #es notifica aquest tipus d'incidència a tots els membres de l'equip directiu
            Professor = apps.get_model( 'usuaris','Professor')
            membres_equip_directiu = Professor.objects.filter( groups__name = u"direcció" )
            for professor in membres_equip_directiu:
                msg1.envia_a_usuari( professor.getUser(), 'VI' )
                
