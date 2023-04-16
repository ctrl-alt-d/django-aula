# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
from django.shortcuts import render

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from aula.mblapp.security_rest import EsUsuariDeLaAPI
import uuid
from rest_framework.parsers import JSONParser
from aula.apps.usuaris.models import QRPortal
from aula.mblapp.serializers import QRTokenSerializer, DarreraSincronitzacioSerializer
from django.contrib.auth.models import User, Group
from django.utils.crypto import get_random_string
from django.db import transaction
from rest_framework import serializers
from django.conf import settings
from django.utils.datetime_safe import datetime
from datetime import timedelta
from aula.apps.presencia.models import EstatControlAssistencia
from aula.apps.presencia.models import ControlAssistencia
from aula.apps.avaluacioQualitativa.models import AvaluacioQualitativa
from aula.apps.sortides.models import NotificaSortida
# ----------- vistes per a testos --------------------------------

@api_view(['GET'])
@permission_classes((AllowAny, ))
def hello_api(request, format=None):
    content = {
        'status': 'here we are'
    }
    return Response(content)

@api_view(['GET'])
@permission_classes((IsAuthenticated, ))
def hello_api_login(request, format=None):
    content = {
        'status': 'here we are just login'
    }
    return Response(content)


@api_view(['GET'])
@permission_classes((EsUsuariDeLaAPI,))
def hello_api_login_app(request, format=None):
    content = {
        'status': 'here we are login group app'
    }
    return Response(content)


# ---------------------  user x token ----------------------------
# La vista que genera el QR és a l'App portal famílies.

# ----------------------------------------------------------------

#@csrf_exempt
@transaction.atomic
@api_view(['POST'])
@permission_classes((AllowAny, ))
def capture_token_api(request, format=None):
    """
    Rep un token i retorna un usuari de la API (is_active=False)
    """

    # deserialitzem
    data = JSONParser().parse(request)
    serializer = QRTokenSerializer(data=data)
    if not serializer.is_valid():
        raise serializers.ValidationError("ups! Aquest token no serveix")
    # busquem el token
    key = serializer.validated_data["key"]
    born_date = serializer.validated_data["born_date"]
    token = (QRPortal
             .objects
             .filter( moment_captura__isnull = True, clau = key )
             .first()
            )

    if "validacions del token":

        # si no hi ha token -> error
        if not token:
            raise serializers.ValidationError("ups! Aquest token no serveix")

        # si el token ja ha estat previament capturat
        if token.moment_captura:
            raise serializers.ValidationError("ups! Aquest token no serveix")

        # caducat?
        caduca_dia = token.moment_expedicio + timedelta(days=settings.CUSTOM_DIES_API_TOKEN_VALID)
        if datetime.now() > caduca_dia:
            raise serializers.ValidationError("ups! Aquest token no serveix")
        # born date is ok?
        fuky_random_jesucryst_date = datetime(1000,1,1).date
        db_born_date = ( token.alumne_referenciat.data_neixement or fuky_random_jesucryst_date )
        if db_born_date != born_date:
            raise serializers.ValidationError("ups! Aquest token no serveix")

    # creo un nou usuari per aquest token
    allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789' +  '0Oo^?#!'
    password_xunga = User.objects.make_random_password(length=12, allowed_chars=allowed_chars)
    nou_usuari = User.objects.create_user( username = "API"+token.localitzador ,
                                           email = "",
                                           password = password_xunga )
    grup_api, _ = Group.objects.get_or_create(name='API')
    nou_usuari.groups.add(grup_api)
    nou_usuari.is_active = False             #serà actiu quan el tutor l'activi
    nou_usuari.save()

    # assigno usuari al token
    token.moment_captura = datetime.now()
    token.usuari_referenciat = nou_usuari
    token.save()

    # preparem resposta
    content = {
        'username': nou_usuari.username,
        'password': password_xunga,
    }

    return Response(content)


@api_view(['POST'])
@permission_classes((EsUsuariDeLaAPI,))
def notificacions_mes(request, mes, format=None):
    """
    Rep la darrera data de sincronització (i un jwt), el mes i retorna tots valors actuals.
    """
    ara = datetime.now()
    data = JSONParser().parse(request)
    serializer = DarreraSincronitzacioSerializer(data=data)
    if not serializer.is_valid():
        raise serializers.ValidationError("ups! petició amb errors")

    qrtoken = request.user.qrportal

    # Tant si hi ha novetats com si no s'envia tota la info del mes:

    alumne = qrtoken.alumne_referenciat
    content = [{
        "id": alumne.id,
        "darrera_sincronitzacio": qrtoken.darrera_sincronitzacio,
    }]

    presencies_notificar = EstatControlAssistencia.objects.filter(codi_estat__in=['F', 'R', 'J'])
    faltes_assistencia = (ControlAssistencia
                          .objects
                          .filter( alumne = alumne,  estat__in = presencies_notificar, impartir__dia_impartir__month=mes )
                          .select_related('impartir',  # dia
                                          'impartir__horari__assignatura',  # materia
                                          'impartir__horari__hora',  # franja
                                          'estat',  # tipus
                                          )
                          .order_by('-impartir__dia_impartir', '-impartir__horari__hora')
                          )

    content = content + [{"dia": "/".join([str(f.impartir.dia_impartir.day), str(f.impartir.dia_impartir.month),
                                           str(f.impartir.dia_impartir.year)]),
                          "materia": str(f.impartir.horari.assignatura),
                          "hora": str(f.impartir.horari.hora),
                          "professor": str(f.professor),
                          "text": "Falta d'assistència" if str(f.estat) == "Falta" else "Retard",
                          "tipus": str(f.estat)}
                         for f in faltes_assistencia]



    incidencies = (alumne
                   .incidencia_set
                   .filter(dia_incidencia__month=mes)
                   .select_related('tipus',  # tipus
                                   'franja_incidencia',  # franja
                                   )
                   .order_by('-dia_incidencia', '-franja_incidencia')
                   )

    # content["Incidències"] = [ {'dia': i.dia_incidencia,
    #                             'tipus': str(i.tipus),
    #                             'franja': str(i.franja_incidencia),
    #                             'motiu': i.descripcio_incidencia}
    #                             for i in incidencies  ]

    content = content + [{'dia': "/".join(
        [str(i.dia_incidencia.day), str(i.dia_incidencia.month), str(i.dia_incidencia.year)]),
                          'hora': str(i.franja_incidencia),
                          'professor': str(i.professional),
                          'text': i.descripcio_incidencia,
                          'tipus': str(i.tipus)}
                         for i in incidencies]


    # "Expulsions": [],
    expulsions = alumne.expulsio_set.filter(dia_expulsio__month=mes).exclude(estat='ES')
    content = content + [
        {'dia': "/".join([str(i.dia_expulsio.day), str(i.dia_expulsio.month), str(i.dia_expulsio.year)]),
         'hora': str(i.franja_expulsio),
         'professor': str(i.professor),
         'text': i.motiu,
         'tipus': "expulsió"}
        for i in expulsions]

    # "Sancions": [],
    sancions = alumne.sancio_set.filter(impres=True)
    #content["Sancions"] = [ ] #TODO

    # "Activitats": [],
    sortides = NotificaSortida.objects.filter(alumne=alumne)
    #content["sortides"] = [ ] #TODO

    # "Qualitatives": [],
    avui = datetime.now().date()
    qualitatives_en_curs = [q for q in AvaluacioQualitativa.objects.all()
                            if (bool(q.data_obrir_portal_families) and
                                bool(q.data_tancar_tancar_portal_families) and
                                q.data_obrir_portal_families <= avui <= q.data_tancar_tancar_portal_families
                                )
                            ]
    respostes_qualitativa = (alumne
                             .respostaavaluacioqualitativa_set
                             .filter(qualitativa__in=qualitatives_en_curs)
                             )
    #content["Qualitatives"] = [ ] #TODO

    # Anoto canvis
    qrtoken.darrera_sincronitzacio = ara

    qrtoken.save()

    return Response(content)




@api_view(['POST'])
@permission_classes(( EsUsuariDeLaAPI, ))
def notificacions_news(request, format=None):
    """
    Rep la darrera data de sincronització (i un jwt), i retorna si hi ha novetats o no
    """
    data = JSONParser().parse(request)
    serializer = DarreraSincronitzacioSerializer(data=data)
    if not serializer.is_valid():
        raise serializers.ValidationError("ups! petició amb errors")

    darrera_sincronitzacio = serializer.validated_data["last_sync_date"]

    qrtoken = request.user.qrportal

    # No hi ha novetats:

    content = {"resultat":"No"} if qrtoken.novetats_detectades_moment and qrtoken.novetats_detectades_moment < darrera_sincronitzacio else {"resultat":"Sí"}

    return Response(content)
