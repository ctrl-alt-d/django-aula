# -*- coding: utf-8 -*-
import json
from datetime import date
from django.test import TestCase
from django.test.client import Client
from django.core import serializers
from django.conf import settings

from aula.apps.alumnes.models import Nivell, Curs, Grup
from aula.apps.horaris.models import DiaDeLaSetmana, FranjaHoraria, Horari
from aula.apps.presencia.models import Impartir, ControlAssistencia
from aula.apps.assignatures.models import Assignatura, TipusDAssignatura
from aula.apps.aules.models import Aula
from aula.utils.testing.tests import TestUtils
from . import utils

#typing.
from typing import Dict
from django.core.handlers.wsgi import WSGIRequest
from rest_framework.response import Response
from .utils import ControlAssistenciaIHoraAnterior

class Test(TestCase):

    def setUp(self):
        tUtils = TestUtils()
        
        #Crear n alumnes.
        DAM = Nivell.objects.create(nom_nivell='DAM') #type: Nivell
        primerDAM = Curs.objects.create(nom_curs='1er', nivell=DAM) #type: Curs
        primerDAMA = Grup.objects.create(nom_grup='A', curs=primerDAM) #type: Grup
        
        self.alumnes = tUtils.generaAlumnesDinsUnGrup(primerDAMA, 10)
        
        # Crear un profe.
        self.profe = tUtils.crearProfessor('SrProgramador','patata')
        self.profe2 = tUtils.crearProfessor('Profe2', 'patata')
        self.professional = tUtils.crearUsuari('Professional', 'patata')

        #Crear un horari, 
        dataDiaActual = date.today() #type: date
        dataDiaAnterior = tUtils.obtenirDataLaborableAnterior(dataDiaActual)
        self.dataTest = dataDiaAnterior #type: date

        #Obtenir dos dies laborals anteriors.
        diaAnterior = dataDiaAnterior.weekday()
        diaAnteriorUK = dataDiaAnterior.isoweekday()
        
        diaSetmanaAhir = DiaDeLaSetmana.objects.create(n_dia_uk=diaAnteriorUK,n_dia_ca=diaAnterior,
            dia_2_lletres=tUtils.diesSetmana2Lletres[diaAnterior],dia_de_la_setmana=tUtils.diesSetmana[diaAnterior], es_festiu=False)
        
        #Crear franges horaries.
        franges = [
            FranjaHoraria.objects.create(hora_inici = u'9:00', hora_fi = u'10:00'), 
            FranjaHoraria.objects.create(hora_inici = u'10:00', hora_fi = u'11:00')]
        self.franges = franges
        
        tipusAssigUF = TipusDAssignatura.objects.create(
            tipus_assignatura=u'Unitat Formativa')

        aula = Aula.objects.create(nom_aula=u"3.04", descripcio_aula=u"La 3.04")

        programacioDAM = Assignatura.objects.create(
            nom_assignatura=u'Programació', curs=primerDAM,
            tipus_assignatura = tipusAssigUF
        )

        #Crea controls d'assistencia
        self.estats = tUtils.generarEstatsControlAssistencia()

        #Crear dos franges horaries de programació en data d'ahir i crea alumnes a dins l'hora.        
        entradesHorari = []
        self.classesAImpartir = []
        self.classesAImpartirProfe = []
        for i in range(0,2):
            entradesHorari.append(
                Horari.objects.create(
                    assignatura=programacioDAM, 
                    professor=self.profe,
                    grup=primerDAMA, 
                    dia_de_la_setmana=diaSetmanaAhir,
                    hora=franges[i],
                    aula=aula,
                    es_actiu=True))

            #Aquí hauriem de crear unes quantes classes a impartir i provar que l'aplicació funciona correctament.
            classeAImpartir = Impartir.objects.create(
                    horari = entradesHorari[i],
                    professor_passa_llista = self.profe,
                    dia_impartir = dataDiaAnterior)#type: Impartir
            self.classesAImpartirProfe.append(classeAImpartir)
            self.classesAImpartir.append(classeAImpartir)
            tUtils.omplirAlumnesHora(self.alumnes, classeAImpartir)

        entradesHorari.append(
                Horari.objects.create(
                    assignatura=programacioDAM, 
                    professor=self.profe2,
                    grup=primerDAMA, 
                    dia_de_la_setmana=diaSetmanaAhir,
                    hora=franges[0],
                    aula=aula,
                    es_actiu=True))
        
        self.classesAImpartir.append(
            Impartir.objects.create(
                    horari = entradesHorari[-1],
                    professor_passa_llista = self.profe2,
                    dia_impartir = dataDiaAnterior))
        tUtils.omplirAlumnesHora(self.alumnes, self.classesAImpartir[-1])

    def _getToken(self, response):
        #Obtenir el token a partir de la response.
        #Desactivo el token només per efectes de facilitar la programació i el 
        #debug de l'aplicació.
        if settings.CUSTOM_MODUL_EXTAULADROID_VIEW_DESACTIVA_AUTH_TOKEN:
            return 'fakeToken'
        else:
            return json.loads(response.content)['token']

    def _putTokenInHeader(self, token):
        return {'HTTP_AUTHORIZATION': 'Token ' + token}
   
    def _getTokenAndPutInHeader(self, response)->Dict[str, str]:
        #Obté el token del Login i el posa en el header a enviar en 
        #cada petició.
        #import ipdb; ipdb.set_trace()   
        token = self._getToken(response)
        header = self._putTokenInHeader(token)
        return header

    def test_login(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', data={'username': 'SrProgramador', 'password': 'patata'})
        self.assertTrue(response.status_code==200)

    def test_ajuda(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'SrProgramador', 'password': 'patata'})
        #Agafa el token i passal a la següent petició.
        header = header = self._getTokenAndPutInHeader(response)
        response = c.get('/extAulaDroid/ajuda/', **header)
        self.assertTrue(response.status_code==200)

    def test_putGuardia(self):
        #Hauria de petar la API indicant que no tens permisos per fer el canvi.
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'SrProgramador', 'password': 'patata'})
        #Agafa el token i passal a la següent petició.
        header = self._getTokenAndPutInHeader(response)
        #Doblo els {}
        jsonAEnviar = """
        {{
            "idUsuariASubstituir":"{}", 
            "idUsuari":"{}", 
            "idFranja":"{}",
            "diaAImpartir":"{}"
        }}""".format(
            self.profe2.username,
            self.profe.username,
            self.franges[0].pk,
            self.dataTest.strftime("%Y-%m-%d"))

        response = c.put(
            '/extAulaDroid/putGuardia/', 
            data=jsonAEnviar,
            content_type="application/json", **header)
        
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'Profe2', 'password': 'patata'})
        header = self._getTokenAndPutInHeader(response)
        response = c.get('/extAulaDroid/getImpartirPerData/{}/Profe2/'.format(
            self.dataTest.strftime('%Y-%m-%d')), **header)
        dades = json.loads(response.content.decode('utf-8'))
        self.assertTrue(str(dades[0]['professor_guardia'])==str(self.profe.pk))

    def test_impartirPerData(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'SrProgramador', 'password': 'patata'})
        token = self._getToken(response)
        header = self._putTokenInHeader(token)
        url = '/extAulaDroid/getImpartirPerData/{}/SrProgramador/'.format(
            self.dataTest.strftime('%Y-%m-%d'))
        #print (url)
        response = c.get(url, **header)
        dades = response.content.decode('utf-8')
        #print ("debug", dades)
        self.assertTrue('"nom_assignatura":"Programació"' in dades)

    def test_getControlAssistencia(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'SrProgramador', 'password': 'patata'})
        header = self._getTokenAndPutInHeader(response)
        response = c.get('/extAulaDroid/getControlAssistencia/{}/{}/'.format(
            self.classesAImpartir[0].pk, 'SrProgramador'), **header)
        dades = response.content.decode('utf-8')
        #print (dades)
        assistenciesJSON = json.loads(dades)
        self.assertEqual(len(assistenciesJSON), len(self.alumnes))

    def test_putControlAssistenciaManual(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'SrProgramador', 'password': 'patata'})
        header = self._getTokenAndPutInHeader(response)
        response: Response = c.get('/extAulaDroid/getControlAssistencia/{}/{}/'.format(
            self.classesAImpartir[0].pk, 'SrProgramador'), **header)
        
        assistenciesJSON = json.loads(response.content.decode('utf-8'))
        ca: ControlAssistenciaIHoraAnterior = assistenciesJSON[0]
        
        #Doblo els {}
        caMinim = [{ 
            "pk": ca['id'],
            "estat": self.estats['f'].pk,
        }]
        response = c.put(
            '/extAulaDroid/putControlAssistencia/{}/{}/'.format(self.classesAImpartir[0].pk, 'SrProgramador'), 
            data=json.dumps(caMinim), 
            content_type="application/json", **header)
        response = c.get('/extAulaDroid/getControlAssistencia/{}/{}/'.format(
            self.classesAImpartir[0].pk, 'SrProgramador'), **header)
        #print ("--------------------------------------")
        assistenciesJSON = json.loads(response.content.decode('utf-8'))
        ca = assistenciesJSON[0]
        self.assertEqual(ca['estat'], self.estats['f'].pk)

    def test_postControlAssistenciaSensePermisos(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'Profe2', 'password': 'patata'})
        header = self._getTokenAndPutInHeader(response)
        
        #Obtinc el control d'assistència del primer alumne.
        ca = ControlAssistencia.objects.filter(
                impartir__id=self.classesAImpartirProfe[0].pk) \
                .order_by('alumne__cognoms')[0]
        #Doblo els {}
        caMinim = [{
            "pk": ca.id,
            "estat": self.estats['p'].pk
        }]
        response = c.put(
            '/extAulaDroid/putControlAssistencia/{}/{}/'.format(
            self.classesAImpartir[0].pk, 'Profe2'), 
            data=json.dumps(caMinim), 
            content_type="application/json", **header)
        self.assertNotEqual(response.status_code, 200)

    def test_getFrangesHoraries(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'SrProgramador', 'password': 'patata'})
        header = self._getTokenAndPutInHeader(response)
        response = c.get('/extAulaDroid/getFrangesHoraries/', **header)
        franges = json.loads(response.content.decode('utf-8'))
        
        count = 0
        for franja in franges:
            count +=1
        self.assertEqual(count, 2)

    def test_getEstatsControlAssistencia(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'SrProgramador', 'password': 'patata'})
        header = self._getTokenAndPutInHeader(response)
        response = c.get('/extAulaDroid/getEstatsControlAssistencia/', **header)
        estats = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(estats), 4)

    def test_getProfes(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'SrProgramador', 'password': 'patata'})
        header = self._getTokenAndPutInHeader(response)
        response = c.get('/extAulaDroid/getProfes/', **header)
        profes = json.loads(response.content.decode('utf-8')) 
        self.assertEqual(len(profes), 2)

    def test_getProfesAmbUsuariSensePermisos(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'Professional', 'password': 'patata'})
        header = self._getTokenAndPutInHeader(response)
        response: Response = c.get('/extAulaDroid/getProfes/', **header)
        #Ha de donar error perque no és un profe, no pot usar aquesta funció.
        self.assertEqual(response.status_code, 403)

    def test_comprovaSeguretatToken(self):
        c = Client()
        response = c.post('/extAulaDroid/login/', 
            data={'username': 'SrProgramador', 'password': 'patata'})
        response: Response = c.get('/extAulaDroid/getProfes/')
        self.assertNotEqual(response.status_code, 200, "Protecció token no activada, bé si estàs en debug.")