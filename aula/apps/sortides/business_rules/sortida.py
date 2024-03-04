# This Python file uses the following encoding: utf-8
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from aula.apps.tutoria.models import Tutor
from django.apps import apps
from datetime import timedelta
from django.conf import settings
from aula.utils.tools import unicode


def clean_sortida(instance):
    errors = []

    instance.estat_sincronitzacio = instance.__class__.NO_SINCRONITZADA

    if hasattr(instance, 'flag_clean_nomes_toco_alumnes'):
        return

    (user, l4) = instance.credentials if hasattr(instance, 'credentials') else (None, None,)

    instance.instanceDB = None  # Estat a la base de dades
    if instance.pk:
        instance.instanceDB = instance.__class__.objects.get(pk=instance.pk)

    # ('E', u'Esborrany',),
    #     ('P', u'Proposada',),
    #     ('R', u'Revisada pel Coordinador',),
    #     ('G', u"Gestionada pel Cap d'estudis",),

    if instance.informacio_pagament == None or instance.informacio_pagament == '':
        instance.informacio_pagament = settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ENTITAT_BANCARIA \
            if instance.tipus_de_pagament == 'EB' else settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_EFECTIU if \
                instance.tipus_de_pagament == 'EF' else settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ONLINE if instance.tipus_de_pagament == 'ON' else ''


        # if instance.tipus_de_pagament == 'EB':
        #     instance.informacio_pagament = settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ENTITAT_BANCARIA
        # elif instance.tipus_de_pagament == 'EF':
        #     instance.informacio_pagament = settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_EFECTIU
        # elif instance.tipus_de_pagament == 'ON':
        #     instance.informacio_pagament = settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ONLINE


            # Per estats >= G només direcció pot tocar:
    if bool(instance.instanceDB) and instance.instanceDB.estat in ['G']:
        if not User.objects.filter(pk=user.pk, groups__name='direcció').exists():
            errors.append(u"Només Direcció pot modificar una sortida que s'està gestionant.")

            # Per estats >= R només direcció pot tocar:
    if bool(instance.instanceDB) and instance.instanceDB.estat in ['R', 'G']:
        if not User.objects.filter(pk=user.pk, groups__name__in=['sortides', 'direcció']).exists():
            errors.append(
                u"Només el Coordinador de Sortides i Direcció pot modificar una sortida que s'està gestionant.")

            # si passem a proposat
    if instance.estat in ('P', 'R') and instance.tipus!= 'P':
        if (not bool(instance.calendari_desde) or
                not bool(instance.calendari_finsa) or
                    instance.calendari_desde < datetime.now() or
                    instance.calendari_finsa < instance.calendari_desde
            ):
            errors.append(u"Comprova les dates del calendari")

    # si passem a revisada
    if instance.estat in ('R',):

        if not User.objects.filter(pk=user.pk, groups__name__in=['sortides', 'direcció']).exists():
            errors.append(u"Només el coordinador de sortides (i direcció) pot Revisar Una Sortida")

        if not bool(instance.instanceDB) or instance.instanceDB.estat not in ['P', 'R']:
            errors.append(u"Només es pot Revisar una sortida ja Proposada")

        if bool(instance.instanceDB) and instance.instanceDB.estat in ['G']:
            errors.append(u"Aquesta sortida ja ha està sent gestionada.")

        if not instance.esta_aprovada_pel_consell_escolar in ['A', 'N'] and instance.tipus!= 'P':
            errors.append(u"Cal que l'activitat estigui aprovada pel consell escolar per poder-la donar per revisada.")

    # si passem a gestionada pel cap d'estudis
    if instance.estat in ('G',):

        if not User.objects.filter(pk=user.pk, groups__name='direcció').exists():
            errors.append(u"Només el Direcció pot Gestionar una Sortida.")

            #         if not bool(instance.instanceDB) or instance.instanceDB.estat not in [ 'P', 'R' ]:
            #             errors.append( u"Només es pot Gestionar una Sortida Revisada" )

    # només direcció o grup sortides pot marcar com aprovada pel CE
    if ((not bool(instance.pk) and instance.esta_aprovada_pel_consell_escolar != 'P')
        or
            (bool(instance.instanceDB) and
                     instance.instanceDB.esta_aprovada_pel_consell_escolar != instance.esta_aprovada_pel_consell_escolar)
        ):
        if not User.objects.filter(pk=user.pk, groups__name__in=['sortides', 'direcció']).exists():
            errors.append(u"Només Direcció o el coordinador de sortides pot marcar com aprovada pel Consell Escolar.")

    # només direcció o grup sortides pot tocar
    if ((not bool(instance.pk) and instance.codi_de_barres != '')
        or
            (bool(instance.instanceDB) and
                     instance.instanceDB.codi_de_barres != instance.codi_de_barres)
        ):
        if not User.objects.filter(pk=user.pk, groups__name__in=['sortides', 'direcció']).exists():
            errors.append(u"Només Direcció o el coordinador de sortides pot posar el codi de barres.")

    # només direcció o grup sortides pot tocar
    # if ( instance.informacio_pagament != settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT) :
    #    if not User.objects.filter( pk=user.pk, groups__name__in = [ 'sortides', 'direcció' ] ).exists():
    #        errors.append( u"Només Direcció o el coordinador de sortides pot posar informació de pagament." )

    # només direcció o grup sortides pot tocar. Tenim tres missatges diferents

    if ( instance.informacio_pagament not in [settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_EFECTIU,settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ENTITAT_BANCARIA,settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ONLINE,'']) :
        if not User.objects.filter( pk=user.pk, groups__name__in = [ 'sortides', 'direcció' ] ).exists():
            errors.append( u"Només Direcció o el coordinador de sortides pot posar informació de pagament." )

    if (User.objects.filter(pk=user.pk, groups__name__in=['sortides', 'direcció']).exists() and
            instance.tipus_de_pagament == 'ON' and
            instance.estat not in ['E', 'P'] and
            (instance.preu_per_alumne == None or
             instance.preu_per_alumne < settings.CUSTOM_PREU_MINIM_SORTIDES_PAGAMENT_ONLINE)):
        errors.append(
            u"Preu mínim per poder fer el pagament online: {0} €".format(settings.CUSTOM_PREU_MINIM_SORTIDES_PAGAMENT_ONLINE))



    dades_presencia = [bool(instance.data_inici),
                       bool(instance.franja_inici),
                       bool(instance.data_fi),
                       bool(instance.franja_fi), ]
    entrat_a_mitges = len(set(dades_presencia)) > 1
    if entrat_a_mitges:
        instance.data_inici = None
        instance.data_fi = None
        instance.franja_inici = None
        instance.franja_fi = None
        #errors.append(u"Dates i franges de control de presencia cal entrar-les totes o cap")

    if l4:
        pass
    elif bool(errors):
        raise ValidationError(errors)


def sortida_m2m_changed(sender, instance, action, reverse, model, pk_set, *args, **kwargs):
    # Un cop gestionada pel cap d'estudis ja no es pot tocar pels mortals.
    (user, l4) = instance.credentials if hasattr(instance, 'credentials') else (None, None,)
    if instance.pk:
        instance.instanceDB = instance.__class__.objects.get(pk=instance.pk)
    errors = []

    # Alumnes justificats que no estan convocats:
    if action in ("post_add", "post_clear", "post_remove"):
        # comprovar alumnes justificats a la llista de convocats
        alumnesJustificats = set([a.pk for a in instance.alumnes_justificacio.all()])
        alumnesQueVenen = set([a.pk for a in instance.alumnes_convocats.all()])
        justificats_que_venen = alumnesJustificats - alumnesQueVenen
        if bool(justificats_que_venen):
            l = list([a for a in instance.alumnes_justificacio.all() if a.pk in justificats_que_venen])
            l_str = u", ".join([unicode(a) for a in l[:3]])
            if len(l) > 3:
                l_str += ' i ' + unicode(len(l)) + ' més.'
            errors.append(u"Hi ha alumnes que no vindran a la sortida, tenen justificat no assistir al Centre i no estan convocats: " + l_str)

    # Per estats >= G només direcció pot tocar:
    if bool(instance.instanceDB) and instance.instanceDB.estat in ['G']:
        if not User.objects.filter(pk=user.pk, groups__name='direcció').exists():
            errors.append(u"Només Direcció pot modificar una sortida que s'està gestionant.")

    if l4:
        pass
    elif bool(errors):
        raise ValidationError(errors)

    if action in ("post_add", "post_clear", "post_remove"):

        # a la llista 'alumnesQueNoVenen' no poden haver altres alumnes dels que apareixen a 'alumnesQueVenen'
        alumnesQueVenen = set([i.pk for i in instance.alumnes_convocats.all()])
        alumnesQueNoVenen = set([i.pk for i in instance.alumnes_que_no_vindran.all()])
        alumnesATreure = alumnesQueNoVenen - (alumnesQueVenen & alumnesQueNoVenen)
        for alumne in alumnesATreure:
            instance.alumnes_que_no_vindran.remove(alumne)

        # a la llista 'alumnesJustificats' no poden haver altres alumnes dels que apareixen a 'alumnesQueVenen'
        alumnesJustificats = set([i.pk for i in instance.alumnes_justificacio.all()])
        alumnesATreure = alumnesJustificats - (alumnesQueVenen & alumnesJustificats)
        for alumne in alumnesATreure:
            instance.alumnes_justificacio.remove(alumne)

        # els alumnes justificats han d'aparèixer a la llista d'alumnes que no vindran
        alumnesQueNoVenen = set([i.pk for i in instance.alumnes_que_no_vindran.all()])
        for alumne in (alumnesJustificats - alumnesQueNoVenen):
            instance.alumnes_que_no_vindran.add(alumne)

        # actualitzo index de participació
        instance.participacio = u"{0} de {1}".format(instance.alumnes_convocats.count() - instance.alumnes_que_no_vindran.count(),
                                                     instance.alumnes_convocats.count())
        instance.__class__.objects.filter(pk=instance.pk).update(participacio=instance.participacio)

        # actualitzo professors acompanyants.
        if instance.professor_que_proposa not in instance.professors_responsables.all():
            instance.professors_responsables.add(instance.professor_que_proposa)

        # actualitzem tutors alumnes  #TODO: falten tutors individualitzats
        tutors = Tutor.objects.filter(grup__id__in=instance.alumnes_convocats.values_list('grup', flat=True).distinct())
        instance.tutors_alumnes_convocats.set([t.professor for t in tutors])

        # marco que cal sincronitzar ( posar alumnes que no han de ser a classe )
        instance.__class__.objects.filter(id=instance.id).update(estat_sincronitzacio=instance.NO_SINCRONITZADA)





