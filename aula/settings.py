# -*- coding: utf-8 -*- 

CUSTOM_RETART_PROVOCA_INCIDENCIA = True
CUSTOM_RETART_TIPUS_INCIDENCIA = { 'tipus': u'Incidència', 'es_informativa': False }
CUSTOM_RETART_FRASE = u'Ha arribat tard a classe.'

try:
    from settings_local import *
except ImportError:
    from settings_dir.demo import *


    




