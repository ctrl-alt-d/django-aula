# -*- coding: utf-8 -*- 

CUSTOM_RETARD_PROVOCA_INCIDENCIA = True
CUSTOM_RETARD_TIPUS_INCIDENCIA = { 'tipus': u'Incidència', 'es_informativa': False }
CUSTOM_RETARD_FRASE = u'Ha arribat tard a classe.'
CUSTOM_RANKING_BY_TIPUS = False
CUSTOM_PERIODE_CREAR_O_MODIFICAR_INCIDENCIA = 90
CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO = True
CUSTOM_PERIODE_MODIFICACIO_ASSISTENCIA = 90
CUSTOM_DIES_PRESCRIU_INCIDENCIA = 30
CUSTOM_DIES_PRESCRIU_EXPULSIO = 60

try:
    from settings_local import *
except ImportError:
    from settings_dir.demo import *


    




