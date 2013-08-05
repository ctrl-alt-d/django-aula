# This Python file uses the following encoding: utf-8
# Django settings for aula project.

from dev import *

INSTALLED_APPS  = [
                   'demo',
                   ] + INSTALLED_APPS

NOM_CENTRE = 'Centre de Demo'
LOCALITAT = u"L'Escala"
URL_DJANGO_AULA = r'http://djau.ctrlalt.d.webfactional.com'

EMAIL_SUBJECT_PREFIX = '[DEMO AULA] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

COMPRESS_ENABLED = False