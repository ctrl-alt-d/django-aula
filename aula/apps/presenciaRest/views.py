# -*- coding: utf-8 -*-
import traceback
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from django.http import JsonResponse, HttpResponse, HttpResponseServerError
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from . import utils
from aula.apps.presencia.models import Impartir, ControlAssistencia, EstatControlAssistencia
from . import serializers

class Ajuda(APIView):
    #Activar això per tal de protegir la API.
    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        return HttpResponse("API DjAu per passar llista")
        #usernames = [user.username for user in User.objects.all()]
        #return Response(usernames)


class ListImpartirPerData(APIView):

    #authentication_classes = [authentication.TokenAuthentication]
    #permission_classes = [IsAuthenticated]

    def get(self, request, paramData, idUsuari):
        #type: (HttpRequest, str, str) -> HttpResponse
        #Retorna tots els registres del model Impartir donada una data.
        #El format d'ingŕes de la data és Y-M-D
        
        try:
            data = utils.convertirData(paramData)
            usuari = utils.obtenirUsuari(idUsuari)
            if not usuari:
                return Response('Usuari no localitzat', status=status.HTTP_404_NOT_FOUND)

            idProfe = usuari.pk
            #Sempre obtinc les classes a impartir dels profes que fan classe i els de guàrdia.
            classesAImpartirDelDia = Impartir.objects.filter(
                Q(horari__professor__id = idProfe, dia_impartir=data) |
                Q(professor_guardia_id = idProfe, dia_impartir=data)).order_by('horari__hora')
            serializer = serializers.ImpartirSerializer(classesAImpartirDelDia, many=True)
            return Response(serializer.data)
        except:
            traceback.print_exc()
            return Response('Error API', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListControlAssistencia(APIView):
    
    def get(self, request, idImpartir, idUsuari):
        #
        #Retorna una llista d'objectes JSON
        #Cada objecte conté tres valors ca (controlAssistencia), alumne(Alumne) i estat(Codi estat hora anterior).
        #
        try:
            usuari = utils.obtenirUsuari(idUsuari)
            if not usuari:
                return HttpResponseNotFound('Usuari no localitzat')
        
            cas = utils.ControlAssistenciaIHoraAnterior.objects.filter(
                impartir__id=idImpartir).order_by('alumne__cognoms')
            print(cas)
            serializer = serializers.ControlAssistenciaIHoraAnteriorSerializer(cas, many=True)            

            '''for ca in cas: #type: ControlAssistencia
                #print "CA:", ca.impartir.horari.hora.hora_inici
                if assistencies != "":
                    assistencies+=","
                
                estatHoraAnterior="-1"
                if utils.faltaHoraAnterior(ca):
                    estatHoraAnterior = utils.faltaHoraAnterior(ca).pk

                assistencies+= '{ "ca":%s, "estatHoraAnterior":"%s", "alumne":%s }' % \
                    (serializers.serialize('json', [ca])[1:-1], 
                    estatHoraAnterior,
                    serializers.serialize('json', [ca.alumne])[1:-1])
            dadesAEnviar = "[%s]" % assistencies
            #print (dadesAEnviar)'''
            return Response(serializer.data)
        except:
            traceback.print_exc()
            return Response('Error API', status=status.HTTP_500_INTERNAL_SERVER_ERROR)










# Faig l'autenticació basada en la idea:
# https://www.ibm.com/support/knowledgecenter/en/SSFKSJ_9.0.0/com.ibm.mq.sec.doc/q128720_.htm
# Es tracta de passar un token a l'usuari un cop s'hagi autenticat, així no exposo el password cada vegada.
'''
from __future__ import unicode_literals
import json, traceback, datetime
from typing import Dict

from django.conf import settings
from django.db.models.query import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseServerError, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError, NON_FIELD_ERRORS
from django.db.models import Q
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

from . import utils
from aula.apps.presencia.models import Impartir, ControlAssistencia, EstatControlAssistencia
from aula.apps.usuaris.models import User2Professor, Accio, Professor
from aula.apps.alumnes.models import Alumne
from aula.apps.presencia.business_rules.impartir import impartir_despres_de_passar_llista
from aula.apps.horaris.models import FranjaHoraria, Horari
from django.contrib.auth import authenticate

#Dicionari de tokens d'usuari indexats per id usuari.

usuariTokens = {}

API_LEVEL = "1"

def ajuda(request):
    return HttpResponse('API Rest framework, per usar en Android i altres sistemes.')

@csrf_exempt
def login(request):
    #type: (HttpRequest) -> HttpResponse
    #Obtenir el body de la petició, generar un token, aquest token el rebrà l'usuari i podrà accedir a tota l'API a través seu, 
    #així no exposem el password. 
    #Guardarem el token en memòria i esborrem els que superin una hora des de que han estat creats'.

    idUsuari = request.POST.get('idusuari','')
    passwd = request.POST.get('password','')
    print (request.POST, request.content_type)
    
    usuari = authenticate(username=idUsuari, password=passwd)
    if usuari is None:
        return HttpResponseNotFound('Usuari no localitzat o password incorrecte.')
        
    token = utils.gen_password(length=50)
    dataExpiracioToken = datetime.datetime.now()+datetime.timedelta(minutes=60)
    usuariTokens[usuari.pk] = utils.TokenICaducitat(token, dataExpiracioToken)
    
    response = HttpResponse(token)
    response.set_cookie('token', token)
    return response
    

def getImpartirPerData(request, paramData, idUsuari):
    #type: (HttpRequest, str, str) -> HttpResponse
    #Retorna tots els registres del model Impartir donada una data.
    #El format d'ingŕes de la data és Y-M-D
    
    try:
        data = utils.convertirData(paramData)
        usuari = utils.obtenirUsuari(idUsuari)
        if not usuari:
            return HttpResponseNotFound('Usuari no localitzat')

        if not utils.tokenCorrecte(request, usuariTokens, usuari.pk):
            return HttpResponseBadRequest("Token no trobat")
        
        idProfe = usuari.pk
        #Sempre obtinc les classes a impartir dels profes que fan classe i els de guàrdia.
        classesAImpartirDelDia = Impartir.objects.filter(
            Q(horari__professor__id = idProfe, dia_impartir=data) |
            Q(professor_guardia_id = idProfe, dia_impartir=data)).order_by('horari__hora')
        llistaClasseAImpartirHorari = ''
        for classeAImpartir in classesAImpartirDelDia:
            horariSerialitzat = serializers.serialize('json', [classeAImpartir.horari.hora])[1:-1]
            classeAImpartirSerialitzada = serializers.serialize('json', [classeAImpartir])[1:-1]
            #print(classeAImpartirSerialitzada, horariSerialitzat, classeAImpartir.horari.assignatura.nom_assignatura)
            tmp= {"impartir": %s,
                "horari": %s,
                "assignatura": "%s"} % (classeAImpartirSerialitzada, horariSerialitzat, classeAImpartir.horari.assignatura.nom_assignatura)
            if llistaClasseAImpartirHorari!='':
                llistaClasseAImpartirHorari+=','
            llistaClasseAImpartirHorari+=tmp
        dadesAEnviar = '[' + llistaClasseAImpartirHorari + ']' #json.dumps(llistaClasseAImpartirHorari, ensure_ascii=False).encode('utf-8')
        #print ("A enviar:", dadesAEnviar)
        return HttpResponse(dadesAEnviar)
    except:
        traceback.print_exc()
        return HttpResponseServerError('Error API')

def getControlAssistencia(request, idImpartir, idUsuari):
    #
    #Retorna una llista d'objectes JSON
    #Cada objecte conté tres valors ca (controlAssistencia), alumne(Alumne) i estat(Codi estat hora anterior).
    #
    try:
        usuari = utils.obtenirUsuari(idUsuari)
        if not usuari:
            return HttpResponseNotFound('Usuari no localitzat')

        if not utils.tokenCorrecte(request, usuariTokens, usuari.pk):
                return HttpResponseBadRequest("Token no trobat")
        
        assistencies = ""
        cas = ControlAssistencia.objects.filter(
            impartir__id=idImpartir).order_by('alumne__cognoms')
        for ca in cas: #type: ControlAssistencia
            #print "CA:", ca.impartir.horari.hora.hora_inici
            if assistencies != "":
                assistencies+=","
            
            estatHoraAnterior="-1"
            if utils.faltaHoraAnterior(ca):
                estatHoraAnterior = utils.faltaHoraAnterior(ca).pk

            assistencies+= '{ "ca":%s, "estatHoraAnterior":"%s", "alumne":%s }' % \
                (serializers.serialize('json', [ca])[1:-1], 
                estatHoraAnterior,
                serializers.serialize('json', [ca.alumne])[1:-1])
        dadesAEnviar = "[%s]" % assistencies
        #print (dadesAEnviar)
        return HttpResponse(dadesAEnviar)
    except:
        traceback.print_exc()
        return HttpResponseServerError('Error API')

@csrf_exempt
def putControlAssistencia(request, idImpartir, idUsuari):
    #type: (HttpRequest, str, str) -> HttpResponse
    # Passa llista d'una hora en concret, rebem un array de ControlAssistencia en JSON.
    try:
        usuari = utils.obtenirUsuari(idUsuari)
        if not usuari:
            return HttpResponseNotFound('Usuari no localitzat')

        if not utils.tokenCorrecte(request, usuariTokens, usuari.pk):
            return HttpResponseBadRequest("Token no trobat")
        
        impartir = Impartir.objects.get(pk=idImpartir)
        pertany_al_professor = usuari.pk in [impartir.horari.professor.pk, \
                                       impartir.professor_guardia.pk if impartir.professor_guardia else -1]
        if not (pertany_al_professor):
            return HttpResponseServerError('No tens permissos per passar llista')    

        #Comprovar que no sigui una assignatura prohibida de passar a través de WebService, cas UF's Monti.
        if impartir.horari.assignatura.tipus_assignatura in (settings.CUSTOM_PRESENCIA_VIEW_TIPUS_ASSIGNATURES_PROHIBIDES):
            return HttpResponseServerError(u"No pots actualitzar assignatures de tipus: " + unicode(settings.CUSTOM_PRESENCIA_VIEW_TIPUS_ASSIGNATURES_PROHIBIDES))

        #Retorna una llista de controls d'assistència.
        controlsAssistencia = json.loads(request.body) #type: Dict
        
        #Modifica només en cas que hi hagi elements a modificar.
        if len(controlsAssistencia) > 0:

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

            return HttpResponse(msg)
        else:
            return HttpResponseServerError('Cal passar informació en el body.')    
    except ValidationError as excpt:
        #import ipdb; ipdb.set_trace()
        return HttpResponseServerError(excpt.message_dict[NON_FIELD_ERRORS])
    except Exception as excpt:
        traceback.print_exc()
        #import ipdb; ipdb.set_trace()
        return HttpResponseServerError('Error API')

def getFrangesHoraries(request, idUsuari):
    try:
        usuari = utils.obtenirUsuari(idUsuari)
        if not usuari:
            return HttpResponseNotFound('Usuari no localitzat')

        franges = FranjaHoraria.objects.all()
        return HttpResponse(serializers.serialize('json', franges))
    except Exception as excpt:
        traceback.print_exc()
        #import ipdb; ipdb.set_trace()
        return HttpResponseServerError('Error API')

def getEstatControlAssistencia(request, idUsuari):
    try:
        usuari = utils.obtenirUsuari(idUsuari)
        if not usuari:
            return HttpResponseNotFound('Usuari no localitzat')

        estats = EstatControlAssistencia.objects.all()
        return HttpResponse(serializers.serialize('json', estats))
    except Exception as excpt:
        traceback.print_exc()
        #import ipdb; ipdb.set_trace()
        return HttpResponseServerError('Error API')

def getProfes(request, idUsuari):
    try:
        correcte, HttpResponseOnError = utils.comprovarUsuariIPermisos(request, idUsuari, usuariTokens)
        if not correcte:
            return HttpResponseOnError

        return HttpResponse(serializers.serialize('json', Professor.objects.all()))
    except Exception as excpt:
        traceback.print_exc()
        #import ipdb; ipdb.set_trace()
        return HttpResponseServerError('Error API')

@csrf_exempt
def putGuardia(request, idUsuari):
    try:
        correcte, HttpResponseOnError = utils.comprovarUsuariIPermisos(request, idUsuari, usuariTokens)
        if not correcte:
            return HttpResponseOnError

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

        if dadesAModificar[0].horari.assignatura.tipus_assignatura in (settings.CUSTOM_PRESENCIA_VIEW_TIPUS_ASSIGNATURES_PROHIBIDES):
            return HttpResponseServerError(u"No pots actualitzar assignatures de tipus: " + unicode(settings.CUSTOM_PRESENCIA_VIEW_TIPUS_ASSIGNATURES_PROHIBIDES))

        if len(dadesAModificar)==0:
            return HttpResponseNotFound("Error, no existeix aquesta guàrdia")
        dadesAModificar.update( professor_guardia = professor_guardia  )
        return HttpResponse("ok")

    except Exception as excpt:
        traceback.print_exc()
        return HttpResponseServerError('Error API')

def getAPILevel(req):
    return HttpResponse(API_LEVEL)

def test(request):
    alumne = {"nom":'ó'}
    dades = json.dumps(alumne, ensure_ascii=False).encode('utf-8')
    return HttpResponse(u'ó'.encode('utf-8') + dades)
'''