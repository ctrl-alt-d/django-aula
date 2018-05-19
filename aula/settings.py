# -*- coding: utf-8 -*-

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

CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT = u"""Podeu fer el pagament amb targeta de crèdit a qualsevol caixer de CaixaBank, amb el codi de barres o amb el codi entitat: XXXXXXX"""
#Si True, permet que els tutors tinguin accés als informes de seguiment de faltes i incidències.
CUSTOM_TUTORS_INFORME = False

#URL on trobar el tutorial del portal famílies
CUSTOM_PORTAL_FAMILIES_TUTORIAL = u""

#Número de faltes no justificades per tal de generar carta
#Els tipus de carta els trobareu a:
#      aula/apps/tutoria/business_rules/cartaaabsentisme.py
CUSTOM_FALTES_ABSENCIA_PER_CARTA = 1
CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA = { 'tipus1': 1 }

CUSTOM_FALTES_ABSENCIA_PER_CARTA = 15
CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA = { 'tipus1': 15 }
CUSTOM_DIES_PRESCRIU_EXPULSIO = 90
CUSTOM_MODUL_SORTIDES_ACTIU = True

try:
    from settings_local import *
except ImportError:
    from settings_dir.demo import *