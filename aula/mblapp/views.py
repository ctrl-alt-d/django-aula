# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from aula.mblapp.security_rest import EsUsuariVinculatAEstudiant
import uuid

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

def genera_clau( ):
    clau = str( uuid.uuid4() )
    #google url = https://chart.googleapis.com/chart?cht=qr&chl=701fe92c-4676-4863-9dd5-6c64d019efc7&chs=300x300
    return clau