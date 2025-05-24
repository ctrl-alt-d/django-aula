#encoding: utf-8
# Utilitats compartides per fer testing.

from aula.apps.usuaris.models import Professor, Group
from aula.apps.alumnes.models import Grup, Alumne
from aula.apps.presencia.models import EstatControlAssistencia, Impartir, ControlAssistencia
from aula.apps.horaris.models import FranjaHoraria
from typing import List, Dict, Union
from datetime import date, time, datetime, timedelta
from django.conf import settings
from django.test import LiveServerTestCase

import random

class TestUtils():

    diesSetmana = ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte", "Diumenge"]
    diesSetmana2Lletres = ["DL", "DM", "DI", "DJ", "DV", "DS", "DU"]
    
    def crearProfessor(self, nomUsuari, passwordUsuari, mail="mail@mailserver.com"):
    # type:(str, str) -> Professor
        grupProfessors, _ = Group.objects.get_or_create(name='professors')
        grupProfessionals, _ = Group.objects.get_or_create(name='professional')
        profe1 = Professor.objects.create(username=nomUsuari, password=passwordUsuari) #type: Professor
        profe1.groups.add(grupProfessors)
        profe1.groups.add(grupProfessionals)
        profe1.set_password(passwordUsuari)
        profe1.first_name = nomUsuari
        profe1.last_name = "cognom_" + nomUsuari
        profe1.email = mail
        profe1.save()
        
        return profe1

    def generaAlumnesDinsUnGrup(self, grupAlumnes, nAlumnesAGenerar):
        #type:(Grup,int) -> List[Alumne]
        noms = [u'Xevi',u'Joan',u'Pere',u'Lluís',u'Brandom',u'Maria',u'Lola',u'Azucena']
        cognoms = [u'Serra',u'Vazquez',u'García',u'Moreno',u'Vila',u'Vilamitjana']
        alumnesGenerats = [] #type: List[Alumne]
        
        if nAlumnesAGenerar > (len(noms)*len(cognoms)):
            raise Exception("Error no pots generar tants alumnes, sortirien repetits.")

        nCognom = 0
        nNom = 0
        for i in range(0,nAlumnesAGenerar):
            alumne = Alumne.objects.create(ralc=100, grup=grupAlumnes, 
                nom=noms[nNom], 
                cognoms=cognoms[nCognom], 
                data_neixement=date(1990,7,7) #english date.
                ) 
            alumnesGenerats.append(alumne)
            nNom+=1
            if nNom == len(noms):
                nCognom+=1
                nNom = 0
        return alumnesGenerats
        
    def generarEstatsControlAssistencia(self):
        #type: ()->Dict[str, EstatControlAssistencia]
        estats = {} #type: Dict[str, EstatControlAssistencia]
        estats['p'] = EstatControlAssistencia.objects.create( codi_estat = 'P', nom_estat='Present' )
        estats['f'] = EstatControlAssistencia.objects.create( codi_estat = 'F', nom_estat='Falta' )
        estats['r'] = EstatControlAssistencia.objects.create( codi_estat = 'R', nom_estat='Retard' )
        estats['j'] = EstatControlAssistencia.objects.create( codi_estat = 'J', nom_estat='Justificada' )
        return estats

    def omplirAlumnesHora(self,alumnes, horaAImpartir):
        #type: (List[Alumne], Impartir)->Any
        for alumne in alumnes:
            ControlAssistencia.objects.create(
                alumne = alumne,
                impartir = horaAImpartir)

    @staticmethod
    def llancaPostMortem():
        import ipdb, sys, traceback
        extype, value, tb = sys.exc_info()
        traceback.print_exc()
        ipdb.post_mortem(tb)

class SeleniumLiveServerTestCase(LiveServerTestCase):
    #Classe porqueria per tal que funcionin les traces en el codi de selenium.
    #Altrament no et dona els settings i és complicat.
    def __init__(self, *args, **kwargs):
        super(SeleniumLiveServerTestCase, self).__init__(*args, **kwargs)
        if settings.DEBUG == False:
            settings.DEBUG = True
