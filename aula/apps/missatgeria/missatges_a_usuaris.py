# This Python file uses the following encoding: utf-8


PASSAR_LLISTA_GRUP_NO_MEU = u"""Has passat llista a un grup que no és el teu: ({0}).
El professor del grup {1} rebrà un missatge com aquest."""

HAN_PASSAT_LLISTA_PER_MI = u"""Ha passat llista d'una classe on consta que la fas tú: ({0})."""

FI_PROCES_AFEGIR_ALUMNES = u"""Fi procés afegir alumnes a {0}"""

FI_PROCES_TREURE_ALUMNES = u'Fi procés treure alumnes a {0}'

FI_PROCES_TREURE_ALUMNES_AMB_ERRORS = u'Fi procés treure alumnes a {0} amb errors'

FI_PROCES_AFEGIR_ALUMNES_AMB_ERRORS = u"""Fi procés afegir alumnes a {0} amb errors"""

EXPULSIO_PER_ACUMULACIO_INCIDENCIES = u"""A l'alumne {0} ja li has posat {1} incidències en els darrers {2} dies. 
                        Segons la normativa del Centre hauries de tramitar 
                        una expulsió per acumulació d'incidències."""

EXPULSIO_PER_ACUMULACIO_INCIDENCIES_FORA_AULA = u"""A l'alumne {0} li han posat {1} incidències gestionades pel tutor en els darrers {2} dies. 
                        Segons la normativa del Centre, com a tutor de l'alumne, hauries de tramitar 
                        una expulsió per acumulació d'incidències."""

INCIDENCIA_INFORMATIVA = u"""Ha posat una incidència {0}a {1} ({2}) el dia {3}. 
                            El text de la incidència és: {4}"""

CONSERGERIA_A_TUTOR = u'''Missatge relatiu a un teu alumne tutorat'''

CONSERGERIA_A_CONSERGERIA = u'''Enviat avís a tutors de l'alumne {0} ({1}). El text de l'avís és: "{2}"'''

AVIS_ABSENCIA = u"Avís d'absència de l'alumne {0}. Dates absència: {1} {2} fins {3} {4}. Motiu: {5}"

ERROR_AL_PROGRAMA = u'''Avís d'error al programa: {0}'''

ACUS_REBUT_ERROR_AL_PROGRAMA = u'''Avís a administradors enviat correctament. El text de l'avís és: "{0}"'''

ACUS_REBUT_ENVIAT_A_PROFE_O_PAS = u'''Missatge enviat a {0}. El text del missatge és: "{1}"'''

EMAIL_A_FAMILIES = u'''Email a famílies enviat a {0} adreces. El text del mail és: {1}''' 

HAS_RECOLLIT_EXPULSIO = u'''ha recollit la següent expulsió: {0}'''

CAL_TRAMITAR_EXPULSIO = u'''Cal tramitar expulsió: {0}'''

ALUMNES_DONATS_DE_BAIXA = u'''El següents alumnes han estat donats de baixa.'''

ALUMNES_CANVIATS_DE_GRUP = u'''El següents alumnes han estat canviats de grup.'''

ALUMNES_ASSIGNAR_NOMSENTIT = "L'alumne {0} té nom sentit {1}"

ALUMNES_ESBORRAR_NOMSENTIT = "L'alumne {0} té nom sentit {1}"

ALUMNES_DONATS_DALTA = u'''El següents alumnes han estat donats d'alta.'''

ALUME_HA_ESTAT_SANCIONAT = u"L'alumne {0} ha estat sancionat ( del {1} al {2} )."

ACOMPANYANT_A_ACTIVITAT = u"""Has estat afegit com a professor acompanyant a l'activitat {sortida} 
                    del dia {dia}
                    """

RESPONSABLE_A_ACTIVITAT = u"""Has estat afegit com a professor responsable a l'activitat {sortida} 
                    del dia {dia}
                    """

FI_REPROGRAMACIO_CLASSES = "Reprogramació de classes finalitzada."

RECORDA_REPROGRAMAR_CLASSES = "Actualització d'horaris realitzada, recorda reprogramar les classes."

HE_POSAT_INCIDENCIA_EN_NOM_TEU = u"""He posat una {0} en nom teu a {1} ({2}) el dia {3}. 
                                El text de la incidència és: {4}"""

HE_POSAT_INCIDENCIA_EN_NOM_DALGU = u"""He posat una {0} en nom de {5} a {1} ({2}) el dia {3}. 
                                El text de la incidència és: {4}"""

SISTEMA_ANULA_RESERVA = u"El sistema ha hagut d'anul·lar la teva reserva: {0}"

ERROR_NOTIFICACIO_FAMILIES = u"Error enviant notificacions relació famílies."

ERROR_SINCRONITZANT_SORTIDES = u"Error sincronitzant sortides."

IMPORTACIO_SAGA_FINALITZADA = u"Importació Saga finalitzada."

IMPORTACIO_ESFERA_FINALITZADA = u"Importació Esfer@ finalitzada."

IMPORTACIO_PREINSCRIPCIO_FINALITZADA = u"Importació de la preinscripció finalitzada."

ACTIVACIO_MATRICULA_FINALITZADA = "Activació de matrícula completada."

IMPORTACIO_DADES_ADDICIONALS_FINALITZADA = u"Importació dades addicionals finalitzada."

ERROR_SIGNATURES_REPORT_PAGAMENT_ONLINE = u"Redsys: No hi ha coincidència entre firma rebuda {0}, i calculada {1}, en dades corresponents a report de transacció online"

ERROR_FALTEN_DADES_REPORT_PAGAMENT_ONLINE = u"Redsys: Falta nombre d'ordre ({0}) o codi autorització ({1}) o firma ({2}) en report de transacció online"

ERROR_IP_NO_PERMESA_REPORT_PAGAMENT_ONLINE =u"Redsys: Intent de reportar transacció online desde IP no permesa {0} , {1}"

MAIL_REBUTJAT=u"Mail rebutjat per l'usuari: \"{0}\"  adreça: \"{1}\".\nData d'enviament: {2}\nMotiu: {3}"

ALUMNE_SENSE_EMAILS=u"L'usuari: \"{0}\" no té adreça d'email informada"

FI_INITDB=u"Inicialització de la base de dades completada"

ERROR_INITDB=u"Inicialització incompleta de la base de dades"

PROFESSOR_RESERVA_MASSIVA=u"Se t'ha assignat el recurs \"{0}\" tots els {1} des del dia {2} fins al dia {3} a la franja \"{4}\""

PAGAMENT_INCORRECTE=u"El pagament fet no correspon"

MISSATGES = {'ADMINISTRACIO' : {'warning': {PASSAR_LLISTA_GRUP_NO_MEU,
                                FI_PROCES_AFEGIR_ALUMNES,
                                FI_PROCES_AFEGIR_ALUMNES_AMB_ERRORS,
                                HAN_PASSAT_LLISTA_PER_MI,
                                ERROR_AL_PROGRAMA,
                                ACUS_REBUT_ERROR_AL_PROGRAMA,
                                FI_PROCES_TREURE_ALUMNES,
                                FI_PROCES_TREURE_ALUMNES_AMB_ERRORS,
                                ALUMNES_DONATS_DE_BAIXA,
                                ALUMNES_CANVIATS_DE_GRUP,
                                ALUMNES_ASSIGNAR_NOMSENTIT,
                                ALUMNES_ESBORRAR_NOMSENTIT,
                                ALUMNES_DONATS_DALTA,
                                FI_REPROGRAMACIO_CLASSES,
                                RECORDA_REPROGRAMAR_CLASSES,
                                SISTEMA_ANULA_RESERVA,
                                ERROR_NOTIFICACIO_FAMILIES,
                                ERROR_SINCRONITZANT_SORTIDES,
                                IMPORTACIO_SAGA_FINALITZADA,
                                IMPORTACIO_ESFERA_FINALITZADA,
                                ERROR_SIGNATURES_REPORT_PAGAMENT_ONLINE,
                                ERROR_FALTEN_DADES_REPORT_PAGAMENT_ONLINE,
                                ERROR_IP_NO_PERMESA_REPORT_PAGAMENT_ONLINE,
                                MAIL_REBUTJAT,
                                ALUMNE_SENSE_EMAILS,
                                FI_INITDB,
                                ERROR_INITDB,
                                IMPORTACIO_PREINSCRIPCIO_FINALITZADA,
                                ACTIVACIO_MATRICULA_FINALITZADA,
                                }},
             'DISCIPLINA': {'danger': {EXPULSIO_PER_ACUMULACIO_INCIDENCIES,
                                       EXPULSIO_PER_ACUMULACIO_INCIDENCIES_FORA_AULA,
                                       HAS_RECOLLIT_EXPULSIO,
                                       CAL_TRAMITAR_EXPULSIO,}},
             'MISSATGERIA': {'info': {CONSERGERIA_A_TUTOR,
                                      CONSERGERIA_A_CONSERGERIA,
                                      AVIS_ABSENCIA,
                                      ACUS_REBUT_ENVIAT_A_PROFE_O_PAS,
                                      EMAIL_A_FAMILIES,
                                      PROFESSOR_RESERVA_MASSIVA}},
             'ACTIVITATS': {'success': {ACOMPANYANT_A_ACTIVITAT,
                                        RESPONSABLE_A_ACTIVITAT,}},
             'INFORMATIVES_DISCIPLINA': {'primary': {INCIDENCIA_INFORMATIVA,
                                                     ALUME_HA_ESTAT_SANCIONAT,
                                                     HE_POSAT_INCIDENCIA_EN_NOM_TEU,
                                                     HE_POSAT_INCIDENCIA_EN_NOM_DALGU,
                                                     }},}


def tipusMissatge(missatge):
    for tipus, valors in iter(MISSATGES.items()):
        for estat,frases in iter(valors.items()):
            if missatge in frases:
                return tipus
    return None