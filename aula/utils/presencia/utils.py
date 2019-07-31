from typing import Tuple
import datetime
from django.contrib.auth.models import User, AnonymousUser,AbstractUser
from aula.apps.presencia.models import Impartir, ControlAssistencia, EstatControlAssistencia
from aula.apps.usuaris.models import Professor

#definició de tipus.
Credentials = Tuple[AbstractUser,bool]

def comprovarQueLaHoraPertanyAlProfessorOError(credentials:Credentials, impartir:Impartir)->None:
    #Controlem que el profe tingui permisos per modificar la hora.
    #El profe al que li controlem els permisos és el que marquen les credencials, no el que fa la 
    #petició.
    (user, l4) = credentials
    #print ("debug", user.pk, impartir.horari.professor.pk)
    pertany_al_professor = user.pk in [impartir.horari.professor.pk, \
                                impartir.professor_guardia.pk if impartir.professor_guardia else -1]
    if not (l4 or pertany_al_professor):
        raise Exception(u"Error al modificar l'assistència del grup, el profe no és propietari de l'hora assignada")

def modificaEstatControlAssistencia( idNouEstat:int, controlAssistencia: ControlAssistencia, 
    profeQuePassaLlista: Professor, credentials: Credentials)->str:
    #Assignem les credencials de l'usuari que fa la feina retorna el codi d'estat (P,F,R,J) o blanc.
    controlAssistencia.currentUser = credentials[0]
    controlAssistencia.professor = profeQuePassaLlista
    controlAssistencia.credentials = credentials
    controlAssistencia.estat_id = idNouEstat
    controlAssistencia.save()
    if not controlAssistencia.estat:
        return ' '
    else:
        return controlAssistencia.estat.codi_estat

def modificaImpartir(impartir: Impartir, usuari: User, professor: Professor):
    #Modifica impartir segons l'usuari i professor actual. Els passo a part per evitar fer "User2Profe" cada vegada.
    impartir.dia_passa_llista = datetime.datetime.now()
    impartir.professor_passa_llista = professor
    impartir.currentUser = usuari
    impartir.save()