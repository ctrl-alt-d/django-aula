# This Python file uses the following encoding: utf-8
from django.core.exceptions import ValidationError



def reservaaula_clean(instance):
    errors = {}
    ReservaAula = instance.__class__
    aulaOcupada = ReservaAula.objects.filter(hora = instance.hora,
                                             aula = instance.aula,
                                             dia_reserva = instance.dia_reserva).exclude(pk=instance.pk).exists()
    #
    # Pre-save
    #
    if aulaOcupada:
        professorsQueOcupen = [reserva.usuari.first_name + ' ' +
                               reserva.usuari.last_name for reserva in ReservaAula.objects.filter(hora = instance.hora,
                                                                                                  aula = instance.aula,
                                                                                                  dia_reserva = instance.dia_reserva)]
        errors.setdefault('hora', []).append(u'''Aula ocupada en aquesta hora per ''' +
                                             ','.join(professorsQueOcupen))
    else:
        pass
    if len(errors) > 0:
        raise ValidationError(errors)




def reservaaula_pre_save(sender, instance, **kwargs):
    instance.clean()

def reservaaula_post_save(sender, instance, created, **kwargs):
    pass

def reservaaula_pre_delete(sender, instance, **kwargs):
    pass