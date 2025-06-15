# This Python file uses the following encoding: utf-8
# Django settings for aula project.

from .dev import *
location = lambda x: os.path.join(PROJECT_DIR, x)

TEMPLATES[0]['DIRS'] = [location('../demo/templates')]+TEMPLATES[0]['DIRS']

INSTALLED_APPS  = [
#                   'demo',
#                   'django.contrib.staticfiles',
                   ] + INSTALLED_APPS

NOM_CENTRE = 'Centre de Demo'
LOCALITAT = u"L'Escala"
URL_DJANGO_AULA = r'http://127.0.0.1:8000'

EMAIL_SUBJECT_PREFIX = '[DEMO AULA] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATICFILES_DIRS = [
    location( '../demo/static-web/'),
] + STATICFILES_DIRS

COMPRESS_ENABLED = False

CUSTOM_NOMES_TUTOR_POT_JUSTIFICAR = False
CUSTOM_MODUL_SORTIDES_ACTIU = True
CUSTOM_MODUL_MATRICULA_ACTIU = True
CUSTOM_FAMILIA_POT_MODIFICAR_PARAMETRES = True
CUSTOM_FAMILIA_POT_COMUNICATS = True
CUSTOM_PERMET_COPIAR_DES_DUNA_ALTRE_HORA = True

# Si True, permet que els tutors tinguin accés als informes de seguiment de faltes i incidències.
CUSTOM_TUTORS_INFORME = True

 
# Número de faltes no justificades per tal de generar carta
# Els tipus de carta els trobareu a:
#      aula/apps/tutoria/business_rules/cartaaabsentisme.py
CUSTOM_FALTES_ABSENCIA_PER_CARTA = 1
CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA = { 'tipus1': 1 }

# amorilla@xtec.cat 
# Permet concretar quantes faltes són necessaries segons el número de la carta
# Si existeix aquest valor aleshores no es fa servir CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA
# Si un nivell té assignat zero aleshores es mostrarà el missatge "Error triant la carta a enviar a la família"
# Si es superen les cartes indicades mostrarà el missatge "Aquest alumne ha arribat al màxim de cartes"
CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA = {
                    # nivell: [faltes per carta1, faltes per carta 2, ...],
                    u"ESO": [1, 1, 1],
                    u"BTX": [1, 1, 1],
                    u"INFORMATICA": [1],
                    u"CICLES": [1, 1, 1, 1],
                }

# Permet fer servir un idioma concret per al format
# de la data de la carta.
# S'ha d'activar, per Ubuntu:
# sudo locale-gen ca_ES.utf8

CUSTOM_LC_TIME = 'ca_ES.utf8'
CUSTOM_DATE_FORMAT = "%-d %B de %Y"  #  5 d'abril de 1999, si fem servir 'ca_ES.utf8'

# Per al càlcul d'indicadors
# Aquest indicadors apareixen a Coord.Alumnes / Indicadors
#  (Alumnes amb absències de més del <percentatge> de les hores lectives del trimestre / Total alumnes del nivell)*100
# els noms dels nivells corresponen a CUSTOM_NIVELLS
CUSTOM_INDICADORS = [
            # [inici_curs,  Final 1Trim,  Final 2Trim,  Final 3Trim, nivell,  %, controls ],
            ['09/09/2024', '29/11/2024', '07/03/2025', '20/06/2025', 'ESO', 25],
            ['09/09/2024', '29/11/2024', '07/03/2025', '20/06/2025', 'ESO', 10],
            ['09/09/2024', '29/11/2024', '07/03/2025', '20/06/2025', 'ESO', 5, ('F')],
            ['12/09/2024', '29/11/2024', '07/03/2025', '30/05/2025', 'BTX', 25],
            ['12/09/2024', '29/11/2024', '07/03/2025', '30/05/2025', 'BTX', 10],
            ['12/09/2024', '29/11/2024', '07/03/2025', '30/05/2025', 'BTX', 5, ('F')],
            ['12/09/2024', '22/11/2024', '07/03/2025', '23/05/2025', 'CICLES', 25],
            ['12/09/2024', '22/11/2024', '07/03/2025', '23/05/2025', 'CICLES', 10],
            ['12/09/2024', '22/11/2024', '07/03/2025', '23/05/2025', 'CICLES', 5, ('F')],
          ]

# Permet veure una graella amb les diferents faltes setmanals d'un curs.
CUSTOM_MODUL_PRESENCIA_SETMANAL_ACTIU = True

PRIVATE_STORAGE_ROOT = location('../storage')

CUSTOM_CODI_COMERÇ = '999008881'
CUSTOM_KEY_COMERÇ = 'sq7HjrUOBfKmC576ILgskD5srU870gJ7'
CUSTOM_SORTIDES_PAGAMENT_ONLINE = True
CUSTOM_SORTIDES_PAGAMENT_CAIXER = True
CUSTOM_FORMULARI_SORTIDES_REDUIT = True
CUSTOM_REDSYS_ENTORN_REAL = False
CUSTOM_QUOTES_ACTIVES = True
CUSTOM_TIPUS_QUOTA_MATRICULA = 'material'

CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT = 'Paga com puguis, no s\'ha especificat res de res'
CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ENTITAT_BANCARIA = u"""El pagament s'ha de realitzar fent ingrés en el número de compte de l'Institut Thos i Codina"""
CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_EFECTIU = u"""El pagament s'ha de realitzar en efectiu al professor organitzador de la sortida o al tutor."""
CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ONLINE = u"""El pagament s'ha de realitzar, amb targeta Mastercard o VISA, a través d'aquesta mateixa plataforma.\
                                                Targeta per DEMO 4548810000000003 12/49 123"""

POLITICA_COOKIES = location(r'../customising/TermesIcondicions/POLITICACOOKIES.sample')
POLITICA_RGPD = location(r'../customising/TermesIcondicions/POLITICARGPD.sample')
INFORGPD = location(r'../customising/TermesIcondicions/INFORGPD.sample')

FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760

CUSTOM_MESSAGE_BENVINGUDA_FAMILIES = [ u"Aquest missatge ha estat enviat per un sistema automàtic. No responguis  a aquest e-mail, el missatge no serà llegit per ningú.",
                     u"",
                     u"Per qualsevol dubte/notificació posa't en contacte amb el tutor/a.",
                     u"",
                     u"Benvolgut/da,",
                     u"",
                     u"El motiu d'aquest correu és el de donar-vos les instruccions d'alta de l'aplicació Djau del nostre centre.",
                     u"Aquesta aplicació us permetrà fer un seguiment diari del rendiment acadèmic del vostre fill/a.",
                     u"Per tant, hi trobareu les faltes d'assistència, de disciplina, les observacions del professorat , les sortides que afectaran al vostre fill/a entre altres informacions.",
                     u"",
                     u"Per a donar-vos d'alta:",
                     u"",
                     u" * Entreu a {0} on podeu obtenir o recuperar les claus d'accés a l'aplicació.".format(URL_DJANGO_AULA),
                     u" * Cliqueu l'enllaç 'Obtenir o recuperar accés'. ",
                     u" * Escriviu la vostra adreça de correu electrònic.",
                     u" * Cliqueu el botó  Enviar.",
                     u" * Consulteu el vostre correu electrònic on hi trobareu un missatge amb les instruccions per completar el procés d'accés al Djau.",
                     u"",
                     u"Com bé sabeu és molt important que hi hagi una comunicació molt fluida entre el centre i les famílies.",
                     u"És per això que us recomanem que us doneu d'alta a aquesta aplicació i per qualsevol dubte que tingueu al respecte, poseu-vos en contacte amb el tutor/a del vostre fill/a.",
                     u"",
                     u"Restem a la vostra disposició per a qualsevol aclariment.",
                     u"",
                     u"Cordialment,",
                     u"",
                     NOM_CENTRE,
                     u"",
                     ]
                     

