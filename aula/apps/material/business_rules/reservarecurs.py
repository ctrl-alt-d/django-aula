# This Python file uses the following encoding: utf-8
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.datetime_safe import datetime
from datetime import timedelta
from django.db.models import Q
from django.contrib.auth.models import User
from django.apps import apps

from ....apps.missatgeria.missatges_a_usuaris import SISTEMA_ANULA_RESERVA, tipusMissatge

def reservarecurs_clean(instance):
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (instance.usuari,False,)
    if instance.hora:
        instance.hora_inici = instance.hora.hora_inici
        instance.hora_fi = instance.hora.hora_fi

    if l4:
        return
    
    errors = {}
    ReservaRecurs = instance.__class__

    # -- No es pot reservar una recurs no reservable
    if instance.es_reserva_manual:
        if not instance.recurs.reservable:
            errors.setdefault('hora', []).append(u'''Material exempt de reserves. No pot ser reservat.''')

    # -- No es pot reservar un recurs ocupat
    if instance.es_reserva_manual:
        recursReservat = ( ReservaRecurs
                       .objects.filter(hora = instance.hora,
                                                recurs = instance.recurs,
                                                dia_reserva = instance.dia_reserva)
                       .exclude(pk=instance.pk)
                       .exists() )

        if recursReservat:
            professorsQueReserven = [reserva.usuari.first_name + ' ' +
                                reserva.usuari.last_name for reserva in ReservaRecurs.objects.filter(hora = instance.hora,
                                                                                                    recurs = instance.recurs,
                                                                                                    dia_reserva = instance.dia_reserva)]
            errors.setdefault('hora', []).append(u'''Material ocupat en aquesta hora per ''' +
                                                ','.join(professorsQueReserven))

    # -- Només es poden fer reserves de la data actual en endavant
    if instance.es_reserva_manual:
        data_del_passat = ( instance.dia_reserva < datetime.today().date() )
        if data_del_passat:
            errors.setdefault('dia_reserva', []).append(u'Compte! Aquesta data de reserva és del passat!')       

    # -- No es pot reservar més enllà de 15 dies si l'usuari no és reservador
    es_reservador = User.objects.filter(pk=user.pk, groups__name__in=['reservador']).exists()
    if instance.es_reserva_manual and not es_reservador:
        tretze_dies = timedelta( days = 13 )
        darrer_dia_reserva = datetime.today().date() + tretze_dies - timedelta( days = datetime.today().weekday() )
        if instance.dia_reserva > darrer_dia_reserva:
            errors.setdefault('dia_reserva', []).append(u"Només pots reservar fins al dia {0}".format(darrer_dia_reserva))       

    # -- No es pot reservar més aviat ni més tard de la primera i darrera docència d'aquell dia
    if instance.es_reserva_manual:
        Impartir = apps.get_model( 'presencia','Impartir')

        q_hi_ha_docencia_abans = Q(horari__hora__hora_inici__lte = instance.hora.hora_inici)
        q_hi_ha_docencia_despres = Q(horari__hora__hora_fi__gte = instance.hora.hora_fi)
        hi_ha_classe_al_centre_aquella_hora = ( Impartir
                                                .objects
                                                .filter( dia_impartir = instance.dia_reserva )
                                                .filter( q_hi_ha_docencia_abans|q_hi_ha_docencia_despres  )
                                                .exists ()
                                                )
        if not hi_ha_classe_al_centre_aquella_hora:
            errors.setdefault('hora', []).append(u"En aquesta hora no hi ha docència al centre")


    # -- Si el material té restricció horària només es pot reservar en aquelles hores
    if instance.es_reserva_manual:
        disponibilitatHoraria = list( instance.recurs.disponibilitat_horaria.all() )
        if bool(disponibilitatHoraria) and instance.hora not in disponibilitatHoraria:
            errors.setdefault('hora', []).append(u"No està previst que es pugui reservar aquest material en aquest horari")

    #
    if len(errors) > 0:
        raise ValidationError(errors)


def reservarecurs_pre_save(sender, instance, **kwargs):
    instance.clean()

def reservarecurs_post_save(sender, instance, created, **kwargs):
    pass

def reservarecurs_pre_delete(sender, instance, **kwargs):
    errors = {}
    (user, l4) = instance.credentials if hasattr(instance,"credentials") else (None, False)
    usuari_informat = bool(user)
    es_meva = usuari_informat and instance.usuari.pk == user.pk

    if not l4 and usuari_informat and not es_meva:
        errors.setdefault('usuari', []).append(u"Només pots anul·lar les teves reserves.")
        raise ValidationError(errors)

    if len(errors) > 0:
        raise ValidationError(errors)    

def reservarecurs_post_delete( sender, instance, **lwargs ):

    if instance.es_reserva_manual:
        usuari_notificacions, _ = User.objects.get_or_create( username = 'TP')
        Missatge = apps.get_model( 'missatgeria','Missatge')
        missatge = SISTEMA_ANULA_RESERVA
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge(
            remitent=usuari_notificacions,
            text_missatge=missatge.format(instance),
            tipus_de_missatge = tipus_de_missatge,
            )
        msg.envia_a_usuari(instance.usuari, 'VI')
