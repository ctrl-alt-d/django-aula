# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from aula.mblapp.security_rest import EsUsuariVinculatAEstudiant
import uuid
from rest_framework.parsers import JSONParser
from aula.apps.usuaris.models import QRPortal

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
@permission_classes((EsUsuariVinculatAEstudiant,))
def hello_api_login_app(request, format=None):
    content = {
        'status': 'here we are login group app'
    }
    return Response(content)


# ---------------------  user x token ----------------------------


from rest_framework import serializers

class QRTokenSerializer(serializers.Serializer):
    clau = serializers.CharField(max_length=40)
    numero_de_mobil = serializers.CharField(max_length=40)

    def validate_clau(self, value):
        """
        Validacions del token.
        """
        if len(value)<5:
            raise serializers.ValidationError("Aquest token és raro")

        token = QRPortal.objects.filter( moment_captura__isnull = True,
                                         clau = value ).first()
        if not token:
            raise serializers.ValidationError("Aquest token no serveix")

        return value

#@csrf_exempt
@api_view(['POST'])
@permission_classes((AllowAny, ))
def get_user_from_token_api(request, format=None):
    data = JSONParser().parse(request)
    serializer = QRTokenSerializer(data=data)
    if not serializer.is_valid():
        raise serializers.ValidationError("ups! Aquest token no serveix")

    # creo un nou usuari per aquest token
    password_xunga = "password_xunga" TODO
    nou_usuari = TODO

    # assigno usuari al token
    clau = serializer.validated_data["clau"]
    token = QRPortal.objects.filter( moment_captura__isnull = True,
                                        clau = clau ).first()
    token.numero_de_mobil = serializer.validated_data["numero_de_mobil"]

    token.moment_captura = ara TODO
    token.usuari_referenciat = nou_usuari TODO
    token.save()

    content = {
        'usuari': nou_usuari.username,
        'password': password_xunga,
    }

    return Response(content)
