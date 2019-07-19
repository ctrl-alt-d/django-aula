# -*- coding: utf-8 -*-
import json
from datetime import date
from django.test import TestCase
from django.test.client import Client
from django.core import serializers
from aula.apps.alumnes.models import Nivell, Curs, Grup
from aula.apps.horaris.models import DiaDeLaSetmana, FranjaHoraria, Horari
from aula.apps.presencia.models import Impartir, ControlAssistencia
from aula.apps.assignatures.models import Assignatura, TipusDAssignatura
from aula.apps.aules.models import Aula
from aula.utils.testing.tests import TestUtils
from . import utils

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
        
    def test_login(self):
        c = Client()
        response = c.post('/presenciaRest/login/', data={'username': 'SrProgramador', 'password': 'patata'})
        print (response.status_code)
        self.assertTrue(response.status_code==200)

    def test_ajuda(self):
        c = Client()
        response = c.post('/presenciaRest/login/', data={'username': 'SrProgramador', 'password': 'patata'})
        token = json.loads(response.content)['token']
        #Agafa el token i passal a la següent petició.
        header = {'HTTP_AUTHORIZATION': 'Token ' + token}
        response = c.get('/presenciaRest/ajuda/', **header)
        self.assertTrue(response.status_code==200)

'''
    def test_impartirPerData(self):
        c = Client()
        data = {'idusuari': 'SrProgramador', 'password': 'patata'}
        response = c.post('/presenciaRest/login/', data={'idusuari': 'SrProgramador', 'password': 'patata'})
        response = c.get('/presenciaRest/getImpartirPerData/{}/SrProgramador/'.format(self.dataTest.strftime('%Y-%m-%d')))
        dades = response.content.decode('utf-8')
        self.assertTrue(u'"assignatura": "Programació"' in dades)
        
    def test_getControlAssistencia(self):
        c = Client()
        response = c.post('/presenciaRest/login/', data={'idusuari': 'SrProgramador', 'password': 'patata'})
        response = c.get('/presenciaRest/getControlAssistencia/{}/{}/'.format(self.classesAImpartir[0].pk, 'SrProgramador'))
        dades = response.content.decode('utf-8')
        assistenciesJSON = json.loads(dades)
        #print (response)
        self.assertEqual(len(assistenciesJSON), len(self.alumnes))

    def test_putControlAssistencia(self):
        c = Client()
        response = c.post('/presenciaRest/login/', data={'idusuari': 'SrProgramador', 'password': 'patata'})
        response = c.get('/presenciaRest/getControlAssistencia/{}/{}/'.format(self.classesAImpartir[0].pk, 'SrProgramador'))
        assistenciesJSON = json.loads(response.content.decode('utf-8'))
        #caDeserialitzat =  serializers.deserialize('json', u'[' + assistenciesJSON[0]['ca'] + u']').next()
        ca = utils.deserialitzarUnElementAPartirObjectePython(assistenciesJSON[0]['ca']).object
        #ca.alumne = self.alumnes[0]
        ca.estat = self.estats['r']
        #ca.impartir = self.classesAImpartir[0]
        ca.professor = self.profe
        ca.save()
        
        caMinim = """
        [{{
            "pk": {}, 
            "estat": {}
        }}]""".format(ca.pk, ca.estat.pk)

        response = c.post(
            '/presenciaRest/putControlAssistencia/{}/{}/'.format(self.classesAImpartir[0].pk, 'SrProgramador'), 
            data=caMinim, 
            content_type="application/json")
        if response.status_code != 200:
            raise Exception("Error:" + response.content)
        #print ("DADES ENVIADES:", serializers.serialize('json', [ca]))
        response = c.get('/presenciaRest/getControlAssistencia/{}/{}/'.format(self.classesAImpartir[0].pk, 'SrProgramador'))
        assistenciesJSON = json.loads(response.content.decode('utf-8'))
        ca = utils.deserialitzarUnElementAPartirObjectePython(assistenciesJSON[0]['ca']).object
        #print ("DADES MODIFICADES:", ca.estat)
        self.assertEqual(ca.estat, self.estats['r'])

    def test_putControlAssistenciaManual(self):
        c = Client()
        response = c.post('/presenciaRest/login/', 
            data={'idusuari': 'SrProgramador', 'password': 'patata'})
        response = c.get('/presenciaRest/getControlAssistencia/{}/{}/'.format(self.classesAImpartir[0].pk, 'SrProgramador'))
        assistenciesJSON = json.loads(response.content.decode('utf-8'))
        ca = utils.deserialitzarUnElementAPartirObjectePython(assistenciesJSON[0]['ca']).object #type: ControlAssistencia

        #Doblo els {}
        caMinim = """
        [{{
            "pk": {}, 
            "estat": {}
        }}]""".format(ca.pk, self.estats['f'].pk)
        response = c.post(
            '/presenciaRest/putControlAssistencia/{}/{}/'.format(self.classesAImpartir[0].pk, 'SrProgramador'), 
            data=caMinim, 
            content_type="application/json")
        response = c.get('/presenciaRest/getControlAssistencia/{}/{}/'.format(self.classesAImpartir[0].pk, 'SrProgramador'))
        #print ("--------------------------------------")
        #print (response.content.decode('utf-8'))
        assistenciesJSON = json.loads(response.content.decode('utf-8'))
        ca = utils.deserialitzarUnElementAPartirObjectePython(assistenciesJSON[0]['ca']).object
        self.assertEqual(ca.estat, self.estats['f'])

    def test_putControlAssistenciaSensePermisos(self):
        #Hauria de petar la API indicant que no tens permisos per fer el canvi.
        c = Client()
        response = c.post('/presenciaRest/login/', 
            data={'idusuari': 'SrProgramador', 'password': 'patata'})
        response = c.get('/presenciaRest/getControlAssistencia/{}/{}/'.format(self.classesAImpartir[-1].pk, 'SrProgramador'))
        assistenciesJSON = json.loads(response.content.decode('utf-8'))
        ca = utils.deserialitzarUnElementAPartirObjectePython(assistenciesJSON[0]['ca']).object #type: ControlAssistencia

        #Doblo els {}
        caMinim = """
        [{{
            "pk": {}, 
            "estat": {}, 
        }}]""".format(ca.pk, ca.alumne.pk, self.estats['f'].pk, ca.impartir.pk, self.profe.pk)

        response = c.post(
            '/presenciaRest/putControlAssistencia/{}/{}/'.format(self.classesAImpartir[-1].pk, 'SrProgramador'), 
            data=caMinim, 
            content_type="application/json")
        self.assertEqual(response.status_code, 500)

    def test_getFrangesHoraries(self):
        #Hauria de petar la API indicant que no tens permisos per fer el canvi.
        c = Client()
        response = c.post('/presenciaRest/login/', 
            data={'idusuari': 'SrProgramador', 'password': 'patata'})
        response = c.get('/presenciaRest/getFrangesHoraries/{}/'.format('SrProgramador'))
        
        franges = serializers.deserialize('json', response.content.decode('utf-8'))
        count = 0
        for franja in franges:
            count +=1
            #print (franja)
        self.assertEqual(count, 2)

    def test_getProfes(self):
        #Hauria de petar la API indicant que no tens permisos per fer el canvi.
        c = Client()
        response = c.post('/presenciaRest/login/', 
            data={'idusuari': 'SrProgramador', 'password': 'patata'})
        response = c.get('/presenciaRest/getProfes/{}/'.format('SrProgramador'))
        #print (response.content)
        profes = serializers.deserialize('json', response.content.decode('utf-8'))
        count = 0
        count = 0
        for profe in profes:
            #print (profe)
            count +=1
        self.assertEqual(count, 2)

    def test_putGuardia(self):
        #Hauria de petar la API indicant que no tens permisos per fer el canvi.
        c = Client()
        response = c.post('/presenciaRest/login/', 
            data={'idusuari': 'SrProgramador', 'password': 'patata'})
        
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

        response = c.post(
            '/presenciaRest/putGuardia/{}/'.format('SrProgramador'), 
            data=jsonAEnviar,
            content_type="application/json")
        
        response = c.post('/presenciaRest/login/', data={'idusuari': 'Profe2', 'password': 'patata'})
        response = c.get('/presenciaRest/getImpartirPerData/{}/Profe2/'.format(self.dataTest.strftime('%Y-%m-%d')))
        dades = json.loads(response.content.decode('utf-8'))
        self.assertTrue(str(dades[0]['impartir']['fields']['professor_guardia'])==str(self.profe.pk))

    def test_test(self):
        from .utils import faltaHoraAnterior
        cas = ControlAssistencia.objects.filter(
            impartir__id=self.classesAImpartir[0].pk)
        ca= cas[0] #type: ControlAssistencia
        
        from django.db import transaction
        with transaction.atomic():
            ca.estat = self.estats['p']
            ca.save()
        
        casActual = ControlAssistencia.objects.filter(
            impartir__id=self.classesAImpartir[1].pk)

'''