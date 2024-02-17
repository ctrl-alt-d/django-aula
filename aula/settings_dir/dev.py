# This Python file uses the following encoding: utf-8
# Django settings for aula project.
from environ import Env, Path

from .common import *

# environ configuration
env = Env()
env_db = Env()
repository = Path(__file__) - 3

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=False)
if READ_DOT_ENV_FILE:
    env.read_env(repository(".env"))

DEBUG = True
SQL_DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': env.str('DB_ENGINE', default='django.db.backends.sqlite3'),
        'NAME': env.str('DB_NAME', default=location('db.sqlite')),
        'USER': env.str('DB_USER', default=''),
        'PASSWORD': env.str('DB_PASSWORD', default=''),
        'HOST': env.str('DB_HOST', default=''),
        'ATOMIC_REQUESTS': env.bool('DB_ATOMIC_REQUESTS', default=True),
    }
}


# per mysql:
#    sudo apt-get install apache2 libapache2-mod-wsgi-py3 python3-mysqldb mysql-server libmysqlclient-dev pkg-config
#    pip3 install wheel mysqlclient
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

MIDDLEWARE += [
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
]

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False
}

EMAIL_SUBJECT_PREFIX = '[DEMO AULA] '
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

COMPRESS_ENABLED = False

