# This Python file uses the following encoding: utf-8
from django.apps import apps

#-------------Impartir-------------------------------------------------------------
from aula.apps.aules.models import ReservaAula, Aula
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.missatgeria.models import Missatge


def impartir_clean( instance ):
    pass

def impartir_pre_delete( sender, instance, **kwargs):
    pass
    
def impartir_pre_save(sender, instance,  **kwargs):

    instance.clean()

    reserva_compartida = (instance.reserva is not None 
                          and instance.reserva.impartir_set.count() > 1 )
    if (not reserva_compartida 
        and instance.reserva is not None 
        and not instance.es_reserva_manual ):
        instance.reserva.delete()


def impartir_post_save(sender, instance, created, **kwargs):

    # Mantenir reserva o assignar-li una de nova
    # Si el professor havia fet un canvi d'aula cal respectar-ho.
    aula_informada_a_l_horari = instance.horari.aula is not None
    te_reserva = instance.reserva is not None
    te_reserva_manual = te_reserva and instance.reserva.es_reserva_manual
    cal_assignar_nova_reserva = aula_informada_a_l_horari and not te_reserva_manual
    if cal_assignar_nova_reserva:
        reserves = ReservaAula.objects.filter( aula=instance.horari.aula,
                                               dia_reserva=instance.dia_impartir,
                                               hora=instance.horari.hora )

        reserves_manuals = list( reserves.filter( impartir__isnull = True ) )
        usuari_notificacions, new = User.objects.get_or_create( username = 'TP')
        for reserva in reserves_manuals:
            reserva.delete()
            msg = Missatge(
                remitent=usuari_notificacions,
                text_missatge=u"El sistema ha hagut d'anul·lar la teva reserva d'aula: {0}".format(reserva),
                )
            msg.envia_a_usuari(reserva.usuari,'VI')            

        reserves_automatiques = list( reserves.filter(impartir__isnull=False) )
        if bool(reserves_automatiques):
            reserva = reserves_automatiques[0]
        else:
            novareserva = ReservaAula(aula=instance.horari.aula,
                                      dia_reserva=instance.dia_impartir,
                                      hora_inici=instance.horari.hora.hora_inici,
                                      hora_fi=instance.horari.hora.hora_fi,
                                      hora=instance.horari.hora,
                                      usuari=instance.horari.professor,
                                      motiu=u"Docència",
                                      es_reserva_manual=False )
            novareserva.save()
            reserva = novareserva

        instance.__class__.objects.filter(pk=instance.pk).update(reserva_id=reserva)
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
    if instance.professor_passa_llista <> instance.horari.professor:
        remitent = instance.professor_passa_llista
        text_missatge = u"""Has passat llista a un grup que no és el teu: ({0}). 
                         El professor del grup {1} rebrà un missatge com aquest.
                         """.format( unicode(instance),  unicode(instance.horari.professor) )
        Missatge = apps.get_model( 'missatgeria','Missatge')
        msg = Missatge( remitent = remitent.getUser(), text_missatge = text_missatge )           
        msg.envia_a_usuari( usuari = instance.professor_passa_llista.getUser(), importancia = 'VI')

        text_missatge = u"""Ha passat llista d'una classe on consta que la fas tú: ({0}). 
                         """.format( unicode(instance),  unicode(instance.horari.professor) )
        msg = Missatge( remitent = remitent.getUser(), text_missatge = text_missatge )           
        msg.envia_a_usuari( usuari = instance.horari.professor.getUser(), importancia = 'VI')
    

