from settings_dir.dev import *

NOM_CENTRE = 'Centre de Prova'
LOCALITAT = u"L'Escala"
URL_DJANGO_AULA = r'https://www.django_aula.sw'


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'dau1',
        'USER': 'pepe',
        'PASSWORD': 'i',
        'HOST': '127.0.0.1',
        'PORT': '',
    }
}