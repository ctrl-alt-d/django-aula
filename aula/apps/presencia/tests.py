#encoding: utf-8
import re
from datetime import date, timedelta

from django.test import TestCase, LiveServerTestCase
from django.test import Client
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from aula.apps.alumnes.models import Nivell, Curs, Grup
from aula.apps.horaris.models import DiaDeLaSetmana, FranjaHoraria, Horari
from aula.apps.assignatures.models import Assignatura, TipusDAssignatura
from aula.apps.presencia.models import Impartir, ControlAssistencia, EstatControlAssistencia
from aula.apps.presencia.test.testDBCreator import TestDBCreator
from aula.utils.testing.tests import SeleniumLiveServerTestCase

class SimpleTest(TestCase):

    def setUp(self):
        self.db = TestDBCreator()
        self.url = 'http://localhost:8000'
        
    def test_numeroAlumnesMostratsEsCorrecte(self):
        c = Client()
        response = c.post(self.url + '/usuaris/login/', {'usuari':'SrProgramador', 'paraulaDePas':'patata'})
        response = c.get( self.url + '/presencia/passaLlista/' + str(self.db.programacioDiaAnterior.pk) + '/')
        c:bytes = response.content
        nBotonsPresent = c.count(b"btn btn-default btnPresent")
        self.assertTrue(nBotonsPresent == self.db.nAlumnesGrup, "Error falten usuaris en el llistat")

    def test_passarLlistaModificaBD(self):
        c = Client()
        response = c.post(self.url + '/usuaris/login/', {'usuari':'SrProgramador', 'paraulaDePas':'patata'})
        response = c.get(self.url + '/presencia/passaLlista/' + str(self.db.programacioDiaAnterior.pk) + '/')
        #Localitzar els CA's que cal enviar.
        estatsAEnviar=self.obtenirEstats(response.content.decode('utf-8'))
        
        response = c.post(self.url + '/presencia/passaLlista/' + str(self.db.programacioDiaAnterior.pk) + '/', 
         estatsAEnviar)
        
        #Comprova que ha canviat l'estat.
        controlsAssistencia = ControlAssistencia.objects.filter(impartir=self.db.programacioDiaAnterior, estat=self.db.estats['p'])
        self.assertTrue(len(controlsAssistencia) == self.db.nAlumnesGrup, 
            "Error el número de controls d'assisència marcats com a present hauria de ser " + str(self.db.nAlumnesGrup) + 
            "i és:" + str(len(controlsAssistencia)))
    
    def obtenirEstats(self, html:str):
        valorsAEnviar={}
        
        matches=re.findall('name="[0-9]+-estat"', html)
        for match in matches:
            coincidencia = str(match)[6:-1]
            valorsAEnviar[coincidencia] = self.db.estats['p'].pk
        return valorsAEnviar


class MySeleniumTests(SeleniumLiveServerTestCase):

    def setUp(self):
        self.db = TestDBCreator()
        #self.selenium = WebDriver()
        options = webdriver.FirefoxOptions()
        #Opció que mostra el navegador o no el mostra (prefereixo que no el mostri així puc programar mentre executo tests.)
        options.add_argument('-headless')

        self.selenium = webdriver.Firefox(firefox_options=options)

        self.selenium.implicitly_wait(5)
    
    def tearDown(self):
        self.selenium.close()

    def test_comprovarOpcioForcarTreure(self):
        #Login
        #Passa llista tot a present alumne X fa falta.
        #Treure alumne X de la hora. No marcar la opció forçar, comprovar que l'alumne continua present.
        #Treure alumne X de la hora. Marcar la opció forçar. Comprovar que l'alumne no està dins la hora.
        self.loginUsuari()
        self.selenium.get(self.live_server_url + '/presencia/afegeixAlumnesLlista/' + 
            str(self.db.programacioDillunsHoraBuidaAlumnes.pk) + '/')
        
        alumneX=self.db.alumnes[0]
        self.seleccionarAlumne(alumneX.pk)
        self.seleccionarAlumne(self.db.alumnes[1].pk)
        self.seleccionarAlumne(self.db.alumnes[2].pk)
        self.selenium.find_elements_by_xpath("//button[@type='submit']")[0].click()

        cas=ControlAssistencia.objects.filter(impartir_id=self.db.programacioDillunsHoraBuidaAlumnes.pk) 
        casAlumneX = cas.get(alumne=alumneX)
        for ca in cas:
            self.selenium.execute_script('x=document.getElementById("label_id_{}-estat_0"); x.click()'.format(ca.pk))
        self.selenium.execute_script('x=document.getElementById("label_id_{}-estat_1"); x.click()'.format(casAlumneX.pk))
        self.selenium.find_elements_by_xpath("//button[@type='submit']")[0].click()

        self.selenium.get(self.live_server_url + '/presencia/treuAlumnesLlista/' + 
            str(self.db.programacioDillunsHoraBuidaAlumnes.pk) + '/')
        self.seleccionarAlumne(alumneX.pk)
        self.selenium.find_elements_by_xpath("//button[@type='submit']")[0].click()

        caAlumneX=ControlAssistencia.objects.get(impartir_id=self.db.programacioDillunsHoraBuidaAlumnes.pk, alumne=alumneX) #type: ControlAssistencia
        estat = caAlumneX.estat #type: EstatControlAssistencia
        self.assertTrue(estat.codi_estat=='F')
        
        self.selenium.get(self.live_server_url + '/presencia/treuAlumnesLlista/' + 
            str(self.db.programacioDillunsHoraBuidaAlumnes.pk) + '/')
        self.seleccionarAlumne(alumneX.pk)
        botoTreureTot = self.selenium.find_element_by_id("id_tots-matmulla")
        botoTreureTot.click()
        self.selenium.find_elements_by_xpath("//button[@type='submit']")[0].click()

        caAlumnes=ControlAssistencia.objects.filter(impartir_id=self.db.programacioDillunsHoraBuidaAlumnes.pk, alumne=alumneX) #type: ControlAssistencia
        self.assertTrue(len(caAlumnes) == 0)

    def test_treureAlumnes(self):
        self.loginUsuari()

        self.selenium.get(self.live_server_url + '/presencia/afegeixAlumnesLlista/' + 
            str(self.db.programacioDillunsHoraBuidaAlumnes.pk) + '/')
        #Comprovar quants alumnes hi ha seleccionats en aquesta hora. No n'hi hauria d'haver cap.
        cas = ControlAssistencia.objects.filter(impartir_id=self.db.programacioDillunsHoraBuidaAlumnes.pk)
        self.assertTrue(len(cas)==0)

        #Seleccionar dos usuaris.
        for i in range(0,2):
            js = """ x = document.evaluate('//input[@type=\\\'checkbox\\\' and @value="""+str(self.db.alumnes[i].pk)+"""]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null );
                    x.singleNodeValue.click();
                """
            self.selenium.execute_script(js)
        #import ipdb; ipdb.set_trace()
        self.selenium.find_elements_by_xpath("//button[@type='submit']")[0].click()
        
        #Comprovar alumnes en aquesta hora, n'hi hauria d'haver-hi dos.
        cas = ControlAssistencia.objects.filter(impartir_id=self.db.programacioDillunsHoraBuidaAlumnes.pk)
        self.assertTrue(len(cas)==2)

        self.selenium.get(self.live_server_url + '/presencia/treuAlumnesLlista/' + 
            str(self.db.programacioDillunsHoraBuidaAlumnes.pk) + '/')

        #Seleccionar dos usuaris.
        js = """ x = document.evaluate('//input[@type=\\\'checkbox\\\' and @value="""+str(self.db.alumnes[0].pk)+"""]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null );
                x.singleNodeValue.click();
            """
        self.selenium.execute_script(js)
        self.selenium.find_elements_by_xpath("//button[@type='submit']")[0].click()
        
        #Queda només un usuari.
        cas = ControlAssistencia.objects.filter(impartir_id=self.db.programacioDillunsHoraBuidaAlumnes.pk)
        self.assertTrue(len(cas)==1)
    
    def test_afegirAlumnes(self):
        #Afegeix alumnes i comprova que hi siguin.
        self.loginUsuari()

        self.selenium.get(self.live_server_url + '/presencia/afegeixAlumnesLlista/' + 
            str(self.db.programacioDillunsHoraBuidaAlumnes.pk) + '/')
        #Comprovar quants alumnes hi ha seleccionats en aquesta hora. No n'hi hauria d'haver cap.
        cas = ControlAssistencia.objects.filter(impartir_id=self.db.programacioDillunsHoraBuidaAlumnes.pk)
        self.assertTrue(len(cas)==0)

        #Seleccionar uns quants usuaris.
        self.selenium.execute_script('''
           cbox = document.getElementsByTagName("input");
               for (i=0;i<cbox.length;i++){
                   if (cbox[i].type == "checkbox") {
                   console.log("hola:" + cbox[i].type); 
                   cbox[i].click()
               }
           }'''
        )
        botons = self.selenium.find_elements_by_xpath("//button[@type='submit']")
        botons[0].click()
        
        #Comprovar alumnes en aquesta hora, hi haurien de ser tots.
        cas = ControlAssistencia.objects.filter(impartir_id=self.db.programacioDillunsHoraBuidaAlumnes.pk)
        self.assertTrue(len(cas)==self.db.nAlumnesGrup)

    def test_passaLlista(self):
        #Passar llista convencional.
        self.loginUsuari()
        
        self.selenium.get(self.live_server_url + '/presencia/passaLlista/' + str(self.db.programacioDiaAnterior.pk) + '/')
        #Obtenir tots els controls d'assistenica de l'hora marcada
        cas=ControlAssistencia.objects.filter(impartir_id=self.db.programacioDiaAnterior.pk)
        #Seleccionar controls amb un script, no sé perque no funciona de la forma habitual.
        self.selenium.execute_script('x=document.getElementById("label_id_{}-estat_0"); x.click()'.format(cas[0].pk))
        for i in range(1, len(cas)):
            self.selenium.execute_script('x=document.getElementById("label_id_{}-estat_1"); x.click()'.format(cas[i].pk))
        
        botons = self.selenium.find_elements_by_xpath("//button[@type='submit']")
        botons[0].click()
        #Comprovar que tots els controls han quedat marcats. (He posat faltes a tots)
        cas = ControlAssistencia.objects.filter(impartir_id=self.db.programacioDiaAnterior.pk)
        self.assertTrue(cas[0].estat.codi_estat=='P')
        for i in range(1, len(cas)):
            self.assertTrue(cas[i].estat.codi_estat=='F')

    def loginUsuari(self):
        self.selenium.get( self.live_server_url + '/usuaris/login/')
        #localitza usuari i paraulaDePas
        inputUser = self.selenium.find_element_by_name("usuari")
        inputUser.clear()
        inputUser.send_keys('SrProgramador')
        inputParaulaDePas = self.selenium.find_element_by_name("paraulaDePas")
        inputParaulaDePas.clear()
        inputParaulaDePas.send_keys('patata')
        botons = self.selenium.find_elements_by_xpath("//button[@type='submit']")
        boto = botons[0]
        boto.click()

    def passaLlista(self):
        self.selenium.get(self.live_server_url + '/presencia/passaLlista/' + str(self.db.sistemesDilluns.pk) + '/')
        #Obtenir tots els controls d'assistenica de l'hora marcada
        cas=ControlAssistencia.objects.filter(impartir_id=self.db.sistemesDilluns.pk)
        #Seleccionar controls amb un script, no sé perque no funciona de la forma habitual.
        for ca in cas:
            self.selenium.execute_script('x=document.getElementById("label_id_{}-estat_0"); x.click()'.format(ca.pk))
            self.selenium.execute_script('x=document.getElementById("label_id_{}-uf_0"); x.click()'.format(ca.pk))
            
        botons = self.selenium.find_elements_by_xpath("//button[@type='submit']")
        botons[0].click()

    def seleccionarAlumne(self, codiAlumne):
        #type: (int)->None
        js = """ x = document.evaluate('//input[@type=\\\'checkbox\\\' and @value="""+str(codiAlumne)+"""]', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null );
                    x.singleNodeValue.click();
                """
        self.selenium.execute_script(js)
