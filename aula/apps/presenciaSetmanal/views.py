# This Python file uses the following encoding: utf-8
import datetime
from django.shortcuts import  render
from django.http import HttpResponse
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.utils.datetime_safe import date
from aula.apps.usuaris.models import User2Professor, Accio
from collections import OrderedDict
from django.conf import settings

#auth
from django.contrib.auth.decorators import login_required
from aula.utils.tools import getImpersonateUser
from aula.utils.decorators import group_required

#Models
from aula.apps.presencia.models import Impartir, ControlAssistencia, EstatControlAssistencia
from aula.apps.presenciaSetmanal.forms import EscollirGrupForm
from aula.apps.alumnes.models import Grup

CONST_ERROR_CODE = '_'

class ProfeNoPot(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None
    
    def __str__(self):
        if self.message:
            return self.message
        else:
            return 'ProfeNoPot: No correspon professor a l\'horari'

#Veure els grups disponibles.
@login_required
@group_required(['professors'])
def index(request):

    #Obtenir l'usuari actual.
    credentials = getImpersonateUser(request)
    (user, _ ) = credentials
    professor = User2Professor( user )
    
    if request.method == 'POST':
        form = EscollirGrupForm(professor, request.POST)
        if form.is_valid():
            grup=form.cleaned_data['grup_list']
            nomesPropies=form.cleaned_data['nomesPropies']
            if nomesPropies: nomesPropies='True'
            else: nomesPropies='False'
            return detallgrup(request, grup.id, dataReferenciaStr='', nomesPropies=nomesPropies)
    else:
        form = EscollirGrupForm(professor)
    return render(
                request,
                'form.html', 
                {'form': form, 
                 },
                )

@login_required
@group_required(['professors'])
def detallgrup(request, grup_id, dataReferenciaStr='', nomesPropies=None):
    '''
    Veure els alumnes que entren dins les hores d'un grup i permetre modificar-ne l'estat.
    :param request:
    :param grup_id: El grup
    :param string dataReferenciaStr:La data de referència a partir de la qual tindrem la setmana.
    :return:
    '''
    #Obtenir l'usuari actual.
    credentials = getImpersonateUser(request)
    (user, _ ) = credentials
    professor = User2Professor( user )
    
    grup = Grup.objects.get(id=grup_id)

    dataRef = date.today()
    if (len(dataReferenciaStr) != 0):
        dataPython = datetime.datetime.strptime(dataReferenciaStr, '%Y%m%d')
        dataRef = date(year=dataPython.year, month=dataPython.month, day=dataPython.day)

    dillunsSetmana = dataRef + datetime.timedelta(days=-dataRef.weekday())
    #4 és el divendres 0,1,2,3,4 (5é dia)
    divendresSetmana = dataRef + datetime.timedelta(days=4-dataRef.weekday())
    
    nextDate = dataRef + datetime.timedelta(days=7)
    previousDate = dataRef - datetime.timedelta(days=7)
    
    #Consultar els estats del control d'assistencia
    estats = LlistaEstats()

    # Llista amb els alumnes que el professor té al control d'assistència en aquest grup.
    llalumnes=ControlAssistencia.objects.filter(
        impartir__horari__grup_id=grup_id,
        impartir__horari__professor_id=professor,
        impartir__dia_impartir__range=[dillunsSetmana, divendresSetmana],
        ).values('alumne')

    #Expresssio per consultar els l'assistencia dels alumnes entre una data d'inici i una data de fi.
    '''sqlExpr = \
        str('SELECT alumnes_alumne.id as id_alumne, presencia_impartir.id as id_hora, ' +
            'presencia_controlassistencia.estat_id as estat_id, ' +
            'presencia_controlassistencia.id, alumnes_alumne.nom as nom_alumne, alumnes_alumne.cognoms as cognoms_alumne ' +
            'FROM presencia_controlassistencia, alumnes_alumne, presencia_impartir, ' +
            'horaris_horari, horaris_diadelasetmana, horaris_franjahoraria ' +
            'WHERE alumnes_alumne.id = alumne_id AND ' +
            'presencia_controlassistencia.impartir_id = presencia_impartir.id AND ' +
            'presencia_impartir.horari_id = horaris_horari.id ' +
            'AND horaris_horari.dia_de_la_setmana_id = horaris_diadelasetmana.id AND ' +
            'horaris_horari.hora_id = horaris_franjahoraria.id AND ' +
            'presencia_impartir.dia_impartir >= "' + dillunsSetmana.isoformat() + '" AND ' +
            'presencia_impartir.dia_impartir <= "' + divendresSetmana.isoformat() + '" AND ' +
            'horaris_horari.grup_id = ' + grup_id + ' ' +
            'ORDER BY alumnes_alumne.cognoms, horaris_diadelasetmana.n_dia_ca, horaris_franjahoraria.hora_inici')

    assistencies = ControlAssistencia.objects.raw(sqlExpr)
    '''

    if nomesPropies is not None and nomesPropies=='True':
        # Selecciona totes les assistències dels alumnes amb aquest professor
        assistencies=ControlAssistencia.objects.filter( 
            impartir__horari__professor_id=professor,
            impartir__dia_impartir__range=[dillunsSetmana, divendresSetmana],  
            alumne_id__in=llalumnes,
        ).order_by('alumne__cognoms', 'impartir__horari__dia_de_la_setmana__n_dia_ca', 'impartir__horari__hora__hora_inici')
    else:
        # Selecciona totes les assistències dels alumnes encara que no siguin del professor
        assistencies=ControlAssistencia.objects.filter( 
            impartir__dia_impartir__range=[dillunsSetmana, divendresSetmana],  
            alumne_id__in=llalumnes,
        ).order_by('alumne__cognoms', 'impartir__horari__dia_de_la_setmana__n_dia_ca', 'impartir__horari__hora__hora_inici')

    #Selecciona les hores de les assistències trobades
    hores = Impartir.objects.filter(
        pk__in=assistencies.values('impartir')).order_by(
            'horari__dia_de_la_setmana__n_dia_ca', 'horari__hora__hora_inici')
    

    # mah = Matriu alumnes, hores.
    mah = {}
    # dAlumnes diccionari d'alumnes
    dAlumnes = {}

    #Explorar les assistències i anotar-les a la matriu de diccionaris mah.
    #Determinar els alumnes que han d'aparèixer i anotar-los al diccionari dAlumnes.
    nAssistencies = 0
    for assistencia in assistencies:
        idAlumne = assistencia.alumne.id
        idHora = assistencia.impartir.id
        idEstat = 0
        #Estat zero equival a none. Millor aixi pel tema Javascript. Estats numerics.
        if (assistencia.estat != None):
            idEstat = assistencia.estat.id
            #print("Estat", idEstat, "idAlumne", idAlumne, "idHora", idHora)

        if ( mah.get(str(idAlumne),None) == None):
            #print "\nidAlumne que no esta al grup:" + str(idAlumne) + "idHora" + str(idHora) + \
            #            "estat:" + str(assistencia.estat_id)
            mah[str(idAlumne)]={}
            dAlumnes[str(idAlumne)] = AlumneMemoria(idAlumne, assistencia.alumne.nom, assistencia.alumne.cognoms)

        mah[str(idAlumne)][str(idHora)] = AssistenciaAlumne(idEstat, idAlumne, idHora, estats)
        nAssistencies = nAssistencies + 1

    #print "NRegistres consulta: " + str(nAssistencies)
    # Llista ordenada d'alumnes per cognom.
    alumnes = sorted(dAlumnes.values(), key=lambda x: x.cognoms.lower())
    
    #Preparar la matriu de visualitzacio, cada cela una hora x alumne.
    i = 0
    mvisualitza = []
    for i in range(0, len(alumnes)):
        #Crea un nou sub-diccionari per cada alumne.
        mvisualitzafila = []
        for j in range(0, len(hores)):
            #Posem els valors
            alumn: AlumneMemoria = alumnes[i]
            idAlumne = str(alumn.id)
            idHora = str(hores[j].id)

            horesXAlumne: dict = mah[idAlumne]
            #import ipdb; ipdb.set_trace()
            if (not idHora in horesXAlumne):
                mvisualitzafila.append(None)
                #print ("..." + str(idAlumne) + ":" + str(idHora))
            else:
                #print (str(idAlumne) + ":" + str(idHora))
                mvisualitzafila.append(mah[idAlumne][idHora])
        mvisualitza.append(mvisualitzafila)


    #Diccionari de dies, per un dia el nombre d'aparicions dins el vector.
    ddies = _recompteHores(hores)

    #assert False, ddies
    context ={
        'mvisualitza': mvisualitza,
        'ddies': ddies,
        'hores': hores,
        'alumnes': alumnes,
        'next_date': nextDate.strftime('%Y%m%d'),
        'previous_date': previousDate.strftime('%Y%m%d'),
        'monday_date': dillunsSetmana.strftime('%d/%m/%Y'),
        'grup': grup,
        'nomesPropies':nomesPropies}

    return render(request, 'presenciaSetmanal/detallgrup.html', context)

@login_required
@group_required(['professors'])
def modificaEstatControlAssistencia(request, codiEstat, idAlumne, idImpartir):
    '''
    Modifica el control d'assistència d'un sol resistre.
    '''
    try:
        profeActual = User2Professor( request.user )
        credentials = getImpersonateUser(request) 
        (user, l4) = credentials   

        estats = LlistaEstats()
        segEstat = estats.obtenirSeguentEstatAPartirCodi(codiEstat)
        if (settings.CUSTOM_NOMES_TUTOR_POT_JUSTIFICAR):
            #Si el profe convencional no pot justificar ens saltem un estat
            #TODO: Només podem justificar si som tutor del grup.
            if segEstat.codi == 'J':
                segEstat = estats.obtenirSeguentEstatAPartirCodi(segEstat.codi)

        #Comprovar que sigui el profe assignat a l'hora o error.
        impartir = Impartir.objects.get(id=idImpartir)
        
        #Controlem que el profe tingui permisos per modificar la hora.
        _comprovarQueLaHoraPertanyAlProfessorOError(credentials, impartir)

        ca = ControlAssistencia.objects.get(impartir_id=idImpartir, alumne_id=idAlumne)
        codiResultat = _modificaEstatControlAssistencia(
            segEstat, ca, profeActual, user, credentials)

        #Actualitzar el control impartir.
        impartir.dia_passa_llista = datetime.datetime.now()
        impartir.professor_passa_llista = profeActual
        impartir.currentUser = user
        impartir.save()

        #Log
        Accio.objects.create(
            tipus='PL',
            usuari=user,
            l4=l4,
            impersonated_from=request.user if request.user != user else None,
            text=u"""Passar llista, presenciaSetmanal: {0}.""".format(impartir)
        )

        #print ("Retorno correctament ", codiResultat)
        return HttpResponse(codiResultat)
    except ValidationError as e:
        cadenaError = u''
        for v in e.message_dict[NON_FIELD_ERRORS]:
            cadenaError += str(v) + u"<br>"
        return HttpResponse(CONST_ERROR_CODE + cadenaError, status=500)
    except ProfeNoPot as e:
        return HttpResponse(CONST_ERROR_CODE + str(e), status=200)
    except Exception as e:
        #print (CONST_ERROR_CODE, str(traceback.format_exc()))
        #return HttpResponse(CONST_ERROR_CODE + unicode(e) + u"-" + unicode(traceback.format_exc(), 'utf-8'))
        return HttpResponse(CONST_ERROR_CODE + str(e), status=500)


@login_required
@group_required(['professors'])
def modificaEstatControlAssistenciaGrup(request, codiEstat, idImpartir):
    '''
    Modifica el control d'assistència de tot un grup.
    '''
    llistaAlumnes=''
    try:
        profeActual = User2Professor( request.user )
        credentials = getImpersonateUser(request) 
        (user, l4) = credentials   
        
        #Comprovar que sigui el profe assignat a l'hora o error.
        impartir = Impartir.objects.get(id=idImpartir)
        
        #Controlem que el profe tingui permisos per modificar la hora.
        _comprovarQueLaHoraPertanyAlProfessorOError(credentials, impartir)
        
        assistencies = impartir.controlassistencia_set.order_by('alumne')
        estats = LlistaEstats()
        nouEstat = estats.obtenirEstatActualAPartirCodi(codiEstat)
        
        for assistencia in assistencies:
            if (llistaAlumnes != ''):
                llistaAlumnes = llistaAlumnes + u','
            _modificaEstatControlAssistencia(nouEstat, assistencia, \
                profeActual, user, credentials)
            llistaAlumnes = llistaAlumnes + str(assistencia.alumne_id)

        #Actualitzar el control impartir.
        impartir.dia_passa_llista = datetime.datetime.now()
        impartir.professor_passa_llista = profeActual
        impartir.currentUser = user
        impartir.save()

        #Log
        Accio.objects.create(
            tipus='PL',
            usuari=user,
            l4=l4,
            impersonated_from=request.user if request.user != user else None,
            text=u"""Passar llista, presenciaSetmanal: {0}.""".format(impartir)
        )
        return HttpResponse(llistaAlumnes)
    except ValidationError as e:
        cadenaError = u''
        for v in e.message_dict[NON_FIELD_ERRORS]:
            cadenaError += str(v) + u"<br>"
        return HttpResponse(CONST_ERROR_CODE + cadenaError, status=500)
    except ProfeNoPot as e:
        return HttpResponse(CONST_ERROR_CODE + str(e), status=200)
    except Exception as e:
        #print (CONST_ERROR_CODE, str(traceback.format_exc()))
        return HttpResponse(CONST_ERROR_CODE + str(e), status=500)       
#        return HttpResponse(CONST_ERROR_CODE + unicode(e) + u"-" + unicode(traceback.format_exc(), 'utf-8'))


def _modificaEstatControlAssistencia(nouEstat, controlAssistencia, profeActual, user, credentials):
    #type: (Estat, ControlAssistencia, Professor, User ,tuple) -> int
    #Assignem les credencials de l'usuari que fa la feina.
    controlAssistencia.currentUser = user
    controlAssistencia.professor = profeActual
    controlAssistencia.credentials = credentials
    controlAssistencia.estat_id = nouEstat.getIdOrNone()
    controlAssistencia.save()
    if not controlAssistencia.estat:
        return ' '
    else:
        return controlAssistencia.estat.codi_estat
    

def _comprovarQueLaHoraPertanyAlProfessorOError(credentials, impartir):
    (user, l4) = credentials
    pertany_al_professor = user.pk in [impartir.horari.professor.pk, \
                                impartir.professor_guardia.pk if impartir.professor_guardia else -1]
    if not (l4 or pertany_al_professor):
        raise ProfeNoPot(u"Error al modificar l'assistència del grup, el profe no és propietari de l'hora assignada")


#Realitza el recompte d'hores per cada dia.
def _recompteHores(hores):

    ddies={}
    if (len(hores) > 0):
        diaAnt = hores[0].dia_impartir

        for hora in hores:
            if diaAnt == hora.dia_impartir:
                if diaAnt not in ddies.keys():
                    ddies[diaAnt] = 1
                else:
                    ddies[hora.dia_impartir] = ddies[hora.dia_impartir] + 1
            else:
                ddies[hora.dia_impartir] = 1
            diaAnt = hora.dia_impartir

    return OrderedDict(sorted(ddies.items(), key=lambda t: t[0]))


class AssistenciaAlumne:
    """
    Classe per representar una casella del tauler d'assistencia.
    """
    idHora = 0
    idAlumne = 0
    idEstat = 0
    estats = None

    CODI_ESTAT_NUL = ' '

    def __init__(self, idEstat, idAlumne, idImpartir, estats):
        """
        :param idEstat:
        :param idAlumne:
        :param idImpartir:
        :param estats: LlistaEstats
        :type estats LlistaEstats
        """
        self.idEstat = idEstat
        self.idImpartir = idImpartir
        self.idAlumne = idAlumne
        self.estats = estats

    def getStringRepr(self):
        return str(self.idAlumne) + "_" + str(self.idImpartir)

    def getStringCommaSepValues(self):
        return str(self.idAlumne) + "," + str(self.idImpartir)

    def getColor(self):
        nomColor = "transparent"
        nomEstat = self.getNomEstat()
        if (nomEstat == 'P'):
            nomColor = "green"
        elif (nomEstat == 'F'):
            nomColor = "red"
        elif (nomEstat == 'J'):
            nomColor = "blue"
        elif (nomEstat == 'R'):
            nomColor = "orange"
        return nomColor

    def getNomEstat(self):
        estat = self.CODI_ESTAT_NUL
        if (self.idEstat != 0):
            estat = self.estats.obtenirCodiAPartirIdEstat(self.idEstat)
            #estat = self.estats.filter(id=self.idEstat)[0].codi_estat
        return estat

    def __str__(self):
        return self.getNomEstat()

class Estat:
    '''
    Classe estat, representa un estat a la BD.
    '''
    id = 0
    codi = 0

    def __init__(self, id, codi):
        self.id = id
        self.codi = codi

    def getIdOrNone(self):
        if (self.id == 0):
            return None
        else:
            return self.id

    def __str__(self):
        return self.codi

class LlistaEstats:
    llistaEstats = []

    def __init__(self):
        """
        Obté una llista d'estats de la BD.
        És el mateix que el model però amb un estat null.
        """

        self.llistaEstats.append(Estat(0, ' '))
        estats = EstatControlAssistencia.objects.all()
        i = 0
        while i < len(estats):
            self.llistaEstats.append(Estat(estats[i].id, estats[i].codi_estat))
            i = i + 1

    def obtenirCodiAPartirIdEstat(self, idEstat):
        """
        Cerca un estat a partir del seu codi.
        TODO: Que tal un diccionari per fer la cerca.
        :param idEstat:
        :return:
        """

        indexEstatTrobat = -1
        i = 0
        while i < len(self.llistaEstats) and indexEstatTrobat == -1:
            if (self.llistaEstats[i].id == idEstat):
                indexEstatTrobat = i
            i = i + 1

        codiTrobat = ''
        if (indexEstatTrobat != -1):
            codiTrobat = self.llistaEstats[indexEstatTrobat].codi
        return codiTrobat

    def obtenirEstatActualAPartirCodi(self, codi):
        # type: (Any) -> Estat
        """
        Cerca l'estat actual a partir del seu codi.
        :param string codi: El codi de l'estat F P J...
        :return Estat:
        """
        indexEstatTrobat = -1
        i = 0
        while i < len(self.llistaEstats) and indexEstatTrobat == -1:
            #print str(estats[i].id) + ", " + str(idEstat)
            if (str(self.llistaEstats[i].codi) == str(codi)):
                indexEstatTrobat = i
            i = i + 1

        if indexEstatTrobat != -1:
            estat = self.llistaEstats[indexEstatTrobat]
        else:
            estat = None
        return estat

    def obtenirSeguentEstatAPartirCodi(self, codi):
        """
        Obté el següent estat a partir d'un codi donat F, P, ...
        TODO:Reaprofitar codi de l'anterior funció per fer aquésta
        :param string codi: Codi donat F, P, ...
        :return: Valor de retorn un estat
        :rtype: Estat
        """

        indexEstatTrobat = -1
        i = 0
        while i < len(self.llistaEstats) and indexEstatTrobat == -1:
            #print str(estats[i].id) + ", " + str(idEstat)
            if (str(self.llistaEstats[i].codi) == str(codi)):
                indexEstatTrobat = i
            i = i + 1

        if indexEstatTrobat != -1:
            indexNouEstat = indexEstatTrobat + 1
            if indexNouEstat >= len(self.llistaEstats):
                indexNouEstat = 0
            estat = self.llistaEstats[indexNouEstat]
        else:
            #Tornem el primer estat disponible.
            raise Exception("Error no existeix l'estat a cercar.")

        return estat

#Classe alumne en memòria.
class AlumneMemoria:
    id = 0
    nom = ''
    cognoms = ''

    def __init__(self, id, nom, cognoms):
        self.id = id
        self.nom = nom
        self.cognoms = cognoms

    def __lt__(self, other):
        """
        :type other: AlumneMemoria
        :return: int
        """
        return self.cognoms < other.cognoms

    def __str__(self):
        return self.cognoms + ' ' + self.nom

