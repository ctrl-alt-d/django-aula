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
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.conf import settings

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

def convertirData(stringData):
    "Passem una data en format Y-M-D, comprova si és correcte i retorna una llista amb 3 enters."
    camps = stringData.split('-')
    return date(int(camps[0]),int(camps[1]), int(camps[2]))

def obtenirUsuari(nomUsuari):
    try:
        return User.objects.get(username=nomUsuari) # type: Usuari
    except ObjectDoesNotExist as ex:
        return None

def comprovarUsuarisIguals(usuariSistema, usuari):
    if (not settings.CUSTOM_PRESENCIA_REST_VIEW_DESACTIVA_AUTH_TOKEN):
        if usuariSistema != usuari:
            raise Exception("Usuari que fa la petició, no coincideix amb el del token.")

class ControlAssistenciaIHoraAnterior(ControlAssistencia):
    #Model que incorpora l'estat de la hora anterior. 
    #Ens va bé perque així el programa client(Android?) coneix estat de l'hora anterior directament.
    
    class Meta:
        proxy = True
        #El test falla si no faig això.
        #https://stackoverflow.com/questions/30267237/invalidbaseserror-cannot-resolve-bases-for-modelstate-users-groupproxy
        auto_created = True
        
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