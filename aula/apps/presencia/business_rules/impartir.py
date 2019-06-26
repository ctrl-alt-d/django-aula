# This Python file uses the following encoding: utf-8
from django.apps import apps

#-------------Impartir-------------------------------------------------------------
from aula.apps.aules.models import ReservaAula, Aula
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.missatgeria.models import Missatge
from django.contrib.auth.models import User
from aula.apps.missatgeria.missatges_a_usuaris import PASSAR_LLISTA_GRUP_NO_MEU, HAN_PASSAT_LLISTA_PER_MI, \
    tipusMissatge, SISTEMA_ANULA_RESERVA
from aula.utils.tools import unicode

def impartir_clean( instance ):
    pass

def impartir_pre_delete( sender, instance, **kwargs):
    pass


def impartir_post_delete( sender, instance, **kwargs):
    # Esborrar la reserva
    reserva_compartida = (bool(instance.reserva)
                          and instance.reserva.impartir_set.count() > 1 )
    if (not reserva_compartida 
        and instance.reserva is not None ):
        fake_l4_credentials = (None, True)
        instance.reserva.credentials = fake_l4_credentials
        instance.reserva.delete()
        instance.reserva = None
        instance.reserva_id = None

def impartir_pre_save(sender, instance,  **kwargs):

    instance.clean()
    #reserva_compartida = (bool(instance.reserva)
    #                      and instance.reserva.impartir_set.count() > 1 )
    #if (not reserva_compartida 
    #    and instance.reserva is not None 
    #    and not instance.reserva.es_reserva_manual ):
    #    fake_l4_credentials = (None, True)
    #    instance.reserva.credentials = fake_l4_credentials
    #    instance.reserva.delete()
    #    instance.reserva = None
    #    instance.reserva_id = None


def impartir_post_save(sender, instance, created, **kwargs):

    # Mantenir reserva o assignar-li una de nova
    # Si el professor havia fet un canvi d'aula cal respectar-ho.
    aula_informada_a_l_horari = instance.horari.aula is not None and bool( instance.horari.aula )
    te_reserva = instance.reserva is not None
    es_reserva_manual = te_reserva and instance.reserva.es_reserva_manual
    cal_assignar_nova_reserva = not te_reserva and aula_informada_a_l_horari and not es_reserva_manual
    if cal_assignar_nova_reserva:
        reserves = ReservaAula.objects.filter( aula=instance.horari.aula,
                                               dia_reserva=instance.dia_impartir,
                                               hora=instance.horari.hora )

        reserves_manuals = list( reserves.filter( es_reserva_manual = True ) )
        reserves_automatiques = list( reserves.filter(es_reserva_manual=False) )
        
        usuari_notificacions, new = User.objects.get_or_create( username = 'TP')
        for reserva in reserves_manuals:
            impartir = reserva.impartir_set.first()
            if impartir:
                missatge = SISTEMA_ANULA_RESERVA
                msg = missatge.format(impartir)
                reserva.aula = impartir.horari.aula
                reserva.es_reserva_manual = False
                fake_l4_credentials = (None, True ) 
                reserva.credentials = fake_l4_credentials
                reserva.save()
                tipus_de_missatge = tipusMissatge(missatge)
                msg = Missatge(
                    remitent=usuari_notificacions,
                    text_missatge=msg,
                    tipus_de_missatge = tipus_de_missatge,
                    )
                msg.envia_a_usuari(reserva.usuari,'VI')                   
            else:
                reserva.delete()        
                
        #if bool(reserves_automatiques):
        #    reserva_a_assignar = reserves_automatiques[0]
        #else:
        reserva_a_assignar = ReservaAula(aula=instance.horari.aula,
                                      dia_reserva=instance.dia_impartir,
                                      hora_inici=instance.horari.hora.hora_inici,
                                      hora_fi=instance.horari.hora.hora_fi,
                                      hora=instance.horari.hora,
                                      usuari=instance.horari.professor,
                                      motiu=u"Docència",
                                      es_reserva_manual=False )
        reserva_a_assignar.save()

        instance.__class__.objects.filter(pk=instance.pk).update(reserva_id=reserva_a_assignar.pk)
        instance.refresh_from_db()

    #bussiness rule:
    #si un professor passa llista, també passa llista de 
    #totes les imparticions que no tinguin alumnes.
    if instance.professor_passa_llista is not None:
        Impartir = apps.get_model('presencia','Impartir')
        altresHores = Impartir.objects.filter( horari__hora = instance.horari.hora, 
                                               dia_impartir = instance.dia_impartir,
                                               controlassistencia__isnull = True,
                                               horari__professor = instance.horari.professor,
                                               horari__grup__isnull = False  )
        
        altresHores.update( professor_passa_llista = instance.professor_passa_llista,
                           dia_passa_llista = instance.dia_passa_llista )
    
    pass

def impartir_despres_de_passar_llista(instance):
    #Si passa llista un professor que no és el de l'Horari cal avisar.
    if instance.professor_passa_llista != instance.horari.professor:
        remitent = instance.professor_passa_llista
        missatge = PASSAR_LLISTA_GRUP_NO_MEU
        text_missatge = missatge.format( unicode(instance),  unicode(instance.horari.professor) )
        Missatge = apps.get_model( 'missatgeria','Missatge')
        tipus_de_missatge = tipusMissatge (missatge)
        msg = Missatge( remitent = remitent.getUser(), text_missatge = text_missatge, tipus_de_missatge = tipus_de_missatge)
        msg.envia_a_usuari( usuari = instance.professor_passa_llista.getUser(), importancia = 'VI')

        missatge = HAN_PASSAT_LLISTA_PER_MI
        text_missatge = missatge.format( unicode(instance),  unicode(instance.horari.professor) )
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge( remitent = remitent.getUser(), text_missatge = text_missatge, tipus_de_missatge = tipus_de_missatge )
        msg.envia_a_usuari( usuari = instance.horari.professor.getUser(), importancia = 'VI')
