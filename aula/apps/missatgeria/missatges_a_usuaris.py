# This Python file uses the following encoding: utf-8


PASSAR_LLISTA_GRUP_NO_MEU = u"""Has passat llista a un grup que no és el teu: ({0}).
El professor del grup {1} rebrà un missatge com aquest."""

HAN_PASSAT_LLISTA_PER_MI = u"""Ha passat llista d'una classe on consta que la fas tú: ({0})."""

FI_PROCES_AFEGIR_ALUMNES = u"""Fi procés afegir alumnes a {0}"""

FI_PROCES_AFEGIR_ALUMNES_AMB_ERRORS = u"""Fi procés afegir alumnes a {0} amb errors"""

EXPULSIO_PER_ACUMULACIO_INCIDENCIES = u"""A l'alumne {0} ja li has posat {1} incidències en els darrers {2} dies. 
                        Segons la normativa del Centre hauries de tramitar 
                        una expulsió per acumulació d'incidències."""

EXPULSIO_PER_ACUMULACIO_INCIDENCIES_FORA_AULA = u"""A l'alumne {0} li han posat {1} incidències gestionades pel tutor en els darrers {2} dies. 
                        Segons la normativa del Centre, com a tutor de l'alumne, hauries de tramitar 
                        una expulsió per acumulació d'incidències."""

INCIDENCIA_INFORMATIVA = u"""Ha posat una incidència {0}a {1} ({2}) el dia {3}. 
                            El text de la incidència és: {4}"""

MISSATGES = {'ADMINISTRACIO' : {'warning': {PASSAR_LLISTA_GRUP_NO_MEU,
                                FI_PROCES_AFEGIR_ALUMNES,
                                FI_PROCES_AFEGIR_ALUMNES_AMB_ERRORS,
                                HAN_PASSAT_LLISTA_PER_MI,
                                }},
             'DISCIPLINA': {'danger': {EXPULSIO_PER_ACUMULACIO_INCIDENCIES,
                                       EXPULSIO_PER_ACUMULACIO_INCIDENCIES_FORA_AULA,}},
             'MISSATGERIA': {'info': {}},
             'ACTIVITATS': {'success': {}},
             'INFORMATIVES_DISCIPLINA': {'primary': {INCIDENCIA_INFORMATIVA,}},}


def tipusMissatge(missatge):
    for tipus, valors in MISSATGES.iteritems():
        for estat,frases in valors.iteritems():
            if missatge in frases:
                return tipus
    return None