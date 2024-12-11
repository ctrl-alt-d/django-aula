# This Python file uses the following encoding: utf-8
from django.core.exceptions import ValidationError
from aula.apps.tutoria.avis_tutor_faltes import calcular_dades_carta


def cartaabsentisme_clean( instance ):
    '''
    calcular tipus:
        tipus1 = primera carta tots
        tipus2 = segona carta tots
        tipus3A = tercera carta ESO menors 16 anys
        tipus3B = carta Batxillerat
        tipus3C = cursa obligatoria i té més de 16 anys
        tipus3D = carta Cicles
    '''
    errors = []
    llindar = 0
    instance.__is_update = instance.pk is not None
    if not instance.__is_update:
        dades_carta = calcular_dades_carta(instance.alumne, instance.data_carta)
        if dades_carta['nfaltes'] < dades_carta['llindar']:
            raise ValidationError(
                u'Aquest alumne no ha acumulat {} faltes des de la darrera carta'.format(dades_carta['llindar']))
        instance.carta_numero = dades_carta['carta_numero']
        instance.tipus_carta = dades_carta['tipus_carta']
        instance.faltes_des_de_data = dades_carta['faltes_des_de_data']
        instance.faltes_fins_a_data = dades_carta['faltes_fins_a_data']
        instance.nfaltes = dades_carta['nfaltes']
        errors = dades_carta['errors']
        llindar = dades_carta['llindar']

    if instance.nfaltes < llindar:
        errors.append(u'Aquest alumne no ha acumulat {} faltes des de la darrera carta'.format(llindar))

    if len( errors ) > 0:
        raise ValidationError(errors)
    
                                         


