# -*- coding: utf-8 -*-
import traceback
import json
import datetime

from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, HttpResponseServerError
from django.conf import settings

from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from aula.apps.usuaris.models import Professor, User2Professor, Accio
from aula.apps.presencia.models import Impartir, ControlAssistencia, EstatControlAssistencia
from aula.apps.horaris.models import FranjaHoraria, Horari
from aula.apps.presencia.business_rules.impartir import impartir_despres_de_passar_llista

from . import serializers as mySerializers
from . import utils

#Versió de la API, per tal que el client Android la comprovi i 
#Sàpiga si és compatible.
API_LEVEL = "2"

class APIViewAutenticadaAmbToken(APIView):
    #Activar això per tal de protegir la API.
    if settings.CUSTOM_PRESENCIA_REST_VIEW_DESACTIVA_AUTH_TOKEN:
        pass
    else:
        authentication_classes = [authentication.TokenAuthentication]
        permission_classes = [IsAuthenticated]

class Ajuda(APIViewAutenticadaAmbToken):
    
    def get(self, request, format=None):
        return HttpResponse("API DjAu per passar llista")

class PutGuardia(APIViewAutenticadaAmbToken):

    def put(self, request):
        try:
            dadesJSON = json.loads(request.body) #type: Dict
            usuariASubstituir = utils.obtenirUsuari(dadesJSON['idUsuariASubstituir'])
            usuari = utils.obtenirUsuari(dadesJSON['idUsuari'])
            idFranja = dadesJSON['idFranja']
            professor_guardia = User2Professor( usuari )
            professor = User2Professor( usuariASubstituir )
            dataAImpartir = datetime.datetime.strptime(dadesJSON['diaAImpartir'], "%Y-%m-%d")
            
            franja = FranjaHoraria.objects.get(pk=idFranja)
            dadesAModificar = Impartir.objects.filter( dia_impartir = dataAImpartir,
                                        horari__professor = professor,
                                        horari__hora__in = [franja]) #type: QuerySet

            if len(dadesAModificar)==0:
                return Response("Error, no existeix aquesta guàrdia", 
                    status.HTTP_500_INTERNAL_SERVER_ERROR)

            if dadesAModificar[0].horari.assignatura.tipus_assignatura in (settings.CUSTOM_PRESENCIA_REST_VIEW_TIPUS_ASSIGNATURES_PROHIBIDES):
                return Response(u"No pots actualitzar assignatures de tipus: " + unicode(settings.CUSTOM_PRESENCIA_REST_VIEW_TIPUS_ASSIGNATURES_PROHIBIDES))

            dadesAModificar.update( professor_guardia = professor_guardia  )
            return Response("ok")

        except Exception as excpt:
            traceback.print_exc()
            return Response('Error API' + str(excpt), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetImpartirPerData(APIViewAutenticadaAmbToken):

    def get(self, request, paramData, idUsuari):
        #type: (HttpRequest, str, str) -> HttpResponse
        #Retorna tots els registres del model Impartir donada una data.
        #El format d'ingŕes de la data és Y-M-D
        
        try:
            data = utils.convertirData(paramData)
            usuari = utils.obtenirUsuari(idUsuari)
            if not usuari:
                return Response('Usuari no localitzat', status=status.HTTP_404_NOT_FOUND)
            utils.comprovarUsuarisIguals(request.user, usuari)

            idProfe = usuari.pk
            #Sempre obtinc les classes a impartir dels profes que fan classe i els de guàrdia.
            classesAImpartirDelDia = Impartir.objects.filter(
                Q(horari__professor__id = idProfe, dia_impartir=data) |
                Q(professor_guardia_id = idProfe, dia_impartir=data)).order_by('horari__hora')
            serializer = mySerializers.ImpartirSerializer(classesAImpartirDelDia, many=True)
            return Response(serializer.data)
        except Exception as ex:
            traceback.print_exc()
            return Response('Error API' + ex, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetControlAssistencia(APIViewAutenticadaAmbToken):
    
    def get(self, request, idImpartir, idUsuari):
        #
        #Retorna una llista d'objectes JSON
        #Cada objecte conté tres valors ca (controlAssistencia), alumne(Alumne) i estat(Codi estat hora anterior).
        #
        try:
            usuari = utils.obtenirUsuari(idUsuari)
            if not usuari:
                return Response('Usuari no localitzat', status=status.HTTP_404_NOT_FOUND)
            utils.comprovarUsuarisIguals(request.user, usuari)
            cas = utils.ControlAssistenciaIHoraAnterior.objects.filter(
                impartir__id=idImpartir).order_by('alumne__cognoms')
            serializer = mySerializers.ControlAssistenciaIHoraAnteriorSerializer(cas, many=True)            
            return Response(serializer.data)
        except Exception as excpt:
            traceback.print_exc()
            return Response('Error API' + str(excpt), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PutControlAssistencia(APIViewAutenticadaAmbToken):

    def put(self, request, idImpartir, idUsuari):
        #Passa llista per una hora en concret.
        #Li passem l'id a impartir i un conjunt de claus de CA amb el seu estat.
        try:
            usuari = utils.obtenirUsuari(idUsuari)
            if not usuari: 
                return Response('Usuari no localitzat', status=status.HTTP_404_NOT_FOUND)
            utils.comprovarUsuarisIguals(request.user, usuari)

            impartir = Impartir.objects.get(pk=idImpartir)
            pertany_al_professor = usuari.pk in [impartir.horari.professor.pk, \
                                        impartir.professor_guardia.pk if impartir.professor_guardia else -1]
            if not (pertany_al_professor):
                return Response('No tens permisos per passar llista', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
            #Comprovar que no sigui una assignatura prohibida de passar a través de WebService, cas per exemple que calgui marcar UF's. Com a Montilivi.
            if impartir.horari.assignatura.tipus_assignatura in (settings.CUSTOM_PRESENCIA_REST_VIEW_TIPUS_ASSIGNATURES_PROHIBIDES):
                return Response("No pots actualitzar assignatures de tipus: " + unicode(settings.CUSTOM_PRESENCIA_REST_VIEW_TIPUS_ASSIGNATURES_PROHIBIDES), 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            #Retorna una llista de controls d'assistència.
            controlsAssistencia = json.loads(request.body) #type: Dict
        
            #Modifica només en cas que hi hagi elements a modificar.
            if len(controlsAssistencia) == 0:
                return Response("No hi han dades a actualitzar", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            #Modifica tots els controls d'assistència.
            #Només modifiquem l'estat de cada control d'assistència.
            #Si falla quelcom no modifiquem impartir.
            retornIdsCAsModificats = ''
            for caEnviatPerXarxa in controlsAssistencia:
                ca = ControlAssistencia.objects.get(pk=caEnviatPerXarxa['pk']) #type: ControlAssistencia
                ca.estat = EstatControlAssistencia.objects.get(pk=caEnviatPerXarxa['estat'])
                ca.currentUser = usuari
                ca.professor = User2Professor(usuari)
                ca.credentials = (usuari, False) #Usuari i L4.
                ca.save()
                if (retornIdsCAsModificats != ''):
                    retornIdsCAsModificats += ', '
                retornIdsCAsModificats += str(ca.pk)

            impartir.dia_passa_llista = datetime.datetime.now()
            impartir.professor_passa_llista = User2Professor(usuari)
            impartir.currentUser = usuari
            impartir.save()

            # LOGGING
            Accio.objects.create(
                tipus='PL',
                usuari=usuari,
                l4=False,
                impersonated_from=None,
                text=u"""Passar llista API presenciaRest: {0}.""".format(impartir)
            )
                                
            msg = '{"ids": "' + str(retornIdsCAsModificats) + '"}'
            impartir_despres_de_passar_llista(impartir)

            return Response(msg)
        except Exception as excpt:
            traceback.print_exc()
            return Response('Error API' + str(excpt), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GetFrangesHoraries(APIViewAutenticadaAmbToken):
    
    def get(self, request):
        try:
            franges = FranjaHoraria.objects.all()
            serializer = mySerializers.FranjaHorariaSerializer(franges, many=True)
            return Response(serializer.data)
        except Exception as excpt:
            traceback.print_exc()
            return Response('Error API' + str(excpt), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class getEstatsControlAssistencia(APIViewAutenticadaAmbToken):
    
    def get(self, request):
        try:
            estats = EstatControlAssistencia.objects.all()
            serializer = mySerializers.EstatControlAssistenciaSerializer(estats, many=True)
            return Response(serializer.data)
        except Exception as excpt:
            traceback.print_exc()
            return Response('Error API' + str(excpt), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class getProfes(APIViewAutenticadaAmbToken):
    
    def get(self, request):
        try:
            profes = Professor.objects.all()
            serializer = mySerializers.ProfessorSerializer(profes, many=True)
            return Response(serializer.data)
        except Exception as excpt:
            traceback.print_exc()
            return Response('Error API' + str(excpt), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class getAPILevel(APIView):
    
    def get(self, request):
        return HttpResponse(API_LEVEL)
