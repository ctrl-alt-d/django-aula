# This Python file uses the following encoding: utf-8
from django.core.exceptions import ValidationError
from django.utils.datetime_safe import datetime
from datetime import timedelta
from django.apps import apps


def reservaaula_clean(instance):
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,False,)

    if l4:
        return
    
    errors = {}
    ReservaAula = instance.__class__

    # -- No es pot reservar una aula ocupada
    if instance.es_reserva_manual:
        aulaOcupada = ReservaAula.objects.filter(hora = instance.hora,
                                                aula = instance.aula,
                                                dia_reserva = instance.dia_reserva).exclude(pk=instance.pk).exists()

        if aulaOcupada:
            professorsQueOcupen = [reserva.usuari.first_name + ' ' +
                                reserva.usuari.last_name for reserva in ReservaAula.objects.filter(hora = instance.hora,
                                                                                                    aula = instance.aula,
                                                                                                    dia_reserva = instance.dia_reserva)]
            errors.setdefault('hora', []).append(u'''Aula ocupada en aquesta hora per ''' +
                                                ','.join(professorsQueOcupen))

    # -- Només es poden fer reserves de la data actual en endavant
    if instance.es_reserva_manual:
        data_del_passat = ( instance.dia_reserva < datetime.today().date() )
        if data_del_passat:
            errors.setdefault('dia_reserva', []).append(u'Compte! Aquesta data de reserva és del passat!')       

    # -- No es pot reservar més enllà de 15 dies
    if instance.es_reserva_manual:
        tretze_dies = timedelta( days = 13 )
        darrer_dia_reserva = datetime.today().date() + tretze_dies - timedelta( days = datetime.today().weekday() )
        if instance.dia_reserva > darrer_dia_reserva:
            errors.setdefault('dia_reserva', []).append(u"Només pots reservar fins al dia {0}".format(darrer_dia_reserva))       

    # -- No es pot reservar més aviat ni més tard de la primera i darrera docència d'aquell dia
    if instance.es_reserva_manual:
        FranjaHoraria = apps.get_model( 'horaris','FranjaHoraria')
        franges_del_dia = ( FranjaHoraria
                        .objects
                        .filter( horari__impartir__dia_impartir = instance.dia_reserva )
                        .order_by('hora_inici')
                        )
        primera_franja = franges_del_dia.first()
        darrera_franja = franges_del_dia.last()

        franges_reservables = ( FranjaHoraria
                                .objects
                                .filter(hora_inici__gte = primera_franja.hora_inici)
                                .filter(hora_fi__lte = darrera_franja.hora_fi)
                                ) if primera_franja and darrera_franja else []
        if instance.hora not in franges_reservables:
            errors.setdefault('hora', []).append(u"En aquesta hora no hi ha docència al centre")

    # -- Si l'aula té restricció horària només es pot reservar en aquelles hores
    if instance.es_reserva_manual:
        disponibilitatHoraria = list( instance.aula.disponibilitat_horaria.all() )
        if bool(disponibilitatHoraria) and instance.hora not in disponibilitatHoraria:
            errors.setdefault('hora', []).append(u"No està previst que es pugui reservar aquesta aula en aquest horari")

    #
    if len(errors) > 0:
        raise ValidationError(errors)


def reservaaula_pre_save(sender, instance, **kwargs):
    instance.clean()

def reservaaula_post_save(sender, instance, created, **kwargs):
    pass

def reservaaula_pre_delete(sender, instance, **kwargs):
    pass