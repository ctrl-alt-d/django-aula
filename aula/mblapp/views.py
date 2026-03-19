# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import transaction
from rest_framework import request, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.parsers import JSONParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from aula.apps.alumnes.models import Alumne
from aula.apps.presencia.models import ControlAssistencia, EstatControlAssistencia
from aula.apps.relacioFamilies.business_rules import responsable
from aula.apps.sortides.models import (
    NotificaSortida,
    Pagament,
    Sortida,
    SortidaPagament,
)
from aula.apps.avaluacioQualitativa.models import AvaluacioQualitativa
from aula.mblapp.security_rest import EsUsuariDeLaAPI
from aula.mblapp.serializers import DarreraSincronitzacioSerializer
from aula.utils.tools import unicode
from aula.apps.usuaris.tools import getRol

from aula.apps.relacioFamilies.notifica import getNotifElements, setNotifElements, creaNotifUsuari

from aula.apps.usuaris.models import NotifUsuari
from datetime import date
# ----------- vistes per a testos --------------------------------


@api_view(["GET"])
@permission_classes((AllowAny,))
def hello_api(request, format=None):
    content = {"status": "here we are"}
    return Response(content)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def hello_api_login(request, format=None):
    content = {"status": "here we are just login"}
    return Response(content)


@api_view(["GET"])
@permission_classes((EsUsuariDeLaAPI,))
def hello_api_login_app(request, format=None, alumne_id=None):
    content = {"status": "here we are login group app"}
    return Response(content)


@api_view(["GET"])
@permission_classes((EsUsuariDeLaAPI,))
def notificacions_mes(request, mes, format=None, alumne_id=None):
    """
    Rep el mes i retorna tots valors actuals.
    """
    professor, responsable, alumne = getRol(request.user, request)
    alumne = Alumne.objects.get(id=alumne_id)

    # Si l'alumne és major d'edat, no notificar als responsables
    if responsable and alumne.data_neixement and alumne.edat() >= 18:
        raise serializers.ValidationError({"error": ["Accés denegat: l'alumne és major d'edat"]})

    if int(mes) < 1 or int(mes) > 12:
        raise serializers.ValidationError({"error": ["Mes inexistent"]})
    # Tant si hi ha novetats com si no s'envia tota la info del mes:

    content = [
        {
            "id": alumne.id,
        }
    ]

    presencies_notificar = EstatControlAssistencia.objects.filter(
        codi_estat__in=["F", "R", "J"]
    )
    faltes_assistencia = (
        ControlAssistencia.objects.filter(
            alumne=alumne,
            estat__in=presencies_notificar,
            impartir__dia_impartir__month=mes,
        )
        .select_related(
            "impartir",  # dia
            "impartir__horari__assignatura",  # materia
            "impartir__horari__hora",  # franja
            "estat",  # tipus
        )
        .order_by("-impartir__dia_impartir", "-impartir__horari__hora")
    )

    content = content + [
        {
            "dia": "/".join(
                [
                    str(f.impartir.dia_impartir.day),
                    str(f.impartir.dia_impartir.month),
                    str(f.impartir.dia_impartir.year),
                ]
            ),
            "materia": str(f.impartir.horari.assignatura),
            "hora": str(f.impartir.horari.hora),
            "professor": str(f.professor),
            "text": "Falta d'assistència" if str(f.estat) == "Falta" else "Retard",
            "tipus": str(f.estat),
        }
        for f in faltes_assistencia
    ]

    incidencies = (
        alumne.incidencia_set.filter(dia_incidencia__month=mes)
        .select_related(
            "tipus",  # tipus
            "franja_incidencia",  # franja
        )
        .order_by("-dia_incidencia", "-franja_incidencia")
    )

    content = content + [
        {
            "dia": "/".join(
                [
                    str(i.dia_incidencia.day),
                    str(i.dia_incidencia.month),
                    str(i.dia_incidencia.year),
                ]
            ),
            "hora": str(i.franja_incidencia),
            "professor": str(i.professional),
            "text": i.descripcio_incidencia,
            "tipus": str(i.tipus),
        }
        for i in incidencies
    ]

    # "Expulsions": [],
    expulsions = alumne.expulsio_set.filter(dia_expulsio__month=mes).exclude(estat="ES")
    content = content + [
        {
            "dia": "/".join(
                [
                    str(i.dia_expulsio.day),
                    str(i.dia_expulsio.month),
                    str(i.dia_expulsio.year),
                ]
            ),
            "hora": str(i.franja_expulsio),
            "professor": str(i.professor),
            "text": i.motiu,
            "tipus": "Expulsió",
        }
        for i in expulsions
    ]

    # "Sancions": [],
    sancions = alumne.sancio_set.filter(impres=True, data_carta__month=mes)
    content = content + [
        {
            "dia": "/".join(
                [str(i.data_carta.day), str(i.data_carta.month), str(i.data_carta.year)]
            ),
            "hora": str(i.franja_inici),
            "professor": str(i.professor),
            "text": "Del {0} al {1}. Motiu: {2}".format(
                str(datetime.strftime(i.data_inici, "%d/%m/%Y")),
                str(datetime.strftime(i.data_fi, "%d/%m/%Y")),
                str(i.motiu),
            ),
            "tipus": "Sanció",
        }
        for i in sancions
    ]

    # ToDo:
    # sortides = NotificaSortida.objects.filter(alumne=alumne)
    # content["sortides"] = [ ] #TODO

    # ToDo:
    # avui = datetime.now().date()
    # qualitatives_en_curs = [
    #     q
    #     for q in AvaluacioQualitativa.objects.all()
    #     if (
    #         bool(q.data_obrir_portal_families)
    #         and bool(q.data_tancar_tancar_portal_families)
    #         and q.data_obrir_portal_families
    #         <= avui
    #         <= q.data_tancar_tancar_portal_families
    #     )
    # ]
    #
    # respostes_qualitativa = alumne.respostaavaluacioqualitativa_set.filter(
    #    qualitativa__in=qualitatives_en_curs
    # )
    # content["Qualitatives"] = [ ]

    # Marcar com a notificades les novetats enviades
    notifAlumne = creaNotifUsuari(request.user, alumne, "N")
    setNotifElements(faltes_assistencia, notifAlumne)
    setNotifElements(incidencies, notifAlumne)
    setNotifElements(expulsions, notifAlumne)
    setNotifElements(sancions, notifAlumne)
    # TODO: afegir sortides i qualitatives 

    return Response(content)


@api_view(["GET"])
@permission_classes((EsUsuariDeLaAPI,))
def notificacions_news(request, format=None, alumne_id=None):
    
    professor, responsable, alumne = getRol(request.user, request)

    alumne = Alumne.objects.get(id=alumne_id)

    if responsable and alumne.data_neixement and alumne.edat() >= 18:
        raise serializers.ValidationError({"error": ["Accés denegat: alumne major d'edat"]})

    notificar_presencies = EstatControlAssistencia.objects.filter(
        codi_estat__in=["F", "R", "J"]
    )
    noves_faltes_assistencia = getNotifElements(
        ControlAssistencia.objects.filter(
            alumne=alumne, estat__in=notificar_presencies
        ),
        request.user,
        alumne,
    )
    noves_incidencies = getNotifElements(
        alumne.incidencia_set.all(), request.user, alumne
    )
    noves_expulsions = getNotifElements(
        alumne.expulsio_set.exclude(estat="ES"), request.user, alumne
    )
    noves_sancions = getNotifElements(
        alumne.sancio_set.filter(impres=True), request.user, alumne
    )

    noves_sortides = getNotifElements(
        NotificaSortida.objects.filter(alumne=alumne), request.user, alumne
    )

    hiHaNovetats = (
        noves_faltes_assistencia.exists()
        or noves_incidencies.exists()
        or noves_expulsions.exists()
        or noves_sancions.exists()
        or noves_sortides.exists()
    )

    content = {"resultat": "Sí" if hiHaNovetats else "No"}

    # Marcar com a notificades les novetats enviades
    notifAlumne = creaNotifUsuari(request.user, alumne, "N")
    setNotifElements(noves_faltes_assistencia, notifAlumne)
    setNotifElements(noves_incidencies, notifAlumne)
    setNotifElements(noves_expulsions, notifAlumne)
    setNotifElements(noves_sancions, notifAlumne)
    setNotifElements(noves_sortides, notifAlumne)

    return Response(content)


@api_view(["GET"])
@permission_classes((EsUsuariDeLaAPI,))
def alumnes_dades(request, format=None, alumne_id=None):
    professor, responsable, alumne = getRol(request.user, request)
    alumne = Alumne.objects.get(id=alumne_id)

    if responsable and alumne.data_neixement and alumne.edat() >= 18:
        raise serializers.ValidationError({"error": ["Accés denegat: alumne major d'edat"]})
    
    content = {
        "grup": unicode(alumne.grup),
        "datanaixement": "/".join(
            [
                unicode(alumne.data_neixement.day),
                unicode(alumne.data_neixement.month),
                unicode(alumne.data_neixement.year),
            ]
        ),
        "telefon": alumne.get_telefons(),
        "responsables": [
            {
                "nom": unicode(responsable.get_nom() if responsable else ""),
                "mail": unicode(responsable.get_correu_importat() if responsable else ""),
                "telefon": unicode(responsable.get_telefon() if responsable else ""),
            },
        ],
        "adreca": " , ".join(
            filter(
                None,
                [
                    unicode(alumne.adreca),
                    unicode(alumne.localitat),
                    unicode(alumne.municipi),
                ],
            )
        ),
    }
    return Response(content)


@api_view(["GET"])
@permission_classes((EsUsuariDeLaAPI,))
def sortides(request, alumne_id=None):
    """
    Retorna les activitats/pagaments de l'alumne
    """
    professor, responsable, alumne = getRol(request.user, request)
    alumne = Alumne.objects.get(id=alumne_id)

    # Si l'alumne és major d'edat, no mostrar als responsables
    if responsable and alumne.data_neixement and alumne.edat() >= 18:
        raise serializers.ValidationError({"error": ["Accés denegat: l'alumne és major d'edat"]})

    content = []

    sortides_on_no_assistira = alumne.sortides_on_ha_faltat.values_list(
        "id", flat=True
    ).distinct()
    sortides_justificades = alumne.sortides_falta_justificat.values_list(
        "id", flat=True
    ).distinct()
    # sortides a on s'ha convocat a l'alumne
    sortidesnotificat = (
        Sortida.objects.filter(notificasortida__alumne=alumne)
        .exclude(id__in=sortides_on_no_assistira)
        .exclude(id__in=sortides_justificades)
    )
    # sortides pagades a les que ja no s'ha convocat a l'alumne
    sortidespagadesperalumne = (
        SortidaPagament.objects.filter(alumne=alumne, pagament_realitzat=True)
        .values_list("sortida", flat=True)
        .distinct()
    )
    sortidespagadesnonotificades = (
        Sortida.objects.filter(
            id__in=sortidespagadesperalumne,
            pagaments__pagament__alumne=alumne,
            pagaments__pagament__pagament_realitzat=True,
        )
        .exclude(notificasortida__alumne=alumne)
        .exclude(id__in=sortides_on_no_assistira)
        .exclude(id__in=sortides_justificades)
    )
    # totes les sortides relacionades amb l'alumne
    activitats = sortidesnotificat.union(sortidespagadesnonotificades)
    # sortides que s'han de passar a l'app
    for sortida in activitats.order_by("-calendari_desde"):
        if sortida.tipus_de_pagament == "ON":
            try:
                pagament = Pagament.objects.get(sortida=sortida, alumne=alumne)
                realitzat = pagament.pagament_realitzat
            except Pagament.DoesNotExist:
                pagament = None
                realitzat = False
        else:
            pagament = None
            realitzat = False
        content = content + [
            {
                "id": sortida.id,
                "titol": str(sortida.titol),
                "data": str(sortida.calendari_desde),
                "pagament": bool(pagament),
                "realitzat": realitzat,
            }
        ]
    return Response(content)


@api_view(["GET"])
@permission_classes((EsUsuariDeLaAPI,))
def detallSortida(request, pk, alumne_id=None):
    """
    Rep el pk d'una activitat/pagament i retorna informació de l'activitat/pagament
    """
    professor, responsable, alumne = getRol(request.user, request)
    alumne = Alumne.objects.get(id=alumne_id)

    # Si l'alumne és major d'edat, no mostrar als responsables
    if responsable and alumne.data_neixement and alumne.edat() >= 18:
        raise serializers.ValidationError({"error": ["Accés denegat: l'alumne és major d'edat"]})

    try:
        int(pk)
        sortida = Sortida.objects.get(pk=pk)
    except:  # noqa: E722
        raise serializers.ValidationError({"error": ["Sortida inexistent"]})

    try:
        pagament = Pagament.objects.get(sortida=sortida, alumne=alumne)
        realitzat = pagament.pagament_realitzat
    except Pagament.DoesNotExist:
        pagament = None
        realitzat = False

    content = {
        "titol": str(sortida.titol),
        "desde": sortida.calendari_desde.strftime("%d/%m/%Y %H:%M"),
        "finsa": sortida.calendari_finsa.strftime("%d/%m/%Y %H:%M"),
        "programa": "\n".join(
            [
                sortida.programa_de_la_sortida,
                sortida.condicions_generals,
                sortida.informacio_pagament,
            ]
        ),
        "preu": str(sortida.preu_per_alumne) if sortida.preu_per_alumne else "0",
        "dataLimitPagament": (
            str(sortida.termini_pagament) if sortida.termini_pagament else ""
        ),
        "realitzat": realitzat,
        "idPagament": pagament.id if pagament else None,
    }
    return Response(content)


@api_view(["GET"])
@permission_classes((IsAuthenticated,))
def alumnes_associats(request):
    professor, responsable, alumne = getRol(request.user, request)
    associats = responsable.get_alumnes_associats()
    content = []

    for associat in associats:
        # Excloure alumnat major d'edat
        if associat.data_neixement and associat.edat() >= 18:
            continue
        content = content + [
            {
                "nom": associat.nom,
                "cognoms": associat.cognoms,
                "id": associat.id,
            }
        ]
    return Response(content)