# -*- coding: utf-8 -*- 
import os

NOM_CENTRE = 'Centre C'
LOCALITAT = u"Localitat"
URL_DJANGO_AULA = r'https://www.django_aula.sw'
ACCES_RESTRINGIT_A_GRUPS = None   # exemple per restringir = ['direcció','administradors','psicopedagog']

# Django settings for aula project.
PROJECT_DIR = os.path.join( os.path.dirname(__file__), '..')
location = lambda x: os.path.join(PROJECT_DIR, x)

ADMINS = (
    ('dani Herrera', 'ctrl.alt.d@gmail.com'),
)

LOGIN_URL="/usuaris/login/"

LICENSE_FILE = location( r'../LICENSE' )

MANAGERS = ADMINS

#En cas de tenir un arbre de predicció cal posar-lo aquí:
# from lxml import etree  
# PREDICTION_TREE=etree.parse( r'path_fins_el_model' )
PREDICTION_TREE = None

DATABASES = None  #overrided on prod, dev environment

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = []

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Europe/Madrid'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ca'
LANGUAGES = (
             ('ca', 'Català'),
             )

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = False

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = ''

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = location('../static/')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/site-css/'  #sobreescriure-la al 'settings_local.py'

# Additional locations of static files
STATICFILES_DIRS = [
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    location( 'site-css'),
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7!=1#dqm%5f2!1@1yeopi(p3$!d)#t8%4-p-rio^%!l(*p6d4+'

# List of callables that know how to import templates from various sources.
# TEMPLATE_LOADERS = (
#     'django.template.loaders.filesystem.Loader',
#     'django.template.loaders.app_directories.Loader',
# #     'django.template.loaders.eggs.Loader',
# )
DEBUG=True
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
                location('../customising/templates'),
                location('templates'),
        ],
        #'APP_DIRS': True,
        'OPTIONS': {
            'debug' : DEBUG,
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                #"django.core.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.csrf",
                'django.template.context_processors.request',
                'aula.utils.context_processors.dades_basiques',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]



# TEMPLATE_CONTEXT_PROCESSORS = (
#     "django.contrib.auth.context_processors.auth",
#     "django.core.context_processors.debug",
#     #"django.core.context_processors.i18n",
#     "django.core.context_processors.media",
#     "django.core.context_processors.static",
#     "django.contrib.messages.context_processors.messages",
#     "django.core.context_processors.csrf",
#     'django.core.context_processors.request',
#     'aula.utils.context_processors.dades_basiques',
#     )


ATOMIC_REQUESTS = True  # per quan es migri a 1.6
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'aula.utils.middleware.MultipleProxyMiddleware',
    'aula.utils.middleware.NoCacheMiddleware',   
    'aula.utils.middleware.timeOutMiddleware', 
    'aula.utils.middleware.IncludeLoginInErrors',    
]

ROOT_URLCONF = 'aula.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'aula.wsgi.application'

# TEMPLATE_DIRS = [
#     location('../customising/templates'),
#     location('templates'),
# ]

INSTALLED_APPS_DJANGO = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_extensions',
    'django_tables2',
    'django.contrib.humanize',
]
    
INSTALLED_APPS_AULA = [
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
    'aula.apps.missatgeria',
    'aula.apps.alumnes',
    'aula.apps.assignatures',
    'aula.apps.horaris',
    'aula.apps.presencia',
    'aula.apps.incidencies',
    'aula.apps.tutoria',
    'aula.apps.extKronowin',
    'aula.apps.extSaga',
    'aula.apps.extEsfera',
    'aula.apps.avaluacioQualitativa',
    'aula.apps.todo',
    'aula.apps.usuaris',
    'aula.apps.relacioFamilies',
    'aula.apps.sortides',
    'aula.apps.baixes',
    'aula.apps.BI',
    'aula.apps.aules',
    'aula.utils',
    'aula.apps.presenciaSetmanal',
    'aula.apps.extUntis',
]

#select2
AUTO_RENDER_SELECT2_STATICS=False
#---


MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

INSTALLED_APPS = ['customising',] + INSTALLED_APPS_DJANGO + INSTALLED_APPS_AULA

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

#Notice: keep safe your SECRET_KEY, we use PickleSerializer.
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

SEND_BROKEN_LINK_EMAILS = False

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'stop_suspicious_operation': {
            '()': 'aula.utils.loggingFilters.StopSuspiciousOperation',
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false','stop_suspicious_operation',],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}


