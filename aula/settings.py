# -*- coding: utf-8 -*-

CUSTOM_ORDER_PRESENCIA = ['alumne'] # Pots triar ['alumne___cognoms','alumne__nom, 'alumne__grup', 'alumne']
CUSTOM_RETARD_PROVOCA_INCIDENCIA = True
CUSTOM_RETARD_TIPUS_INCIDENCIA = { 'tipus': u'Incidència', 'es_informativa': False }
CUSTOM_RETARD_FRASE = u'Ha arribat tard a classe.'
CUSTOM_TIPUS_INCIDENCIES = False
CUSTOM_PERIODE_CREAR_O_MODIFICAR_INCIDENCIA = 90
CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO = True
CUSTOM_PERIODE_MODIFICACIO_ASSISTENCIA = 90
CUSTOM_DIES_PRESCRIU_INCIDENCIA = 30
CUSTOM_DIES_PRESCRIU_EXPULSIO = 90
CUSTOM_NOMES_TUTOR_POT_JUSTIFICAR = True
CUSTOM_MODUL_SORTIDES_ACTIU = True
CUSTOM_MODUL_MATRICULA_ACTIU = False

CUSTOM_PERMET_COPIAR_DES_DUNA_ALTRE_HORA = False
CUSTOM_RETARD_PRIMERA_HORA_GESTIONAT_PEL_TUTOR = False
CUSTOM_NIVELLS = { u"ESO": [u"ESO"],
                    u"BTX": [u"BTX"],
                    u"CICLES": [u'GA',u'AF',u'SMX',u'DAW',u'FCT',u"CFA",u"CFI",],
                    u"INFORMATICA": [u'SMX',u'DAW'],
                  }

CUSTOM_TIMEOUT = 15*60
CUSTOM_TIMEOUT_GROUP = { u"consergeria": 4*60*60, # 4h
                         u"professors":    15*60, # 15'
                         }

CUSTOM_RESERVES_API_KEY = '_default_api_aules_password_'

DEFAULT_FROM_EMAIL = 'El meu centre <no-reply@el-meu-centre.net>'
# Quantitat màxima de destinataris per cada email, depèn del servidor de correu
CUSTOM_MAX_EMAIL_RECIPIENTS=100
EMAIL_HOST_IMAP = "imap.gmail.com"

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'select2': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': max( CUSTOM_TIMEOUT, *[ CUSTOM_TIMEOUT_GROUP[x] for x in CUSTOM_TIMEOUT_GROUP] ),
        'OPTIONS': {
            'MAX_ENTRIES': 200
        }
    }
}

CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT = u"""Podeu fer el pagament amb targeta de crèdit a qualsevol caixer de CaixaBank, amb el codi de barres o amb el codi entitat: XXXXXXXXXX"""
CUSTOM_SORTIDES_PAGAMENT_ONLINE = False
CUSTOM_PREU_MINIM_SORTIDES_PAGAMENT_ONLINE = 1
CUSTOM_SORTIDES_PAGAMENT_CAIXER = True
CUSTOM_FORMULARI_SORTIDES_REDUIT = True
CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ENTITAT_BANCARIA = u"""El pagament s'ha de realitzar als Caixers del Banc Sabadell (qualsevol targeta de qualsevol entitat funciona per realitzar el pagament, no cal tenir compte al Banc) a pagament a tercers i posar el codi de pagament: 5805."""
CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_EFECTIU = u"""El pagament s'ha de realitzar en efectiu al professor organitzador de la sortida o al tutor."""
CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ONLINE = u"""El pagament s'ha de realitzar a través d'aquesta mateixa plataforma"""
CUSTOM_REDSYS_ENTORN_REAL = False
# Si True permet utilitzar les quotes
CUSTOM_QUOTES_ACTIVES = False
CUSTOM_TIPUS_QUOTA_MATRICULA = None

#Fitxer de text amb l'avís sobre el tractament de dades personals, es poden fer servir marques HTML.
#Es mostra a la part inferior de les pantalles d'entrada de dades com la de "Canvi de paràmetres".
#INFORGPD = location( r'../customising/TermesIcondicions/INFORGPD.sample' )
#Política de cookies.
#POLITICA_COOKIES = location( r'../customising/TermesIcondicions/POLITICACOOKIES.sample' )
#Informació sobre protecció de dades de caràcter personal.
#POLITICA_RGPD = location( r'../customising/TermesIcondicions/POLITICARGPD.sample' )

#Si True, permet que els tutors tinguin accés als informes de seguiment de faltes i incidències.
CUSTOM_TUTORS_INFORME = False

#URL on trobar el tutorial del portal famílies
CUSTOM_PORTAL_FAMILIES_TUTORIAL = u""

#Número de faltes no justificades per tal de generar carta
#Els tipus de carta els trobareu a:
#      aula/apps/tutoria/business_rules/cartaaabsentisme.py
CUSTOM_FALTES_ABSENCIA_PER_CARTA = 1
CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA = { 'tipus1': 1 }

CUSTOM_MOSTRAR_MAJORS_EDAT = False
CUSTOM_MARCA_MAJORS_EDAT = u' (^18)' #Missatge que apareix al costat dels majors d'edat

CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA = {  
                    # nivell: [faltes per carta1, faltes per carta 2, ...],
                    # u"ESO": [10],  
                    # u"BAT": [10,10,10],
                }

CUSTOM_LC_TIME = None  # 'ca_ES.utf8'
CUSTOM_DATE_FORMAT = "%-d %B de %Y"   #  5 d'abril de 1999, si fem servir 'ca_ES.utf8'

CUSTOM_NO_CONTROL_ES_PRESENCIA = False

CUSTOM_INDICADORS = [
            # [inici_curs,  Final 1Trim,  Final 2Trim,  Final 3Trim, nivell,  %, controls ],
            # ['dd/mm/aaaa', 'dd/mm/aaaa', 'dd/mm/aaaa', 'dd/mm/aaaa', 'NNNN', 5, ('F')],
          ]

#Permet veure una graella amb les diferents faltes setmanals d'un curs.
CUSTOM_MODUL_PRESENCIA_SETMANAL_ACTIU = False

CUSTOM_GRUPS_PODEN_VEURE_FOTOS = ['direcció', 'professors', 'professional', 'consergeria', 'psicopedagog']
CUSTOM_TIPUS_MIME_FOTOS = ['image/gif','image/jpeg','image/png']
PRIVATE_STORAGE_ROOT ='/dades/fitxers_privats_djAu/'
CUSTOM_CODI_COMERÇ = 'xxxxxx'
CUSTOM_KEY_COMERÇ = 'xxxxxx'

# Per canvis a Django 3.2
DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Per personalitzar el template del widget aula.apps.matricula.forms.CustomClearableFileInput
FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

# Límit de mida per upload
FILE_UPLOAD_MAX_MEMORY_SIZE=20971520
DATA_UPLOAD_MAX_MEMORY_SIZE=20971520

CUSTOM_DADES_ADDICIONALS_ALUMNE = [
    # {
    #     'label':  'Drets imatge',
    #     'esautoritzacio': True,
    #     'visibilitat': ['Familia','Professor'],
    # },
    # {
    #     'label':  'Autorització sortides',
    #     'esautoritzacio': True,
    #     'visibilitat': ['Familia','Professor'],
    # },
    # {
    #     'label':  'Salut i Escola',
    #     'esautoritzacio': True,
    #     'visibilitat': ['Familia','Professor'],
    # },
    # {
    #     'label':  'Responsable Preferent',
    #     'esautoritzacio': False,
    #     'visibilitat': ['Tutor'],
    # },
    # {
    #     'label':  'Dades mèdiques',
    #     'esautoritzacio': False,
    #     'visibilitat': ['Familia','Professor'],
    # },
    ]


try:
    from .settings_local import *
except ImportError:
    from .settings_dir.demo import *


    




