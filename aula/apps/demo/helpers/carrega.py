# -*- coding: utf-8 -*-
import os
from aula.apps.demo.helpers.alumnes import generaFitxerSaga

def fesCarrega( ):
    fitxerSaga = os.path.join( os.path.dirname(__file__), '../tmp/exportSaga.txt')
    
    nivellsCursosGrups = ( 
                            ( 'ESO', 
                              (
                                 ( 3, ( 'A','B',), ),
                              ),
                            ),
                            ( 'INF',
                              (
                                  ( 1, ( 'A',), ),
                                  ( 2, ( 'A',), ),
                              ),
                            )
                         )
                          
    generaFitxerSaga(fitxerSaga, nivellsCursosGrups  )