
# This Python file uses the following encoding: utf-8

#auth
from django.contrib.auth.decorators import login_required
from aula.apps.usuaris.models import User2Professor, User2Professional, Accio, LoginUsuari, Professional, Professor
from aula.utils.decorators import group_required

#helpers
from aula.utils import tools
from aula.utils.tools import unicode
from aula.apps.presencia.models import  ControlAssistencia
from datetime import  date
from datetime import timedelta

from aula.apps.alumnes.models import Alumne, Grup
from django.db.models import Q

@login_required
@group_required(['professors'])
def justificadorMKTable(request, year, month, day ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
    
    data = date( year = int(year), month= int(month), day = int(day) )

    q_grups_tutorats = Q( grup__in =  [ t.grup for t in professor.tutor_set.all() ] )
    q_alumnes_tutorats = Q( pk__in = [ti.alumne.pk 
                                    for ti in professor.tutorindividualitzat_set.all() ]  )
    alumnes = list( Alumne
                   .objects
                   .filter( q_grups_tutorats | q_alumnes_tutorats )
                   .order_by ('grup', 'cognoms', 'nom' ) )

    #busco el dilluns i el divendres
    dia_de_la_setmana = data.weekday()
    delta = timedelta( days = (-1 * dia_de_la_setmana ) )
    dilluns = data + delta
    dies = [ dilluns + timedelta( days = delta ) for delta in  [0,1,2,3,4] ]
    q_controls = ( Q( impartir__dia_impartir__in = dies ) &
                  Q( alumne__in = alumnes ) )
    controls = list ( ControlAssistencia
                           .objects
                           .select_related(
                                'alumne',
                                'estat', 
                                'estat_backup',
                                'impartir__horari',
                                'impartir__horari__assignatura',
                                'impartir__horari__hora',
                                'professor',
                                'professor_backup',
                             )
                           .filter( q_controls ) )
        
    #marc horari per cada dia
    dades = tools.classebuida()
    dades.alumnes =  alumnes
    dades.c = []    #controls
    
    dades.dia_hores = tools.diccionari()
    dades.marc_horari = {}
    for delta in [0,1,2,3,4]:
        dia = dilluns + timedelta( days = delta )
        diferents_hores = { control.impartir.horari.hora 
                            for control in controls
                            if control.impartir.dia_impartir == dia  }
        if (diferents_hores):
            diferents_hores_ordenat = sorted( list(diferents_hores) , key = lambda x: x.hora_inici )
            dades.dia_hores[dia] = tools.llista( diferents_hores_ordenat )
            dades.marc_horari[dia] = { 'desde':diferents_hores_ordenat[0],'finsa':diferents_hores_ordenat[-1]}        
        
    dades.quadre = tools.diccionari()
    
    for alumne in dades.alumnes:

        dades.quadre[unicode(alumne)] = []
        for dia, hores in dades.dia_hores.itemsEnOrdre():
            hora_inici = dades.marc_horari[dia]['desde']
            controls_alumne = [ control for control in controls
                           if control.impartir.dia_impartir == dia  and
                              control.alumne == alumne ]
            for hora in hores:
                cella = tools.classebuida()
                cella.txt = ''
                controls_alumne_hora =  [ c for c in controls_alumne if c.impartir.horari.hora == hora]
                hiHaControls = bool( controls_alumne_hora )
                haPassatLlista = hiHaControls and bool( [ c for c in controls_alumne_hora 
                                                         if c.estat is not None ] )
                cella.c = [ c for c in controls_alumne_hora]
                for item in cella.c:
                    item.professor2show = item.professor or ( item.impartir.horari.professor if item.impartir.horari else ' ' ) 
                    item.estat2show= item.estat or " "
                dades.c.extend(cella.c)
                if not hiHaControls:
                    cella.color = '#505050'
                else:
                    if not haPassatLlista:
                        cella.color = '#E0E0E0'
                    else:
                        cella.color = 'white'
                if hora == hora_inici:
                    cella.primera_hora = True
                else:
                    cella.primera_hora = False
                dades.quadre[unicode(alumne)].append( cella )

    return dades    
    