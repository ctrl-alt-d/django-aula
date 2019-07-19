# -*- coding: utf-8 -*-
import os
import datetime
import json
from datetime import date
from django.contrib.auth.models import User
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseServerError
from typing import List
from django.core import serializers
from django.contrib.auth.models import User

from aula.apps.presencia.models import ControlAssistencia
from typing import Dict


def add_secs_to_time(timeval, secs_to_add):
    dummy_date = datetime.date(1, 1, 1)
    full_datetime = datetime.datetime.combine(dummy_date, timeval)
    added_datetime = full_datetime + datetime.timedelta(seconds=secs_to_add)
    return added_datetime.time()

def PresenciaQuerySetGetCode(qs):
    #type: (QuerySet)-> None ; QuerySet de tipus assistència
    '''
    Passar un conjunt d'assistencies, determina si en alguna hi ha un present o retard.
    Si és així, vol dir que tenim un assistència durant aquest període.
    '''
    assistenciaCode = 'N'
    if qs is not None and qs.filter( estat__isnull = False  ).exists():
        if qs.filter( estat__codi_estat__in = ['P','R'] ):
            assistenciaCode = 'P'
        elif qs.filter( estat__codi_estat__in = ['J'] ):
            assistenciaCode = 'J'
        else:
            assistenciaCode = 'F'
    return assistenciaCode

def PresenciaQuerySet( qs ):
    #type: (QuerySet); QuerySet de tipus assistència
    if qs is not None and qs.filter( estat__isnull = False  ).exists():
        if qs.filter( estat__codi_estat__in = ['P','R'] ):
            esFaltaAnterior = 'Present'
        else:
            esFaltaAnterior = 'Absent'
    else:
        esFaltaAnterior = 'NA'
    return esFaltaAnterior

def gen_password(length=50, charset="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"):
    random_bytes = os.urandom(length)
    len_charset = len(charset)
    indices = [int(len_charset * (ord(byte) / 256.0)) for byte in random_bytes]
    return "".join([charset[index] for index in indices])

def convertirData(stringData):
    "Passem una data en format Y-M-D, comprova si és correcte i retorna una llista amb 3 enters."
    camps = stringData.split('-')
    return date(int(camps[0]),int(camps[1]), int(camps[2]))

def obtenirUsuari(nomUsuari):
    try:
        return User.objects.get(username=nomUsuari) # type: Usuari
    except ObjectDoesNotExist as ex:
        return None

def tokenCorrecte(request, usuariTokens, pkUsuari):
    #type: (HttpRequest, List[TokenICaducitat], str) -> None
    if not pkUsuari in usuariTokens:
        return False
    if 'token' in request.COOKIES:
        tokenICaducitat = usuariTokens[pkUsuari] 
        if request.COOKIES.get('token') == tokenICaducitat.token \
            and datetime.datetime.now() < tokenICaducitat.caducitat: 
            return True
    return False

def deserialitzarUnElement(objecteSerialitzat):
    return serializers.deserialize('json', u'[' + objecteSerialitzat + u']').next()

def deserialitzarUnElementAPartirObjectePython(objectePythonSerialitzat):
    return serializers.deserialize('json', u'[' + 
        json.dumps(objectePythonSerialitzat, ensure_ascii=False).encode('utf-8') + u']').next()

def serialitzarUnElement(objecte):
    #type: (Object)->string
    return serializers.serialize('json', [objecte])[1:-1], 

def comprovarUsuariIPermisos(request, idUsuari, usuariTokens):
    #type: (HttpRequest, String, Dict[str])->HttpResponse
    usuari = obtenirUsuari(idUsuari) #type: str
    
    if not usuari:
        return False, HttpResponseNotFound('Usuari no localitzat')

    if not tokenCorrecte(request, usuariTokens, usuari.pk):
        return False, HttpResponseBadRequest("Token no trobat")
    return True, None

class TokenICaducitat:
    def __init__(self,token, caducitat):
        self.token = token
        self.caducitat = caducitat

class ControlAssistenciaIHoraAnterior(ControlAssistencia):
    #Model que incorpora l'estat de la hora anterior. 
    #Ens va bé perque així el programa client(Android?) coneix estat de l'hora anterior directament.
    class Meta:
        proxy = True
    def estatHoraAnterior(self):
        #     Comprova el codi de l'hora anterior, 2 Modes de retorn ('C', 'W'):
        #     Torna: Present, Absent o bé NA. (Mode paraula original='W')
        #     Torna: P o R -> P, F->F, J->J o N (Mode codi='C')
    
        unaHora40abans = add_secs_to_time(self.impartir.horari.hora.hora_inici, -100*60)
        controls_anteriors = ControlAssistencia.objects.filter(
            alumne = self.alumne,
            impartir__horari__hora__hora_inici__lt = self.impartir.horari.hora.hora_inici,
            impartir__horari__hora__hora_inici__gt = unaHora40abans,
            impartir__dia_impartir = self.impartir.dia_impartir  )

        if controls_anteriors:
            return controls_anteriors.all()[0].estat.codi_estat
        else:
            return None

    def nomAlumne(self):
        return self.alumne.nom

    def cognomsAlumne(self):
        return self.alumne.cognoms