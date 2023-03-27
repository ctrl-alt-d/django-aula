# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
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
import datetime
from django.db import transaction
from rest_framework import serializers
from django.conf import settings
import datetime

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

#@csrf_exempt
@transaction.atomic
@api_view(['POST'])
@permission_classes((AllowAny, ))
def capture_token_api(request, format=None):
    """
    Rep un token i retorna un usuari de la API (is_active=False)
    """

    # deserialitzem    data = JSONParser().parse(request)
    serializer = QRTokenSerializer(data=data)
    if not serializer.is_valid():
        raise serializers.ValidationError("ups! Aquest token no serveix")
    # busquem el token
    clau = serializer.validated_data["clau"]
    token = ( QRPortal
             .objects
             .filter( moment_captura__isnull = True, clau = clau )
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
        caduca_dia = token.moment_expedicio + datetime.timedelta(days = settings.CUSTOM_DIES_API_TOKEN_VALID )
        if datetime.datetime.now() > caduca_dia:
            raise serializers.ValidationError("ups! Aquest token no serveix")

    # creo un nou usuari per aquest token
    allowed_chars='abcdefghjkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789' +  '0Oo^?#!'
    password_xunga = User.objects.make_random_password(length=12, allowed_chars=allowed_chars)
    nou_usuari = User.objects.create_user( username = token.localitzador ,
                                           email = "",
                                           password = password_xunga )
    grup_api, _ = Group.objects.get_or_create(name='API')
    nou_usuari.groups.add(grup_api)
    nou_usuari.is_active = False             #serà actiu quan el tutor l'activi
    nou_usuari.save()

    # assigno usuari al token
    token.moment_captura = datetime.datetime.now()
    token.usuari_referenciat = nou_usuari
    token.save()

    # preparem resposta
    content = {
        'usuari': nou_usuari.username,
        'password': password_xunga,
    }

    return Response(content)


@api_view(['POST'])
@permission_classes((EsUsuariDeLaAPI,))
def syncro_data_api(request, format=None):
    """
    Rep la darrera data de sincronització (i un jwt) i retorna tots valors actuals.
    """
    data = JSONParser().parse(request)
    serializer = DarreraSincronitzacioSerializer(data=data)
    if not serializer.is_valid():
        raise serializers.ValidationError("ups! petició amb errors")

    darrera_sincronitzacio = serializer.validated_data["darrera_sincronitzacio"]

    qrtoken = request.user.qrportal_set.get(es_el_token_actiu=True)

    # No hi ha novetats:
    if qrtoken.novetats_detectades_moment and qrtoken.novetats_detectades_moment < darrera_sincronitzacio:
        content = {"status": "All is up-to-date"}
        return Response(content)

    # Sí hi ha novetats, envio tot:
    qrtoken.darrera_sincronitzacio = datetime.datetime.now()
    content = {
        "darrera_sincronitzacio": qrtoken.darrera_sincronitzacio,
        "Assistència": [{"dia": "2018-06-01", "materia": "MA", "franja": "12:00-13:05", "tipus": "Retard"},
                        {"dia": "2018-06-02", "materia": "FI", "franja": "10:00-11:05", "tipus": "Justificada"},
                        ],

        "Incidències": [
            {"dia": "2018-06-01", "tipus": "Incidència", "franja": "12:00-13:05", "motiu": "Molesta els companys"},
            {"dia": "2018-06-02", "tipus": "Observació", "franja": "12:00-13:05", "motiu": "Bona feina"},
            ],
        "Expulsions": [],
        "Sancions": [],
        "Activitats": [],
    }

    # Anoto canvis
    qrtoken.save()

    return Response(content)

