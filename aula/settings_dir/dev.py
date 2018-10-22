# This Python file uses the following encoding: utf-8
# Django settings for aula project.

from common import *

DEBUG = True
SQL_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': "/tmp/db.sqlite", # location( 'db.sqlite'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
        'ATOMIC_REQUESTS': True,
    }
}


# per mysql:  
#     sudo apt-get install mysql-server python-mysqldb libmysqlclient-dev
#     pip install MySQL-python
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'dau1',
#         'USER': 'pepe',
#         'PASSWORD': 'i',
#         'HOST': '127.0.0.1',
#         'PORT': '',
#     }
# }

INSTALLED_APPS = [
    #'debug_toolbar',
    'demo',
] + INSTALLED_APPS

MIDDLEWARE_CLASSES += [
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

EMAIL_SUBJECT_PREFIX = '[DEMO AULA] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

COMPRESS_ENABLED = False

