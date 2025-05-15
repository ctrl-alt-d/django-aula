#encoding: utf-8
"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

import urllib

from django.test import TestCase
from aula.utils.testing.tests import TestUtils
from django.contrib.auth.models import User, Group
from datetime import date, timedelta
from django.test import Client
from django.http.response import HttpResponse
from django.conf import settings

from aula.apps.alumnes.models import Alumne, Grup, Curs, Nivell
from aula.apps.usuaris.models import Professor
from aula.apps.horaris.models import Horari, DiaDeLaSetmana, FranjaHoraria
from aula.apps.assignatures.models import Assignatura
from aula.apps.presencia.models import Impartir, ControlAssistencia, EstatControlAssistencia

#typehint imports.
from django.db.models.query import QuerySet

class IControlAssistencia(ControlAssistencia):
    #Experiment per posar tipus a Python, no fer cas.
    objects = None # type: QuerySet
    
    class Meta:
        abstract = True

class PresenciaSetmanalTestCase(TestCase):
    #Ho passo tot a tests individuals, que hereden de la classe actual. Aquesta aporta les funcions comunes.
    #Així m'asseguro que cada test s'executa de forma totalment aillada.

    #Vell... abans ho feia amb TransactionTestCase, 
    # no funciona per SQLITE i ho canviat.
    #----------------------------------------------
    #Necessito el TransactionTestCase, perque torna a l'estat inicial de la BD esborrant les taules.
    #Si ho faig amb el TestCase habitual no hi poden haver subtransaccions dins el test
    #   - sempre n'hi ha perque s'executen amb ATOMIC_REQUEST (la vista acaba bé=commit, malament=rollback)
    urlBase = 'http://localhost:8000/'

    def generaBD(self):
        #Crear n alumnes.
        ESO = Nivell.objects.create(nom_nivell='ESO') #type: Nivell
        primerESO = Curs.objects.create(nom_curs='1er', nivell=ESO) #type: Curs
        self.primerESOA = Grup.objects.create(nom_grup='A', curs=primerESO) #type: Grup
        alumne = Alumne.objects.create(ralc=100, grup=self.primerESOA, 
            nom='Xevi', cognoms='Petit') #type: Alumne
        self.alumne = alumne
        alumne2 = Alumne.objects.create(ralc=100, grup=self.primerESOA, 
            nom='Joan', cognoms='Serra') #type: Alumne
        # Crear un profe.
        grupProfessors, _ = Group.objects.get_or_create(name='professors')
        grupProfessionals, _ = Group.objects.get_or_create(name='professional')
        profe1 = Professor.objects.create(username='SrCastanya', password='patata') #type: Professor
        profe1.groups.add(grupProfessors)
        profe1.groups.add(grupProfessionals)
        profe1.set_password('patata')
        profe1.save()

        profe2 = Professor.objects.create(username='SrIntrus', password='patata') #type: Professor
        profe2.groups.add(grupProfessors)
        profe2.groups.add(grupProfessionals)
        profe2.set_password('patata')
        profe2.save()

        profe3 = Professor.objects.create(username='SrTutorESOA', password='patata') #type: Professor
        profe3.groups.add(grupProfessors)
        profe3.groups.add(grupProfessionals)
        profe3.set_password('patata')
        profe3.save()

        # Crear un horari
        import datetime
        diaActual = datetime.datetime.now()
        diaAnterior = diaActual - datetime.timedelta(-1)

        tmpDS = DiaDeLaSetmana.objects.create(n_dia_uk=diaAnterior.isoweekday(),n_dia_ca=diaAnterior.weekday(),dia_2_lletres='XX',dia_de_la_setmana="dia" + str(diaAnterior.weekday()), es_festiu=False)
        tmpFH = FranjaHoraria.objects.create(hora_inici = '9:00', hora_fi = '10:00')

        matresPrimerESO = Assignatura.objects.create(nom_assignatura='Mates', curs=primerESO)
        horari = Horari.objects.create(
            assignatura=matresPrimerESO, 
            professor=profe1,
            grup=self.primerESOA, 
            dia_de_la_setmana=tmpDS,
            hora=tmpFH,
            nom_aula='x',
            es_actiu=True)

        #Aquí hauriem de crear unes quantes classes a impartir i provar que l'aplicació funciona correctament.
        diaActual = date.today() #type: date
        diaActualSetmana = diaActual.weekday()
        dillunsActual = diaActual - timedelta(diaActualSetmana)

        impartirDilluns = Impartir.objects.create(
            horari = horari,
            professor_passa_llista = profe1,
            dia_impartir = dillunsActual
        )     
        self.impartirDilluns =impartirDilluns

        estatPresent = EstatControlAssistencia.objects.create( codi_estat = 'P', nom_estat='Present' )
        EstatControlAssistencia.objects.create( codi_estat = 'F', nom_estat='Falta' )
        EstatControlAssistencia.objects.create( codi_estat = 'R', nom_estat='Retard' )
        EstatControlAssistencia.objects.create( codi_estat = 'J', nom_estat='Justificada' )

        ControlAssistencia.objects.create(
            alumne = alumne,
            estat = estatPresent,
            impartir = impartirDilluns)

        ControlAssistencia.objects.create(
            alumne = alumne2,
            impartir = impartirDilluns)

   
    def _canviEstat(self, client, estatInicial):
        #type: () => HttpResponse
        url = self.urlBase + 'presenciaSetmanal/modificaEstatControlAssistencia/{2}/{0}/{1}'.format(
            self.alumne.pk, self.impartirDilluns.pk, urllib.parse.quote(estatInicial))
        #print ("debug:::", url)
        return client.get(url) 

    def _testComprovaCanviEstat(self, client, estatInicial, estatCanviat):
        #print ("debug:", estatInicial)
        nouEstat = self._canviEstat(client, estatInicial).content.decode('utf-8')
        #print ("debug modificat:", nouEstat, estatCanviat)
        self.assertIn(estatCanviat, nouEstat)

class PresenciaSetmanalTestCaseAillament1(PresenciaSetmanalTestCase):
    
    def test_alumne_creat(self):
        self.generaBD()
        """Animals that can speak are correctly identified"""
        alumne = Alumne.objects.get(nom="Xevi")
        self.assertEqual(alumne.cognoms, 'Petit')
        
    def test_client(self):
        self.generaBD()
        c=Client()
        response = c.post('http://localhost:8000/usuaris/login/', {'usuari':'SrCastanya', 'paraulaDePas':'patata'})
        response2 = c.get('http://127.0.0.1:8000/presenciaSetmanal/' + str(self.primerESOA.pk) + '/')
        f = open('prova.html','w')
        f.write(response2.content.decode('utf-8'))
        f.close()
        self.assertNotEqual(response2.content,'')

    def test_comprovaNElementsTaula(self):
        self.generaBD()
        #Comprova que la taula fa NxM files i columnes.
        c=Client()
        response = c.post('http://localhost:8000/usuaris/login/', {'usuari':'SrCastanya', 'paraulaDePas':'patata'})
        response = c.get('http://127.0.0.1:8000/presenciaSetmanal/' + str(self.primerESOA.pk) + '/')
        contingut = response.content.decode('utf-8') #type: str

        nceles = contingut.count('class="botoMatriu"')
        #print (response.context)
        #Ha de ser igual al número d'alumnes x el número d'assignatures.
        nAlumnes = len(Alumne.objects.all())
        nAssignatures = len(Assignatura.objects.all())
        self.assertEquals(nAlumnes*nAssignatures, nceles, "El número d'elements de la taula no coincidèixen.")
    
    def test_client_nopuc_modificar_assistencia_altri(self):
        self.generaBD()
        c=Client()
        response = c.post(self.urlBase + 'usuaris/login/', {'usuari':'SrIntrus', 'paraulaDePas':'patata'})
        #Ha de donar error doncs l'usuari no pot modificar.
        #with self.assertRaises(AssertionError):
        #    self._testComprovaCanviEstat(c,'P','F')
        try:
            self._testComprovaCanviEstat(c,'P','F')
            self.fail("Error no s'ha generat excepció.")
        except AssertionError as identifier:
            pass #Tot bé.

    def test_client_nopuc_posar_tot_a_present(self):
        self.generaBD()
        #Posar totes les hores a present.
        c=Client()
        response = c.post(self.urlBase + 'usuaris/login/', {'usuari':'SrIntrus', 'paraulaDePas':'patata'})
        self._canviEstat(c, 'P')
        
        response = c.get(self.urlBase + 'presenciaSetmanal/modificaEstatControlAssistenciaGrup/P/' + str(self.impartirDilluns.pk))
        #Cal assegurar-se que NO tot els element son P.
        ca = ControlAssistencia # type: IControlAssistencia
        controls = ca.objects.filter(impartir=self.impartirDilluns.pk) # type: QuerySet
        self.assertGreater(len(controls.exclude(estat__codi_estat='P')), 0, "Hauria d'haver-hi estats no presents")

class PresenciaSetmanalTestCaseAillament2(PresenciaSetmanalTestCase):

    def test_client_modificar_control_assistencia_justifica_tothom(self):
        self.generaBD()
        with self.settings(CUSTOM_NOMES_TUTOR_POT_JUSTIFICAR=False):
            c=Client()
            c.post(self.urlBase + 'usuaris/login/', {'usuari':'SrCastanya', 'paraulaDePas':'patata'})
            self._testComprovaCanviEstat(c,'P','F')
            self._testComprovaCanviEstat(c,'F','R')
            self._testComprovaCanviEstat(c,'R','J')
            self._testComprovaCanviEstat(c,'J',' ')

class PresenciaSetmanalTestCaseAillament3(PresenciaSetmanalTestCase):

    def test_client_posar_tot_a_present(self):
        self.generaBD()
        #Posar totes les hores a present.
        c=Client()
        response = c.post(self.urlBase + 'usuaris/login/', {'usuari':'SrCastanya', 'paraulaDePas':'patata'})
        self._canviEstat(c, 'P')
        
        response = c.get(self.urlBase + 'presenciaSetmanal/modificaEstatControlAssistenciaGrup/P/' + str(self.impartirDilluns.pk))
        #Cal assegurar-se que tot els element son P.
        manager = ControlAssistencia.objects # type: QuerySet
        controls = manager.filter(impartir=self.impartirDilluns.pk) # type: QuerySet
        self.assertEqual(len(controls.exclude(estat__codi_estat='P')), 0, "Haurien de ser tots presents")
        
class PresenciaSetmanalTestCaseAillament4(PresenciaSetmanalTestCase):

    def test_client_modificar_control_assistencia(self):
        self.generaBD()
        with self.settings(CUSTOM_NOMES_TUTOR_POT_JUSTIFICAR=True):
            c=Client()
            c.post(self.urlBase + 'usuaris/login/', {'usuari':'SrCastanya', 'paraulaDePas':'patata'})
            self._testComprovaCanviEstat(c,'P','F')
            self._testComprovaCanviEstat(c,'F','R')
            self._testComprovaCanviEstat(c,'R',' ')
            self._testComprovaCanviEstat(c,' ','P')
