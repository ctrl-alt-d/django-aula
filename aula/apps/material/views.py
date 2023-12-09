# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# workflow
import os

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect

# auth
from django.contrib.auth.decorators import login_required

# tables
from django.utils.safestring import SafeText
from django_tables2 import RequestConfig

from aula import settings
from aula.apps.material.tables2_models import HorariRecursTable, Table2_ReservaRecurs
from aula.apps.missatgeria.missatges_a_usuaris import tipusMissatge, PROFESSOR_RESERVA_MASSIVA
from aula.apps.missatgeria.models import Missatge
from aula.utils.my_paginator import DiggPaginator

# models
from aula.apps.material.models import Recurs, ReservaRecurs
from aula.apps.horaris.models import FranjaHoraria, Horari
from aula.apps.presencia.models import Impartir
from django.db.models import Q

# forms
from aula.apps.material.forms import (
    reservaRecursForm,
    disponibilitatRecursPerRecursForm,
    carregaComentarisRecursForm, disponibilitatRecursPerFranjaForm, RecursosForm,
    disponibilitatMassivaRecursPerFranjaForm, reservaMassivaRecursForm)

# helpers
from aula.apps.usuaris.models import User2Professor, Professor
from aula.utils.decorators import group_required
from aula.utils import tools
from aula.utils.tools import unicode
from django.contrib import messages
import csv
from datetime import datetime
from datetime import timedelta


@login_required
@group_required(['professors', 'professional', 'consergeria'])
def reservaRecursList(request):
    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor(user)

    reserves = (ReservaRecurs
                .objects
                .filter(es_reserva_manual=True)
                .filter(usuari=user)
                )

    table = Table2_ReservaRecurs(reserves)
    table.order_by = ['-dia_reserva', ]

    RequestConfig(request, paginate={"paginator_class": DiggPaginator, "per_page": 30}).configure(table)
    es_reservador = User.objects.filter(pk=user.pk, groups__name__in=['reservador']).exists()
    return render(
        request,
        'reservesRecursos.html',
        {'table': table,
         'es_reservador': es_reservador,
         }
    )


 # -- wizard per recurs 1/3
@login_required
@group_required(['professors', 'professional', 'consergeria'])
def consultaRecursPerRecurs(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    formset = []
    if request.method == 'POST':
        formDisponibilitatRecurs = disponibilitatRecursPerRecursForm(request.POST)

        if formDisponibilitatRecurs.is_valid():
            recurs = formDisponibilitatRecurs.cleaned_data['recurs']
            data = formDisponibilitatRecurs.cleaned_data['data']
            year = data.year
            month = data.month
            date = data.day
            next_url = r'/recursos/detallRecursReserves/{0}/{1}/{2}/{3}'
            return HttpResponseRedirect(next_url.format(year, month, date, recurs.pk))

    else:
        formDisponibilitatRecurs = disponibilitatRecursPerRecursForm()

    return render(
        request,
        'form.html',
        {'form': formDisponibilitatRecurs,
         'head': u'Consultar disponibilitat material',
         'titol_formulari': u"Assistent Reserva de Material (1/3)",
         },
    )


 # -- wizard per recurs 2/3
@login_required
@group_required(['professors', 'professional', 'consergeria'])
def detallRecursReserves(request, year, month, day, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    recurs = get_object_or_404(Recurs, pk=pk)

    #
    import datetime as t
    try:
        year = int(year)
        month = int(month)
        day = int(day)
    except:
        today = t.date.today()
        year = today.year
        month = today.month
        day = today.day

    data = t.date(year, month, day)
    tretze_dies = timedelta(days=13)
    darrer_dia_reserva = datetime.today().date() + tretze_dies - timedelta(days=datetime.today().weekday())
    es_reservador = User.objects.filter(pk=user.pk, groups__name__in=['reservador']).exists()
    if not es_reservador and (data > darrer_dia_reserva or data < datetime.today().date()):
        msg = u"Aquesta data no permet fer reserves. Només es pot des d'avui i fins al dia {0}".format(
            darrer_dia_reserva)
        messages.warning(request, SafeText(msg))
    reserves_dun_dia_un_recurs = (ReservaRecurs
                                .objects
                                .filter(recurs=recurs)
                                .filter(dia_reserva=data))

    franges_del_dia = (FranjaHoraria
                       .objects
                       .filter(horari__impartir__dia_impartir=data)
                       .order_by('hora_inici')
                       .distinct()
                       )

    # -- si el recurs presenta un horari restringit
    q_horari_restringit = Q()
    disponibilitatHoraria = [franja.pk for franja in recurs.disponibilitat_horaria.all()]
    if bool(disponibilitatHoraria):
        franges_reservades = [reserva.hora.pk for reserva in reserves_dun_dia_un_recurs]
        q_horari_restringit = Q(pk__in=disponibilitatHoraria + franges_reservades)

    # Només les franges que corresponen al dia
    franges_reservables = ( franges_del_dia.filter( q_horari_restringit )) if franges_del_dia else []

    horariRecurs = []
    for franja in franges_reservables:
        # Si la franja es solapa amb una altra ja ocupada, no es mostrarà
        if not reserves_dun_dia_un_recurs.filter(hora__hora_inici=franja.hora_inici, 
                                               hora__hora_fi=franja.hora_fi) \
            and reserves_dun_dia_un_recurs.filter(hora__hora_inici__lt=franja.hora_fi,
                                                hora__hora_fi__gt=franja.hora_inici):
            continue
                
        reserva = reserves_dun_dia_un_recurs.filter(hora=franja).order_by().first()
        nova_franja = {}
        nova_franja['franja'] = franja
        nova_franja['reserva'] = reserva
        nova_franja['professor'] = u", ".join(
            [reserva.usuari.first_name + ' ' + reserva.usuari.last_name]) if reserva else u""
        nova_franja['reservable'] = not bool(reserva) and recurs.reservable
        nova_franja['eliminable'] = bool(reserva) and reserva.usuari.pk == user.pk
        nova_franja['recurs'] = recurs
        nova_franja['dia'] = data
        horariRecurs.append(nova_franja)

    table = HorariRecursTable(horariRecurs)
    table.order_by = 'franja'
    RequestConfig(request).configure(table)

    return render(
        request,
        'mostraInfoReservaRecurs.html',
        {'table': table,
         'recurs': recurs,
         'dia': data,
         'titol_formulari': u"Assistent Reserva de Material (2/3)",
         },
    )


# -- wizard per franja 1/3
@login_required
@group_required(['professors', 'professional', 'consergeria'])
def consultaRecursPerFranja(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    if request.method == 'POST':
        formDisponibilitatRecurs = disponibilitatRecursPerFranjaForm(request.POST, user=request.user)

        if formDisponibilitatRecurs.is_valid():
            franja = formDisponibilitatRecurs.cleaned_data['franja']
            data = formDisponibilitatRecurs.cleaned_data['data']
            year = data.year
            month = data.month
            date = data.day
            next_url = r'/recursos/detallFranjaReserves/{0}/{1}/{2}/{3}'
            return HttpResponseRedirect(next_url.format(year, month, date, franja.pk))

    else:
        formDisponibilitatRecurs = disponibilitatRecursPerFranjaForm(user=request.user)

    for f in formDisponibilitatRecurs.fields:
        formDisponibilitatRecurs.fields[f].widget.attrs['class'] = 'form-control ' + formDisponibilitatRecurs.fields[
            f].widget.attrs.get('class', "")

    return render(
        request,
        'form.html',
        {'form': formDisponibilitatRecurs,
         'head': u'Consultar disponibilitat recurs per franja',
         'titol_formulari': u"Assistent Reserva de Recurs (1/3)",
         },
    )


# -- wizard per franja 2/3
@login_required
@group_required(['professors', 'professional', 'consergeria'])
def detallFranjaReserves(request, year, month, day, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    franja = get_object_or_404(FranjaHoraria, pk=pk)

    import datetime as t
    try:
        year = int(year)
        month = int(month)
        day = int(day)
    except:
        today = t.date.today()
        year = today.year
        month = today.month
        day = today.day

    data = t.date(year, month, day)

    tretze_dies = timedelta(days=13)
    darrer_dia_reserva = datetime.today().date() + tretze_dies - timedelta(days=datetime.today().weekday())
    es_reservador = User.objects.filter(pk=user.pk, groups__name__in=['reservador']).exists()
    if not es_reservador and (data > darrer_dia_reserva or data < datetime.today().date()):
        msg = u"Aquesta data no permet fer reserves. Només es pot des d'avui i fins al dia {0}".format(
            darrer_dia_reserva)
        messages.warning(request, SafeText(msg))

    q_hi_ha_docencia_abans = Q(horari__hora__hora_inici__lte=franja.hora_inici)
    q_hi_ha_docencia_despres = Q(horari__hora__hora_fi__gte=franja.hora_fi)
    hi_ha_classe_al_centre_aquella_hora = (Impartir
                                           .objects
                                           .filter(dia_impartir=data)
                                           .filter(q_hi_ha_docencia_abans | q_hi_ha_docencia_despres)
                                           .exists()
                                           )
    recursos_lliures = Recurs.objects.none()
    if hi_ha_classe_al_centre_aquella_hora:
        # reservables
        reservable_aquella_hora = (Q(disponibilitat_horaria__isnull=True)
                                   | Q(disponibilitat_horaria=franja))
        reservable_aquella_hora_ids = (Recurs
                                       .objects
                                       .filter(reservable_aquella_hora)
                                       .values_list('id', flat=True)
                                       .distinct()
                                       )
        # reservats
        # Recursos ocupats en el dia i franja, també casos de franges solapades
        reservat = Q(reservarecurs__dia_reserva=data) & Q(reservarecurs__hora__hora_inici__lt=franja.hora_fi)\
                    & Q(reservarecurs__hora__hora_fi__gt=franja.hora_inici)
        reservat_ids = (Recurs
                         .objects
                         .filter(reservat)
                         .values_list('id', flat=True)
                         .distinct()
                         )
        # lliures
        recursos_lliures = (Recurs
                         .objects
                         .exclude(reservable=False)
                         .filter(pk__in=reservable_aquella_hora_ids)
                         .exclude(pk__in=reservat_ids)
                         .distinct()
                         )

    if request.method == 'POST':
        form = RecursosForm(queryset=recursos_lliures,
                         data=request.POST,
                         )

        if form.is_valid():
            next_url = r"/recursos/tramitarReservaRecurs/{0}/{1}/{2}/{3}/{4}/"
            return HttpResponseRedirect(next_url.format(form.cleaned_data['recurs'].pk, franja.pk, year, month, day))

    else:
        form = RecursosForm(queryset=recursos_lliures)

    for f in form.fields:
        form.fields[f].widget.attrs['class'] = 'form-control ' + form.fields[f].widget.attrs.get('class', "")

    return render(
        request,
        'form.html',
        {'form': form,
         'titol_formulari': u"Assistent Reserva de Recurs (2/3)",
         },
    )


# -- wizard per recurs ó franja 3/3
@login_required
@group_required(['professors', 'professional', 'consergeria'])
def tramitarReservaRecurs(request, pk_recurs=None, pk_franja=None, year=None, month=None, day=None):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    recurs = Recurs.objects.filter(pk=pk_recurs).first()
    franja = FranjaHoraria.objects.filter(pk=pk_franja).first()

    import datetime as t
    try:
        year = int(year)
        month = int(month)
        day = int(day)
    except:
        today = t.date.today()
        year = today.year
        month = today.month
        day = today.day
    data = t.date(year, month, day)
    tretze_dies = timedelta(days=13)
    darrer_dia_reserva = datetime.today().date() + tretze_dies - timedelta(days=datetime.today().weekday())
    es_reservador = User.objects.filter(pk=user.pk, groups__name__in=['reservador']).exists()
    if not es_reservador and (data > darrer_dia_reserva or data < datetime.today().date()):
        msg = u"Reserva NO realitzada. Només es pot des d'avui i fins al dia {0}".format(
            darrer_dia_reserva)
        messages.warning(request, SafeText(msg))
        return HttpResponseRedirect(r'/recursos/lesMevesReservesDeRecurs/')

    novaReserva = ReservaRecurs(recurs=recurs,
                              hora=franja,
                              dia_reserva=data,
                              usuari=user,
                              es_reserva_manual=True)

    if request.method == 'POST':
        form = reservaRecursForm(request.POST, instance=novaReserva)
        if form.is_valid():
            try:
                reserva = form.save()
                missatge = u"Reserva realitzada correctament"
                messages.success(request, missatge)
                return HttpResponseRedirect(r'/recursos/lesMevesReservesDeRecurs/')

            except ValidationError as e:
                for _, v in e.message_dict.items():
                    form._errors.setdefault(NON_FIELD_ERRORS, []).extend(v)

    else:
        form = reservaRecursForm(instance=novaReserva)

    for f in ['recurs', 'dia_reserva', 'hora', 'motiu']:
        form.fields[f].widget.attrs['class'] = 'form-control ' + form.fields[f].widget.attrs.get('class', "")

    return render(
        request,
        'form.html',
        {'form': form,
         'head': u'Reservar material',
         'titol_formulari': u"Assistent Reserva de Material (3/3)",
         },
    )


# -------------------------------------------------------------------------

@login_required
@group_required(['professors', 'professional', 'consergeria'])
def eliminarReservaRecurs(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials
    reserva = get_object_or_404(ReservaRecurs, pk=pk)
    reserva.credentials = credentials

    try:
        reserva.delete()
        missatge = u"Reserva anul·lada correctament"
        messages.info(request, missatge)
    except ValidationError as e:
        for _, llista_errors in e.message_dict.items():
            missatge = u"No s'ha pogut anul·lar la reserva: {0}".format(
                u", ".join(x for x in llista_errors)
            )
        messages.error(request, missatge)

    # tornem a la mateixa pantalla on erem (en mode incògnit no funciona)
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/recursos/lesMevesReservesDeRecurs/'))


@login_required
@group_required(['direcció'])
def assignaComentarisARecurs(request):
    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor(user)

    errors = []
    warnings = []
    infos = []

    if request.method == 'POST':
        form = carregaComentarisRecursForm(request.POST, request.FILES)

        if form.is_valid():
            info_nRecursosLlegits = 0
            info_nRecursosCreats = 0
            info_nComentarisAfegits = 0
            RecursosCreats = []
            ComentarisAfegits = []

            f = request.FILES['fitxerComentaris']
            path = default_storage.save('tmp/comentarisrecursos.txt', ContentFile(f.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            with open(tmp_file, 'r', encoding="latin-1") as f1:
                reader = csv.DictReader(f1)
                f.seek(0)
                for row in reader:
                    info_nRecursosLlegits += 1
                    nom_recurs = unicode(row['NOM'], 'iso-8859-1')
                    descripcio_recurs = unicode(row['DESC'], 'iso-8859-1')
                    if nom_recurs != '':
                        a, created = Recurs.objects.get_or_create(nom_recurs=nom_recurs,
                                                                defaults={
                                                                    'horari_lliure': False,
                                                                    'reservable': True})
                        if created:
                            info_nRecursosCreats += 1
                            RecursosCreats.append(a.nom_recurs)
                            warnings.append(u'{0}: Recurs creat nou'.format(a.nom_recurs))
                        a.descripcio_recurs = descripcio_recurs
                        info_nComentarisAfegits += 1
                        ComentarisAfegits.append(descripcio_recurs)
                        a.save()
                    else:
                        errors.append('S\'ha trobat material sense nom!!!')
            default_storage.delete(path)
            warnings.append(u'Total recursos nous creats: {0}'.format(info_nRecursosCreats))
            infos.append(u'Total comentaris afegits: {0}'.format(info_nComentarisAfegits))
            resultat = {'errors': errors, 'warnings': warnings, 'infos': infos}
            return render(
                request,
                'resultat.html',
                {'head': 'Resultat càrrega comentaris material',
                 'msgs': resultat},
            )
    else:
        form = carregaComentarisRecursForm()

    return render(
        request,
        'afegirComentarisARecursos.html',
        {'form': form},
    )


# -- wizard massiva per franja 1/3
@login_required
@group_required(['professors', 'professional', 'consergeria'])
def consultaMassivaRecurs (request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    if request.method == 'POST':
        formDisponibilitatRecurs = disponibilitatMassivaRecursPerFranjaForm(request.POST, user=request.user)

        if formDisponibilitatRecurs.is_valid():
            franja = formDisponibilitatRecurs.cleaned_data['franja']
            data_inici = formDisponibilitatRecurs.cleaned_data['data_inici']
            data_fi = formDisponibilitatRecurs.cleaned_data['data_fi']
            year_inici = data_inici.year
            year_fi = data_fi.year
            month_inici = data_inici.month
            month_fi = data_fi.month
            date_inici = data_inici.day
            date_fi = data_fi.day
            next_url = r'/recursos/detallMassiuFranjaReserves/{0}/{1}/{2}/{3}/{4}/{5}/{6}'
            return HttpResponseRedirect(next_url.format(year_inici, year_fi, month_inici, month_fi, date_inici, date_fi, franja.pk))

    else:
        formDisponibilitatRecurs = disponibilitatMassivaRecursPerFranjaForm(user=request.user)

    for f in formDisponibilitatRecurs.fields:
        formDisponibilitatRecurs.fields[f].widget.attrs['class'] = 'form-control ' + formDisponibilitatRecurs.fields[
            f].widget.attrs.get('class', "")

    return render(
        request,
        'form.html',
        {'form': formDisponibilitatRecurs,
         'head': u'Consultar disponibilitat recurs per franja',
         'titol_formulari': u"Assistent Reserva Massiva de Material (1/3)",
         },
    )


# -- wizard massiva per franja 2/3
@login_required
@group_required(['professors', 'professional', 'consergeria'])
def detallMassiuFranjaReserves(request, year_inici, year_fi, month_inici, month_fi, day_inici, day_fi, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    franja = get_object_or_404(FranjaHoraria, pk=pk)

    import datetime as t
    try:
        year_inici = int(year_inici)
        month_inici = int(month_inici)
        day_inici = int(day_inici)
        year_fi = int(year_fi)
        month_fi = int(month_fi)
        day_fi = int(day_fi)
    except:
        today = t.date.today()
        year_inici = today.year
        month_inici = today.month
        day_inici = today.day
        year_fi = today.year
        month_fi = today.month
        day_fi = today.day

    data_inici = t.date(year_inici, month_inici, day_inici)
    data_fi = t.date(year_fi, month_fi, day_fi)

    es_reservador = User.objects.filter(pk=user.pk, groups__name__in=['reservador']).exists()
    if not es_reservador:
        msg = u"No tens permís per reservar un bloc de dies"
        messages.warning(request, SafeText(msg))

    q_hi_ha_docencia_abans = Q(horari__hora__hora_inici__lte=franja.hora_inici)
    q_hi_ha_docencia_despres = Q(horari__hora__hora_fi__gte=franja.hora_fi)
    hi_ha_classe_al_centre_aquella_hora = (Impartir
                                           .objects
                                           .filter(dia_impartir=data_inici)
                                           .filter(q_hi_ha_docencia_abans | q_hi_ha_docencia_despres)
                                           .exists()
                                           )
    recursos_lliures = Recurs.objects.none()
    if hi_ha_classe_al_centre_aquella_hora:
        # reservables
        reservable_aquella_hora = (Q(disponibilitat_horaria__isnull=True)
                                   | Q(disponibilitat_horaria=franja))
        reservable_aquella_hora_ids = (Recurs
                                       .objects
                                       .filter(reservable_aquella_hora)
                                       .values_list('id', flat=True)
                                       .distinct()
                                       )
        # reservats
        reservat = Q(reservarecurs__dia_reserva__gte=data_inici) & \
                   Q(reservarecurs__dia_reserva__lte=data_fi) & \
                   Q(reservarecurs__dia_reserva__week_day=data_inici.weekday()+2) & \
                   Q(reservarecurs__hora=franja)
        reservat_ids = (Recurs
                         .objects
                         .filter(reservat)
                         .values_list('id', flat=True)
                         .distinct()
                         )
        # lliures
        recursos_lliures = (Recurs
                         .objects
                         .exclude(reservable=False)
                         .filter(pk__in=reservable_aquella_hora_ids)
                         .exclude(pk__in=reservat_ids)
                         .distinct()
                         )

    if request.method == 'POST':
        form = RecursosForm(queryset=recursos_lliures,
                         data=request.POST,
                         )

        if form.is_valid():
            next_url = r"/recursos/tramitarReservaMassivaRecurs/{0}/{1}/{2}/{3}/{4}/{5}/{6}/{7}/"
            return HttpResponseRedirect(next_url.format(form.cleaned_data['recurs'].pk, franja.pk, year_inici, year_fi,
                                                        month_inici, month_fi, day_inici, day_fi))

    else:
        form = RecursosForm(queryset=recursos_lliures)

    for f in form.fields:
        form.fields[f].widget.attrs['class'] = 'form-control ' + form.fields[f].widget.attrs.get('class', "")

    return render(
        request,
        'form.html',
        {'form': form,
         'titol_formulari': u"Assistent Reserva Massiva de Material (2/3)",
         },
    )


# -- wizard massiva per franja 3/3
@login_required
@group_required(['professors', 'professional', 'consergeria'])
def tramitarReservaMassivaRecurs(request, pk_recurs=None, pk_franja=None, year_inici=None, year_fi=None, month_inici=None,  month_fi=None, day_inici=None, day_fi=None):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    recurs = Recurs.objects.filter(pk=pk_recurs).first()
    franja = FranjaHoraria.objects.filter(pk=pk_franja).first()

    import datetime as t
    try:
        year_inici = int(year_inici)
        month_inici = int(month_inici)
        day_inici = int(day_inici)
        year_fi = int(year_fi)
        month_fi = int(month_fi)
        day_fi = int(day_fi)
    except:
        today = t.date.today()
        year_inici = today.year
        month_inici = today.month
        day_inici = today.day
        year_fi = today.year
        month_fi = today.month
        day_fi = today.day
    data_inici = t.date(year_inici, month_inici, day_inici)
    data_fi = t.date(year_fi, month_fi, day_fi)
    es_reservador = User.objects.filter(pk=user.pk, groups__name__in=['reservador']).exists()
    if not es_reservador:
        msg = u"No tens permís per reservar un bloc de dies"
        messages.warning(request, SafeText(msg))
        return HttpResponseRedirect(r'/recursos/lesMevesReservesDeRecurs/')

    novaReserva = ReservaRecurs(recurs=recurs,
                                hora=franja,
                                dia_reserva=data_inici,
                                usuari=user,
                                es_reserva_manual=True)
    infoForm = [
        ('Data inici reserva',data_inici),
        ('Data fi reserva', data_fi),
    ]

    if request.method == 'POST':
            novaReserva = ReservaRecurs(recurs=recurs,
                                        hora=franja,
                                        dia_reserva=data_inici,
                                        usuari=user,
                                        es_reserva_manual=False)
            form = reservaMassivaRecursForm(request.POST, instance=novaReserva)

            if form.is_valid():
                try:
                    reserva = form.save(commit=False)
                    dates = []
                    numdies = (data_fi - data_inici).days
                    for x in range(0, numdies + 1, 7):
                        dates.append(data_inici + timedelta(days=x))
                    for data in dates:
                        reserva.pk=None
                        reserva.dia_reserva = data
                        reserva.save()
                    missatge = u"Reserva realitzada correctament"
                    messages.success(request, missatge)
                    # missatge al professor:
                    dies_setmana={0:'dilluns', 1:'dimarts', 2:'dimecres', 3:'dijous', 4:'divendres'}
                    missatge = PROFESSOR_RESERVA_MASSIVA
                    txt = missatge.format(novaReserva.recurs, dies_setmana[data_inici.weekday()], data_inici, data_fi, novaReserva.hora)
                    tipus_de_missatge = tipusMissatge(missatge)
                    msg = Missatge(remitent=user, text_missatge=txt, tipus_de_missatge=tipus_de_missatge)
                    importancia = 'PI'
                    destinatari=reserva.usuari
                    msg.envia_a_usuari(destinatari, importancia)
                    return HttpResponseRedirect(r'/recursos/lesMevesReservesDeRecurs/')
                except ValidationError as e:
                    for _, v in e.message_dict.items():
                        form._errors.setdefault(NON_FIELD_ERRORS, []).extend(v)
    else:
        form = reservaMassivaRecursForm(instance=novaReserva)

    for f in ['recurs', 'dia_reserva', 'hora', 'motiu']:
        form.fields[f].widget.attrs['class'] = 'form-control ' + form.fields[f].widget.attrs.get('class', "")

    return render(
        request,
        'form.html',
        {'form': form,
         'infoForm': infoForm,
         'head': u'Reservar material',
         'titol_formulari': u"Assistent Reserva Massiva de Material (3/3)",
         },
    )
