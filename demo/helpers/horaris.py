# -*- coding: utf-8 -*- 

import random
import csv
from aula.utils.tools import unicode
from os.path import exists

def generaFitxerKronowin( path, nivellsCursosGrups, nivellsMatins, frangesMatins, frangesTardes, override ):
    # Format:
    # 'assignatura', 'professor', 'grup', 'mati_tarda', 'nivell', 'curs', 'lletra', 'aula', 'unk2', 'dia', 'franja', 'unk3' )
    # "TUVP";"DIDV";;;;;;;;4,00;5,00;1,00
    # "TE";"TEJC";"E3D";"M";"ESO";"3";"D";"209";;1,00;1,00;1,00

    fileexists = exists(path)
    if (not override and fileexists):
        return

    horaris_matins = generaHoraris( [ g for g in nivellsCursosGrups if g[0] in nivellsMatins ],  frangesMatins, 'M')
    horaris_tardes = generaHoraris( [ g for g in nivellsCursosGrups if g[0] not in nivellsMatins ],  frangesTardes, 'T')
    
    with open(path, 'w') as csvfile:
        spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        for row in horaris_matins + horaris_tardes:
            #utfrow = [ unicode(s).encode("utf-8") for s in row ]
            spamwriter.writerow( row )    
    
def generaHoraris( nivellsCursosGrups, franges, mati_tarda):
    rows = []
    
    assignatures = None
    if mati_tarda == 'M':
        assignatures = ( 'MA', 'OP2', 'FI', 'TEC', 'GYM', 'TUT', 'OP1')
    else:
        assignatures = ( 'TUT', 'UF9', 'UF1', 'UF2', 'UF3', 'UF4', 'UF5', 'UF6')
    
    tots_els_grups = []
    for nivell, GrupsCursos in nivellsCursosGrups:
        for curs, Grups in GrupsCursos:
            for grup in Grups:
                tots_els_grups.append( u"{nivell}{curs}{grup}".format( nivell = nivell, grup = grup, curs = curs)     ) 
    
    n_profes_calen = len( tots_els_grups ) + 1
    
    professors = [  "{0}{1}".format( mati_tarda, n_professor) for n_professor in range( n_profes_calen ) ]
    
    for dia_setmana in range(1,6):
        for franja in franges:
            aux_professors = professors
            random.shuffle( aux_professors )
            aux_professors2, professor_g = aux_professors[:-1], aux_professors[-1]
            random.shuffle( tots_els_grups )
            professors_grups = zip( aux_professors2, tots_els_grups )
            for professor_grup in professors_grups:
                row = ( 
                       #'assignatura',
                       random.choice( assignatures ),   
                       #'professor', 
                       professor_grup[0],
                       #'grup', 
                       professor_grup[1], 
                       #'mati_tarda', 
                       mati_tarda,
                       #'nivell', 
                       professor_grup[1][:3],
                       #'curs', 
                       professor_grup[1][3:4],
                       #'lletra', 
                       professor_grup[1][-1:],
                       #'aula', 
                       random.randint(100,400),
                       #'unk2',
                       u"unk2", 
                       #'dia',
                       dia_setmana, 
                       #'franja', 
                       franja,
                       #'unk3'
                       u'unk3'
                       )
                rows.append( row  )
            row = ( 
                   #'assignatura',
                   'G',   
                   #'professor', 
                   professor_g,
                   #'grup', 
                   "", 
                   #'mati_tarda', 
                   mati_tarda,
                   #'nivell', 
                   "",
                   #'curs', 
                   "",
                   #'lletra', 
                   "",
                   #'aula', 
                   "",
                   #'unk2',
                   u"unk2", 
                   #'dia',
                   dia_setmana, 
                   #'franja', 
                   franja,
                   #'unk3'
                   u'unk3'
                   )
            rows.append( row  )                
    return rows
        




    