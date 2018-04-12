# This Python file uses the following encoding: utf-8
from django.core.exceptions import ValidationError
from django.utils.datetime_safe import datetime
from datetime import timedelta

def reservaaula_clean(instance):
    ( user, l4)  = instance.credentials if hasattr( instance, 'credentials') else (None,False,)

    if l4:
        return
    
    errors = {}
    ReservaAula = instance.__class__
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

    data_del_passat = ( instance.dia_reserva < datetime.today().date() )
    
    if data_del_passat:
         errors.setdefault('dia_reserva', []).append(u'Compte! Aquesta data de reserva és del passat!')       

    tretze_dies = timedelta( days = 13 )
    darrer_dia_reserva = datetime.today().date() + tretze_dies - timedelta( days = datetime.today().weekday() )
    if instance.dia_reserva > darrer_dia_reserva:
         errors.setdefault('dia_reserva', []).append(u"Només pots reservar fins al dia {0}".format(darrer_dia_reserva))       

    if len(errors) > 0:
        raise ValidationError(errors)




def reservaaula_pre_save(sender, instance, **kwargs):
    instance.clean()

def reservaaula_post_save(sender, instance, created, **kwargs):
    pass

def reservaaula_pre_delete(sender, instance, **kwargs):
    pass