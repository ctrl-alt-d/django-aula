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
URL_DJANGO_AULA = r'http://djau.ctrlalt.d.webfactional.com'

EMAIL_SUBJECT_PREFIX = '[DEMO AULA] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

STATICFILES_DIRS = [
    location( '../demo/static-web/'),
] + STATICFILES_DIRS

COMPRESS_ENABLED = False
