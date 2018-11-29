# This Python file uses the following encoding: utf-8


PASSAR_LLISTA_GRUP_NO_MEU = u"""Has passat llista a un grup que no és el teu: ({0}).
El professor del grup {1} rebrà un missatge com aquest."""

HAN_PASSAT_LLISTA_PER_MI = u"""Ha passat llista d'una classe on consta que la fas tú: ({0})."""

FI_PROCES_AFEGIR_ALUMNES = u"""Fi procés afegir alumnes a {0}"""

FI_PROCES_AFEGIR_ALUMNES_AMB_ERRORS = u"""Fi procés afegir alumnes a {0} amb errors"""


MISSATGES = {'ADMINISTRACIO' : {PASSAR_LLISTA_GRUP_NO_MEU,
                                FI_PROCES_AFEGIR_ALUMNES,
                                FI_PROCES_AFEGIR_ALUMNES_AMB_ERRORS,
                                HAN_PASSAT_LLISTA_PER_MI,
                                },

             'DISCIPLINA': {},
             'MISSATGERIA': {},
             'ACTIVITATS': {},
             'INFORMATIVES_DISCIPLINA': {},}