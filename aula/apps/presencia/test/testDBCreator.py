#encoding: utf-8
from aula.utils.testing.tests import TestUtils
from aula.apps.alumnes.models import Nivell, Curs, Grup
from aula.apps.horaris.models import DiaDeLaSetmana, FranjaHoraria, Horari
from aula.apps.assignatures.models import Assignatura, TipusDAssignatura
from aula.apps.presencia.models import Impartir, ControlAssistencia
from aula.apps.aules.models import Aula
from django.conf import settings
from datetime import date, timedelta

class TestDBCreator(object):
    '''
    Crea una BD de mostra per testejar el mòdul de presència.
    '''
    alumnes = None #type: QuerySet
    TEST_NOM_UNITAT_FORMATIVA = 'Unitat Formativa'

    def __init__(self):
        
        tUtils = TestUtils()
        
        #Crear n alumnes.
        DAM = Nivell.objects.create(nom_nivell='DAM') #type: Nivell
        primerDAM = Curs.objects.create(nom_curs='1er', nivell=DAM) #type: Curs
        primerDAMA = Grup.objects.create(nom_grup='A', curs=primerDAM) #type: Grup
        self.nAlumnesGrup = 10
        alumnes = tUtils.generaAlumnesDinsUnGrup(primerDAMA, self.nAlumnesGrup)
        self.alumnes = alumnes
        
        # Crear un profe.
        profe1=tUtils.crearProfessor('SrProgramador','patata')
        
        # Crear un horari, 
        dataDiaActual = date.today() #type: date
        #Obtenir dia laboral anterior.
        dataDiaAnterior = self.obtenirDataLaborableAnterior(dataDiaActual)
        dataDosDiesAnteriors = self.obtenirDataLaborableAnterior(dataDiaAnterior)

        #Obtenir dos dies laborals anteriors.
        diaAnterior = dataDiaAnterior.weekday()
        diaAnteriorUK = dataDiaAnterior.isoweekday()
        dosDiesAbans = dataDosDiesAnteriors.weekday()
        dosDiesAbansUK = dataDosDiesAnteriors.isoweekday()
        
        diesSetmana = ["Dilluns", "Dimarts", "Dimecres", "Dijous", "Divendres", "Dissabte", "Diumenge"]
        diesSetmana2Lletres = ["DL", "DM", "DI", "DJ", "DV", "DS", "DU"]
        
        diaSetmanaAhir = DiaDeLaSetmana.objects.create(n_dia_uk=diaAnteriorUK,n_dia_ca=diaAnterior,
            dia_2_lletres=diesSetmana2Lletres[diaAnterior],dia_de_la_setmana=diesSetmana[diaAnterior], es_festiu=False)
        diaSetmanaAbansAhir = DiaDeLaSetmana.objects.create(n_dia_uk=dosDiesAbansUK,n_dia_ca=dosDiesAbans,
            dia_2_lletres=diesSetmana2Lletres[dosDiesAbans],dia_de_la_setmana=diesSetmana[dosDiesAbans], es_festiu=False)
        tmpFH1 = FranjaHoraria.objects.create(hora_inici = '9:00', hora_fi = '10:00')
        tmpFH2 = FranjaHoraria.objects.create(hora_inici = '10:00', hora_fi = '11:00')
        tmpFH3 = FranjaHoraria.objects.create(hora_inici = '11:00', hora_fi = '12:00')

        tipusAssigUF = TipusDAssignatura.objects.create(
            tipus_assignatura=self.TEST_NOM_UNITAT_FORMATIVA)

        aula304 = Aula.objects.create(nom_aula="3.04", descripcio_aula="La 3.04")

        programacioDAM = Assignatura.objects.create(
            nom_assignatura='Programació', curs=primerDAM,
            tipus_assignatura = tipusAssigUF
        )
        
        entradaHorariProg1 = Horari.objects.create(
            assignatura=programacioDAM, 
            professor=profe1,
            grup=primerDAMA, 
            dia_de_la_setmana=diaSetmanaAhir,
            hora=tmpFH1,
            aula=aula304,
            es_actiu=True)

        entradaHorariProg2 = Horari.objects.create(
            assignatura=programacioDAM, 
            professor=profe1,
            grup=primerDAMA, 
            dia_de_la_setmana=diaSetmanaAbansAhir,
            hora=tmpFH1,
            aula=aula304,
            es_actiu=True)

        sistemesDAM = Assignatura.objects.create(
            nom_assignatura='Sistemes', 
            curs=primerDAM,
            tipus_assignatura=tipusAssigUF)

        entradaHorariSistemes1 = Horari.objects.create(
            assignatura=sistemesDAM, 
            professor=profe1,
            grup=primerDAMA, 
            dia_de_la_setmana=diaSetmanaAhir,
            hora=tmpFH2,
            aula=aula304,
            es_actiu=True)

        entradaHorariSistemes2 = Horari.objects.create(
            assignatura=sistemesDAM, 
            professor=profe1,
            grup=primerDAMA, 
            dia_de_la_setmana=diaSetmanaAhir,
            hora=tmpFH3,
            aula=aula304,
            es_actiu=True)

        #Crea controls d'assistencia
        self.estats = tUtils.generarEstatsControlAssistencia()

        #Aquí hauriem de crear unes quantes classes a impartir i provar que l'aplicació funciona correctament.
        self.programacioDiaAnterior = Impartir.objects.create(
            horari = entradaHorariProg1,
            professor_passa_llista = profe1,
            dia_impartir = dataDiaAnterior) #type: Impartir
        tUtils.omplirAlumnesHora(alumnes, self.programacioDiaAnterior)

        self.programacioDillunsHoraBuidaAlumnes = Impartir.objects.create(
            horari = entradaHorariProg2,
            professor_passa_llista = profe1,
            dia_impartir = dataDosDiesAnteriors)

        self.sistemesDiaAnterior = Impartir.objects.create(
            horari = entradaHorariSistemes1,
            professor_passa_llista = profe1,
            dia_impartir = dataDiaAnterior)     
        tUtils.omplirAlumnesHora(alumnes, self.sistemesDiaAnterior)

        self.sistemesDiaAnterior2 = Impartir.objects.create(
            horari = entradaHorariSistemes2,
            professor_passa_llista = profe1,
            dia_impartir = dataDiaAnterior)     
        tUtils.omplirAlumnesHora(alumnes, self.sistemesDiaAnterior2)


    def obtenirDataLaborableAnterior(self, dataDiaActual):
        if dataDiaActual.weekday == 0:
            dataDiaAnterior = dataDiaActual + timedelta(days=-3)
        elif dataDiaActual.weekday == 6:
            dataDiaAnterior = dataDiaActual + timedelta(days=-2)
        else:
            dataDiaAnterior = dataDiaActual + timedelta(days=-1)
        return dataDiaAnterior

