# -*- coding: utf-8 -*- 

CUSTOM_RETARD_PROVOCA_INCIDENCIA = True
CUSTOM_RETARD_TIPUS_INCIDENCIA = { 'tipus': u'Incidència', 'es_informativa': False }
CUSTOM_RETARD_FRASE = u'Ha arribat tard a classe.'

try:
    from settings_local import *
except ImportError:
    from settings_dir.demo import *


    




