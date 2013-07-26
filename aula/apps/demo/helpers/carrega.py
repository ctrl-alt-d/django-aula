# -*- coding: utf-8 -*-
import os
from aula.apps.demo.helpers.alumnes import generaFitxerSaga
from aula.apps.demo.helpers.horaris import generaFitxerKronowin

def fesCarrega( ):
    fitxerSaga = os.path.join( os.path.dirname(__file__), '../tmp/exportSaga.txt')
    fitxerKronowin = os.path.join( os.path.dirname(__file__), '../tmp/exportKrono.txt')
    
    nivellsCursosGrups = ( 
                            ( 'ESO', 
                              (
                                 ( 1, ( 'A','B','C'), ),
                                 ( 2, ( 'A','B',), ),
                                 ( 3, ( 'A','B',), ),
                              ),
                            ),
                            ( 'INF',
                              (
                                  ( 1, ( 'A',), ),
                                  ( 2, ( 'A',), ),
                              ),
                            ),
                            ( 'ADM',
                              (
                                  ( 1, ( 'A','B'), ),
                                  ( 2, ( 'A',), ),
                              ),
                            ),
                         )
                          
    generaFitxerSaga(fitxerSaga, nivellsCursosGrups  )
    generaFitxerKronowin( fitxerKronowin, nivellsCursosGrups, nivellsMatins=['ESO',], frangesMatins = range(1,5), frangesTardes  = range(6,10) )