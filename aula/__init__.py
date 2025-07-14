# This Python file uses the following encoding: utf-8

# amorilla@xtec.cat
# Configura l'idioma correcte per les dates

import locale

from django.conf import settings

try:
    locale.setlocale(locale.LC_TIME, settings.CUSTOM_LC_TIME)
except (AttributeError, locale.Error):
    pass
