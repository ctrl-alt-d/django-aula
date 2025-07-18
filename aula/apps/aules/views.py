# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

# workflow
import os
from datetime import datetime, timedelta

from django.contrib import messages

# auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.exceptions import NON_FIELD_ERRORS, ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

# tables
from django.utils.safestring import SafeText
from django_tables2 import RequestConfig

from aula import settings

# forms
from aula.apps.aules.forms import (
    AulesForm,
    carregaComentarisAulaForm,
    disponibilitatAulaPerAulaForm,
    disponibilitatAulaPerFranjaForm,
    reservaAulaForm,
)

# models
from aula.apps.aules.models import Aula, ReservaAula
from aula.apps.aules.tables2_models import HorariAulaTable, Table2_ReservaAula
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.presencia.models import Impartir

# helpers
from aula.apps.usuaris.models import User2Professor
from aula.utils import tools
from aula.utils.decorators import group_required
from aula.utils.my_paginator import DiggPaginator
from aula.utils.tools import unicode


@login_required
@group_required(["professors", "professional", "consergeria"])
def reservaAulaList(request):
    (user, l4) = tools.getImpersonateUser(request)
    User2Professor(user)

    reserves = ReservaAula.objects.filter(es_reserva_manual=True).filter(usuari=user)

    table = Table2_ReservaAula(reserves)
    table.order_by = [
        "-dia_reserva",
    ]

    RequestConfig(
        request, paginate={"paginator_class": DiggPaginator, "per_page": 30}
    ).configure(table)

    return render(
        request,
        "reservesAules.html",
        {
            "table": table,
        },
    )


# -- wizard per aula 1/3
@login_required
@group_required(["professors", "professional", "consergeria"])
def consultaAulaPerAula(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    if request.method == "POST":
        formDisponibilitatAula = disponibilitatAulaPerAulaForm(request.POST)

        if formDisponibilitatAula.is_valid():
            aula = formDisponibilitatAula.cleaned_data["aula"]
            data = formDisponibilitatAula.cleaned_data["data"]
            year = data.year
            month = data.month
            date = data.day
            next_url = r"/aules/detallAulaReserves/{0}/{1}/{2}/{3}"
            return HttpResponseRedirect(next_url.format(year, month, date, aula.pk))

    else:
        formDisponibilitatAula = disponibilitatAulaPerAulaForm()

    return render(
        request,
        "form.html",
        {
            "form": formDisponibilitatAula,
            "head": "Consultar disponibilitat aula",
            "titol_formulari": "Assistent Reserva d'Aula (1/3)",
        },
    )


# -- wizard per aula 2/3
@login_required
@group_required(["professors", "professional", "consergeria"])
def detallAulaReserves(request, year, month, day, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    aula = get_object_or_404(Aula, pk=pk)

    #
    import datetime as t

    try:
        year = int(year)
        month = int(month)
        day = int(day)
    except:  # noqa: E722
        today = t.date.today()
        year = today.year
        month = today.month
        day = today.day

    data = t.date(year, month, day)
    tretze_dies = timedelta(days=13)
    darrer_dia_reserva = (
        datetime.today().date()
        + tretze_dies
        - timedelta(days=datetime.today().weekday())
    )
    es_reservador = User.objects.filter(
        pk=user.pk, groups__name__in=["reservador"]
    ).exists()
    if not es_reservador and (
        data > darrer_dia_reserva or data < datetime.today().date()
    ):
        msg = "Aquesta data no permet fer reserves. Només es pot des d'avui i fins al dia {0}".format(
            darrer_dia_reserva
        )
        messages.warning(request, SafeText(msg))
    #
    reserves_dun_dia_un_aula = ReservaAula.objects.filter(aula=aula).filter(
        dia_reserva=data
    )

    #
    franges_del_dia = (
        FranjaHoraria.objects.filter(horari__impartir__dia_impartir=data)
        .order_by("hora_inici")
        .distinct()
    )

    # -- si l'aula presenta un horari restringit
    q_horari_restringit = Q()
    disponibilitatHoraria = [franja.pk for franja in aula.disponibilitat_horaria.all()]
    if bool(disponibilitatHoraria):
        franges_reservades = [reserva.hora.pk for reserva in reserves_dun_dia_un_aula]
        q_horari_restringit = Q(pk__in=disponibilitatHoraria + franges_reservades)

    # Només les franges que corresponen al dia
    franges_reservables = (
        (franges_del_dia.filter(q_horari_restringit)) if franges_del_dia else []
    )

    horariAula = []
    for franja in franges_reservables:
        # Si la franja es solapa amb una altra ja ocupada, no es mostrarà
        if not reserves_dun_dia_un_aula.filter(
            hora__hora_inici=franja.hora_inici, hora__hora_fi=franja.hora_fi
        ) and reserves_dun_dia_un_aula.filter(
            hora__hora_inici__lt=franja.hora_fi, hora__hora_fi__gt=franja.hora_inici
        ):
            continue

        reserva = reserves_dun_dia_un_aula.filter(hora=franja).order_by().first()
        nova_franja = {}
        nova_franja["franja"] = franja
        nova_franja["reserva"] = reserva
        assignatures_list = (
            (
                reserva.impartir_set.filter(
                    horari__assignatura__nom_assignatura__isnull=False
                )
                .values_list("horari__assignatura__nom_assignatura", flat=True)
                .distinct()
            )
            if reserva
            else []
        )
        nova_franja["assignatura"] = ", ".join(assignatures_list) if reserva else ""
        grup_list = (
            (
                reserva.impartir_set.filter(horari__grup__descripcio_grup__isnull=False)
                .values_list("horari__grup__descripcio_grup", flat=True)
                .distinct()
            )
            if reserva
            else []
        )
        nova_franja["grup"] = ", ".join(grup_list) if reserva else ""
        nova_franja["professor"] = (
            ", ".join([reserva.usuari.first_name + " " + reserva.usuari.last_name])
            if reserva
            else ""
        )
        nova_franja["reservable"] = not bool(reserva) and aula.reservable
        nova_franja["eliminable"] = (
            bool(reserva)
            and reserva.usuari.pk == user.pk
            and not reserva.impartir_set.exists()
        )
        nova_franja["aula"] = aula
        nova_franja["dia"] = data
        horariAula.append(nova_franja)

    table = HorariAulaTable(horariAula)
    table.order_by = "franja"
    RequestConfig(request).configure(table)

    return render(
        request,
        "mostraInfoReservaAula.html",
        {
            "table": table,
            "aula": aula,
            "dia": data,
            "titol_formulari": "Assistent Reserva d'Aula (2/3)",
        },
    )


# -- wizard per franja 1/3
@login_required
@group_required(["professors", "professional", "consergeria"])
def consultaAulaPerFranja(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    if request.method == "POST":
        formDisponibilitatAula = disponibilitatAulaPerFranjaForm(
            request.POST, user=request.user
        )

        if formDisponibilitatAula.is_valid():
            franja = formDisponibilitatAula.cleaned_data["franja"]
            data = formDisponibilitatAula.cleaned_data["data"]
            year = data.year
            month = data.month
            date = data.day
            next_url = r"/aules/detallFranjaReserves/{0}/{1}/{2}/{3}"
            return HttpResponseRedirect(next_url.format(year, month, date, franja.pk))

    else:
        formDisponibilitatAula = disponibilitatAulaPerFranjaForm(user=request.user)

    for f in formDisponibilitatAula.fields:
        formDisponibilitatAula.fields[f].widget.attrs["class"] = (
            "form-control "
            + formDisponibilitatAula.fields[f].widget.attrs.get("class", "")
        )

    return render(
        request,
        "form.html",
        {
            "form": formDisponibilitatAula,
            "head": "Consultar disponibilitat aula per franja",
            "titol_formulari": "Assistent Reserva d'Aula (1/3)",
        },
    )


# -- wizard per franja 2/3
@login_required
@group_required(["professors", "professional", "consergeria"])
def detallFranjaReserves(request, year, month, day, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    franja = get_object_or_404(FranjaHoraria, pk=pk)

    #
    import datetime as t

    try:
        year = int(year)
        month = int(month)
        day = int(day)
    except:  # noqa: E722
        today = t.date.today()
        year = today.year
        month = today.month
        day = today.day

    data = t.date(year, month, day)

    tretze_dies = timedelta(days=13)
    darrer_dia_reserva = (
        datetime.today().date()
        + tretze_dies
        - timedelta(days=datetime.today().weekday())
    )
    es_reservador = User.objects.filter(
        pk=user.pk, groups__name__in=["reservador"]
    ).exists()
    if not es_reservador and (
        data > darrer_dia_reserva or data < datetime.today().date()
    ):
        msg = "Aquesta data no permet fer reserves. Només es pot des d'avui i fins al dia {0}".format(
            darrer_dia_reserva
        )
        messages.warning(request, SafeText(msg))

    q_hi_ha_docencia_abans = Q(horari__hora__hora_inici__lte=franja.hora_inici)
    q_hi_ha_docencia_despres = Q(horari__hora__hora_fi__gte=franja.hora_fi)
    hi_ha_classe_al_centre_aquella_hora = (
        Impartir.objects.filter(dia_impartir=data)
        .filter(q_hi_ha_docencia_abans | q_hi_ha_docencia_despres)
        .exists()
    )
    aules_lliures = Aula.objects.none()
    if hi_ha_classe_al_centre_aquella_hora:
        # reservables
        reservable_aquella_hora = Q(disponibilitat_horaria__isnull=True) | Q(
            disponibilitat_horaria=franja
        )
        reservable_aquella_hora_ids = (
            Aula.objects.filter(reservable_aquella_hora)
            .values_list("id", flat=True)
            .distinct()
        )
        # reservades
        # Aules ocupades en el dia i franja, també casos de franges solapades
        reservada = (
            Q(reservaaula__dia_reserva=data)
            & Q(reservaaula__hora__hora_inici__lt=franja.hora_fi)
            & Q(reservaaula__hora__hora_fi__gt=franja.hora_inici)
        )
        reservada_ids = (
            Aula.objects.filter(reservada).values_list("id", flat=True).distinct()
        )
        # lliures
        aules_lliures = (
            Aula.objects.exclude(reservable=False)
            .filter(pk__in=reservable_aquella_hora_ids)
            .exclude(pk__in=reservada_ids)
            .distinct()
        )

    if request.method == "POST":
        form = AulesForm(
            queryset=aules_lliures,
            data=request.POST,
        )

        if form.is_valid():
            next_url = r"/aules/tramitarReservaAula/{0}/{1}/{2}/{3}/{4}/"
            return HttpResponseRedirect(
                next_url.format(
                    form.cleaned_data["aula"].pk, franja.pk, year, month, day
                )
            )

    else:
        form = AulesForm(queryset=aules_lliures)

    for f in form.fields:
        form.fields[f].widget.attrs["class"] = "form-control " + form.fields[
            f
        ].widget.attrs.get("class", "")

    return render(
        request,
        "form.html",
        {
            "form": form,
            "titol_formulari": "Assistent Reserva d'Aula (2/3)",
        },
    )


# -- wizard per aula ó franja 3/3
@login_required
@group_required(["professors", "professional", "consergeria"])
def tramitarReservaAula(
    request, pk_aula=None, pk_franja=None, year=None, month=None, day=None
):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    aula = Aula.objects.filter(pk=pk_aula).first()
    franja = FranjaHoraria.objects.filter(pk=pk_franja).first()

    #
    import datetime as t

    try:
        year = int(year)
        month = int(month)
        day = int(day)
    except:  # noqa: E722
        today = t.date.today()
        year = today.year
        month = today.month
        day = today.day
    data = t.date(year, month, day)
    tretze_dies = timedelta(days=13)
    darrer_dia_reserva = (
        datetime.today().date()
        + tretze_dies
        - timedelta(days=datetime.today().weekday())
    )
    es_reservador = User.objects.filter(
        pk=user.pk, groups__name__in=["reservador"]
    ).exists()
    if not es_reservador and (
        data > darrer_dia_reserva or data < datetime.today().date()
    ):
        msg = "Reserva NO realitzada. Només es pot des d'avui i fins al dia {0}".format(
            darrer_dia_reserva
        )
        messages.warning(request, SafeText(msg))
        return HttpResponseRedirect(r"/aules/lesMevesReservesDAula/")
    #
    novaReserva = ReservaAula(
        aula=aula, hora=franja, dia_reserva=data, usuari=user, es_reserva_manual=True
    )
    #
    if request.method == "POST":
        form = reservaAulaForm(request.POST, instance=novaReserva)
        if form.is_valid():
            try:
                es_canvi_aula = form.cleaned_data["mou_alumnes"] == "C"
                if es_canvi_aula:
                    reserva = form.save(commit=False)
                    q_es_meva = Q(horari__professor__pk=user.pk) | Q(
                        professor_guardia__pk=user.pk
                    )
                    q_mateix_dia_i_hora = Q(dia_impartir=reserva.dia_reserva) & Q(
                        horari__hora=reserva.hora
                    )
                    q_te_reserva = Q(reserva__isnull=False)
                    impartir = Impartir.objects.filter(
                        q_es_meva & q_mateix_dia_i_hora & q_te_reserva
                    ).first()
                    if bool(impartir):
                        # canvio d'aula l'antiga reserva
                        impartir.reserva.aula = reserva.aula
                        impartir.reserva.motiu = reserva.motiu
                        impartir.reserva.es_reserva_manual = True
                        impartir.reserva.save()
                        missatge = "Canvi d'aula realitzat correctament"
                        messages.success(request, missatge)
                    else:
                        # creo la nova reserva
                        reserva.save()
                        missatge = "No s'ha trobat docència a aquella hora, però la reserva queda feta."
                        messages.success(request, missatge)
                else:
                    reserva = form.save()
                    missatge = "Reserva realitzada correctament"
                    messages.success(request, missatge)
                return HttpResponseRedirect(r"/aules/lesMevesReservesDAula/")

            except ValidationError as e:
                for _, v in e.message_dict.items():
                    form._errors.setdefault(NON_FIELD_ERRORS, []).extend(v)

    else:
        form = reservaAulaForm(instance=novaReserva)

    #
    for f in ["aula", "dia_reserva", "hora", "motiu"]:
        form.fields[f].widget.attrs["class"] = "form-control " + form.fields[
            f
        ].widget.attrs.get("class", "")

    #
    return render(
        request,
        "form.html",
        {
            "form": form,
            "head": "Reservar aula",
            "titol_formulari": "Assistent Reserva d'Aula (3/3)",
        },
    )


# -------------------------------------------------------------------------


@login_required
@group_required(["professors", "professional", "consergeria"])
def eliminarReservaAula(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials
    reserva = get_object_or_404(ReservaAula, pk=pk)
    reserva.credentials = credentials

    try:
        reserva.delete()
        missatge = "Reserva anul·lada correctament"
        messages.info(request, missatge)
    except ValidationError as e:
        for _, llista_errors in e.message_dict.items():
            missatge = "No s'ha pogut anul·lar la reserva: {0}".format(
                ", ".join(x for x in llista_errors)
            )
        messages.error(request, missatge)

    # tornem a la mateixa pantalla on erem (en mode incògnit no funciona)
    return HttpResponseRedirect(
        request.META.get("HTTP_REFERER", "/aules/lesMevesReservesDAula/")
    )


@login_required
@group_required(["direcció"])
def assignaComentarisAAules(request):
    (user, l4) = tools.getImpersonateUser(request)
    User2Professor(user)

    errors = []
    warnings = []
    infos = []

    if request.method == "POST":
        form = carregaComentarisAulaForm(request.POST, request.FILES)

        if form.is_valid():
            info_nAulesLlegides = 0
            info_nAulesCreades = 0
            info_nComentarisAfegits = 0
            AulesCreades = []
            ComentarisAfegits = []

            f = request.FILES["fitxerComentaris"]
            path = default_storage.save(
                "tmp/comentarisaules.txt", ContentFile(f.read())
            )
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            with open(tmp_file, "r", encoding="latin-1") as f1:
                reader = csv.DictReader(f1)
                f.seek(0)
                for row in reader:
                    info_nAulesLlegides += 1
                    nom_aula = unicode(row["CODI"], "iso-8859-1")
                    descripcio_aula = unicode(row["NOM"], "iso-8859-1")
                    if nom_aula != "":
                        a, created = Aula.objects.get_or_create(
                            nom_aula=nom_aula,
                            defaults={"horari_lliure": False, "reservable": True},
                        )
                        if created:
                            info_nAulesCreades += 1
                            AulesCreades.append(a.nom_aula)
                            warnings.append("{0}: Aula creada nova".format(a.nom_aula))
                        a.descripcio_aula = descripcio_aula
                        info_nComentarisAfegits += 1
                        ComentarisAfegits.append(descripcio_aula)
                        a.save()
                    else:
                        errors.append("S'han trobat aules sense nom!!!")
            default_storage.delete(path)
            warnings.append("Total aules noves creades: {0}".format(info_nAulesCreades))
            infos.append(
                "Total comentaris afegits: {0}".format(info_nComentarisAfegits)
            )
            resultat = {"errors": errors, "warnings": warnings, "infos": infos}
            return render(
                request,
                "resultat.html",
                {"head": "Resultat càrrega comentaris aules", "msgs": resultat},
            )
    else:
        form = carregaComentarisAulaForm()

    return render(
        request,
        "afegirComentarisAAules.html",
        {"form": form},
    )
