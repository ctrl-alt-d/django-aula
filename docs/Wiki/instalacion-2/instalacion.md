# Instalación en Ubuntu Server 18.04 LTS

{% hint style="warning" %}
Todas las instrucciones de este documento se deben ejecutar con permisos elevados
{% endhint %}

### Preparando el Entorno

El primer paso es preparar un entorno de desarrollo [`Python`](https://www.python.org/) en nuestro sistema, para ello instalamos los siguientes paquetes:

```text
apt-get update && apt-get install python-virtualenv python-pip libxml2-dev libxslt-dev python-libxml2 python-dev lib32z1-dev git
```

Entre otras cosas se ha instalado el paquete **python-virtualenv** ya que la instalación la haremos sobre un entorno virtual de **Python**, si tienes curiosidad sobre esto, visita este [enlace](https://packaging.python.org/guides/installing-using-pip-and-virtualenv/).

Nos colocamos en el directorio donde instalaremos la aplicación y clonamos el repositorio del proyecto.

```text
cd /opt && sudo git clone https://github.com/ctrl-alt-d/django-aula.git djau2019 && cd djau2019
```

{% hint style="info" %}
Es recomendable que la carpeta contenga el año del curso, ya que la aplicación esta diseñada para ser instalada de nuevo en cada curso \(Decisión de diseño\).
{% endhint %}

El siguiente paso es montar nuestro **entorno virtual Python** sobre la carpeta del proyecto, este comando creará un entorno virtual en un directorio llamado _**venv.**_

```text
djau@djau:/opt/djau2019#  python3 -m venv venv
```

Una vez creado el entorno virtual debemos activarlo, para ello ejecutamos:

```text
djau@djau:/opt/djau2019# source venv/bin/activate
```

Si todo ha ido bien el [**prompt**](https://es.wikipedia.org/wiki/Prompt) debería haber cambiado a algo parecido a:

_**`(venv) djau@djau:/opt/djau2019$`**_

Ahora que ya tenemos el entorno virtual el siguiente paso es instalar las dependencias del proyecto, para ello utilizaremos el gestor de dependencias [**pip**](https://es.wikipedia.org/wiki/Pip_%28administrador_de_paquetes%29)

```text
(venv) djau@djau:/opt/djau2019# pip3 install -r requirements.txt
```

### Instalación de Apache y Base de datos

Antes de seguir con la aplicación, instalaremos Apache  y el módulo [wsgi](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) para que pueda servir nuestra aplicación Python a través de él.

Además instalaremos la base de datos que usará django-aula y su conector python correspondiente, se recomienda instalar la aplicación sobre postgresql pero también es posible hacerlo sobre Mysql.

**Postgresql:**

```text
apt-get install apache2 libapache2-mod-wsgi python-psycopg2 postgresql 
pip3 install psycopg2
```

**Mysql:**

```text
apt-get install apache2 libapache2-mod-wsgi python-mysqldb mysql-server
```

Una vez elegido el motor de base de datos, hay que crear la base de datos de la aplicación, y crear un usuario que la pueda administrar.

{% code-tabs %}
{% code-tabs-item title="Para Postgresql" %}
```text
 
 sudo su postgres
 psql
 CREATE DATABASE djau2019;
 
CREATE USER djau2019 WITH PASSWORD 'XXXXXXXXXX';
 
GRANT ALL PRIVILEGES ON DATABASE djau2019 TO djau2019;
```
{% endcode-tabs-item %}

{% code-tabs-item title="Para Mysql" %}
```
mysql -u root -p
CREATE DATABASE djau2019 CHARACTER SET utf8;
CREATE USER 'djau2019'@'localhost' IDENTIFIED BY 'XXXXXXXX'
GRANT ALL PRIVILEGES ON djau2019.* TO 'djau2019'@'localhost';
USE djau2019;
SET storage-engine=INNODB;
QUIT
```
{% endcode-tabs-item %}
{% endcode-tabs %}

### Configurando Aplicación

Django Aula tiene 3 archivos principales de configuración

* **settings\_local.py \(Aquí esta la configuración principal\)**
* **settings.py \(Aquí se encuentra la parametrización Custom de la app\) más info.** [**aqui**](https://github.com/ctrl-alt-d/django-aula/blob/master/docs/manuals/parametritzacions.txt)
* **wsgi.py \(Es el script que se encargará de levantar la aplicación, Apache utilizará este archivo para servir la app a través de él\).**

A continuación dejo una configuración válida para los 3 archivos citados anteriormente, simplemente copia, pega y adáptalo a tus necesidades.

Los archivos están comentados para entenderlos mejor.

{% code-tabs %}
{% code-tabs-item title="/opt/djau2019/aula/settings\_local.py" %}
```python
# This Python file uses the following encoding: utf-8
# Django settings for aula project.

from aula.settings_dir.common import *

#En Producion dejar en False
DEBUG = False

#Informacion del Centro
NOM_CENTRE = 'Institut Badia'
LOCALITAT = u"Badia Del Valles"

#URL Por donde contestara la apliacion (Cambiar schema a https si se activa el trafico TSL)
URL_DJANGO_AULA = r'http://djau.local'

#HOSTS que tendran acceso a la Aplicacion (Por defecto '*' permite a todos los equipos con acceso a la maquina,usar la aplicacion)
#Puedes colocar direciones en formato CIDR o dominios, tambien se aceptan Wildcards
ALLOWED_HOSTS = [ '*', ]


ACCES_RESTRINGIT_A_GRUPS = None

#Datos del usuario administrador
ADMINS = (
    ('admin', 'juan@xtec.cat'),
)

#Configuracion del Correo Relay SMTP de la Aplicacion
EMAIL_HOST='smtp.gmail.com'
EMAIL_HOST_USER='juan@xtec.cat'
EMAIL_HOST_PASSWORD='xxxx xxxx xxxx xxxx'
DEFAULT_FROM_EMAIL = 'Institut Badia <no-reply@ibadia.cat>'
EMAIL_PORT=587
EMAIL_USE_TLS=True
SERVER_EMAIL='ibadia@xtec.cat'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_SUBJECT_PREFIX = '[Comunicacio Institut Badia del Valles] '

#Activar si se activa el trafico HTTPS
SESSION_COOKIE_SECURE=False

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
CSRF_COOKIE_SECURE=False

#Configuracion del Arbol de Prediccion (Si no eres experto no lo toques)
location = lambda x: os.path.join(PROJECT_DIR, x)
BI_DIR = '/opt/djau2019/aula/apps/BI/PMML'
#__PREDICTION_TREE_TMP = os.path.join( BI_DIR, 'previsioPresencia.pmml' )
#from lxml import etree
#PREDICTION_TREE = etree.parse( __PREDICTION_TREE_TMP )

INSTALLED_APPS  = [] + INSTALLED_APPS

#Ruta donde almacenara los assets de la aplicacion
STATICFILES_DIRS =  STATICFILES_DIRS
STATIC_ROOT= os.path.join(PROJECT_DIR,'static/')



#Comprime los assets estaticos de la app False por defecto
COMPRESS_ENABLED = False

#Passphrase que usara la app para cifrar las credenciales
SECRET_KEY = 'changeit'
CUSTOM_RESERVES_API_KEY = 'sxxxxxxm'

#Componente que utilizara  Django para serializar los objetos
SESSION_SERIALIZER='django.contrib.sessions.serializers.PickleSerializer'

#Configuracion de la Base de datos
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2', #django.db.backends.mysql *para mysql
        'NAME': 'djau2019',
        'USER': 'djau2019',
        'PASSWORD': "secret",
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

```
{% endcode-tabs-item %}

{% code-tabs-item title="/opt/djau2019/settings.py" %}
```python
# -*- coding: utf-8 -*-

CUSTOM_RETARD_PROVOCA_INCIDENCIA = True
CUSTOM_RETARD_TIPUS_INCIDENCIA = { 'tipus': u'Incidència', 'es_informativa': False }
CUSTOM_RETARD_FRASE = u'Ha arribat tard a classe.'
CUSTOM_TIPUS_INCIDENCIES = False
CUSTOM_PERIODE_CREAR_O_MODIFICAR_INCIDENCIA = 90
CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO = True
CUSTOM_PERIODE_MODIFICACIO_ASSISTENCIA = 90
CUSTOM_DIES_PRESCRIU_INCIDENCIA = 30
CUSTOM_DIES_PRESCRIU_EXPULSIO = 90
CUSTOM_NOMES_TUTOR_POT_JUSTIFICAR = True
CUSTOM_MODUL_SORTIDES_ACTIU = True
CUSTOM_PERMET_COPIAR_DES_DUNA_ALTRE_HORA = False
CUSTOM_RETARD_PRIMERA_HORA_GESTIONAT_PEL_TUTOR = False
CUSTOM_NIVELLS = { u"ESO": [u"ESO"],
                    u"BTX": [u"BTX"],
                    u"CICLES": [u'GA',u'AF',u'SMX',u'DAW',u'FCT',u"CFA",u"CFI",],
                    u"INFORMATICA": [u'SMX',u'DAW'],
                  }
CUSTOM_TIMEOUT = 15*60
CUSTOM_TIMEOUT_GROUP = { u"consergeria": 4*60*60, # 4h
                         u"professors":    15*60, # 15'
                         }
CUSTOM_RESERVES_API_KEY = '_default_api_aules_password_'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    },
    'select2': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'TIMEOUT': max( CUSTOM_TIMEOUT, *[ CUSTOM_TIMEOUT_GROUP[x] for x in CUSTOM_TIMEOUT_GROUP] ),
        'OPTIONS': {
            'MAX_ENTRIES': 200
        }
    }
}

CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT = u"""Podeu fer el pagament amb targeta de crèdit a qualsevol caixer de CaixaBank, amb el codi de barres o amb el codi entitat: XXXXXXX"""
#Si True, permet que els tutors tinguin accés als informes de seguiment de faltes i incidències.
CUSTOM_TUTORS_INFORME = False

#URL on trobar el tutorial del portal famílies
CUSTOM_PORTAL_FAMILIES_TUTORIAL = u""

#Número de faltes no justificades per tal de generar carta
#Els tipus de carta els trobareu a:
#      aula/apps/tutoria/business_rules/cartaaabsentisme.py
CUSTOM_FALTES_ABSENCIA_PER_CARTA = 1
CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA = { 'tipus1': 1 }

CUSTOM_FALTES_ABSENCIA_PER_CARTA = 15
CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA = { 'tipus1': 15 }
CUSTOM_DIES_PRESCRIU_EXPULSIO = 90
CUSTOM_MODUL_SORTIDES_ACTIU = True

try:
    from settings_local import *
except ImportError:
    from settings_dir.demo import *
```
{% endcode-tabs-item %}

{% code-tabs-item title="/opt/djau2019/aula/wsgi.py" %}
```python

"""
WSGI config for aula project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""
import os
import sys
import site

site.addsitedir(' /opt/djau2019/venv/lib/python3.6/site-packages/')
sys.path.append(' /opt/djau2019/')
sys.path.append(' /opt/djau2019/aula/')

# We defer to a DJANGO_SETTINGS_MODULE already in the environment. This breaks
# if running multiple sites in the same mod_wsgi process. To fix this, use
# mod_wsgi daemon mode with each site in its own daemon process, or use
# os.environ["DJANGO_SETTINGS_MODULE"] = "aula.settings"
os.environ['DJANGO_SETTINGS_MODULE'] = 'aula.settings'
activate_this = os.path.expanduser("/opt/djau2019/venv/bin/activate_this.py")
execfile(activate_this, dict(__file__=activate_this))

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)

```
{% endcode-tabs-item %}
{% endcode-tabs %}

Con los archivos de configuración listos es momento de [mapear](https://docs.djangoproject.com/en/2.0/topics/migrations/) los modelos del proyecto django hacia nuestra base de datos, es decir vamos a crear las tablas de la aplicación, empezaremos a ver cómo se crean todas las tablas, no debe dar ningún error.

```text
 djau@djau:/opt/djau2019# python manage.py migrate
```

Ahora que tenemos las tablas creadas, hay que llenarlas con algunos datos esenciales para que la app arranque, para ello ejecutamos el siguiente script:

```text
djau@djau:/opt/djau2019# bash scripts/fixtures.sh
```

{% hint style="warning" %}
Es muy posible que dé algún Warning, simplemente ignóralo, recuerda que esta aplicación aún está en desarrollo.
{% endhint %}

Ahora debemos crear un usuario administrador que pueda gestionar la app, para ello ejecutamos:

```text
djau@djau:/opt/djau2019# python manage.py createsuperuser
```

Nos pedirá el nombre del usuario y su contraseña \(en este ejemplo lo he llamado **admin**\).

Para que nuestro administrador pueda iniciar sesión en la aplicación, debe de estar en el grupo de **dirección,profesores y profesional** de la base de datos, para ello abrimos una shell de django y escribimos línea a línea lo siguiente:

```text
djau@djau:/opt/djau2019# python manage.py shell

from django.contrib.auth.models import User, Group
g1 = Group.objects.get( name = 'direcció' )
g2 = Group.objects.get( name = 'professors' )
g3 = Group.objects.get( name = 'professional' )
a = User.objects.get( username = 'admin' )
a.groups.set( [ g1,g2,g3 ] )
a.save()
quit()

```

Como paso final de configuración, vamos a juntar todo el contenido estático \(js,css..etc\) del proyecto a un solo directorio, para que la instalación sea mas limpia. Más información sobre el contenido estático en django [aqui](https://docs.djangoproject.com/en/2.0/howto/static-files/).

```text
djau@djau:/opt/djau2019# python manage.py collectstatic
```

Esto generará un directorio llamado **static** donde se alojarán todos los assets de la aplicación.

### Configurando Apache para que sirva la app

Si se ha seguido al pie de la letra este manual, simplemente hay que crear un nuevo Virtualhost en Apache que sirva nuestra app por el protocolo WSGI.

El primer escenario es para servir la app por el puerto 80 \(http\),

El segundo escenario sirve la app por SSL \(https\)

{% code-tabs %}
{% code-tabs-item title="Primer Escenario /etc/apache2/sites-enabled/djau.conf" %}
```text

<VirtualHost *:80>
        ServerAdmin juan@xtec.cat
        ServerName djau.local
        
        #Ruta del demonio WSGI (utilizamos nuestro virtualenv)
        WSGIDaemonProcess djau  python-home=/opt/djau2019/venv/bin  python-path=/opt/djau2019:/opt/djau2019/venv/lib/python3.6/sites-packages
        WSGIProcessGroup djau
        #Script que arrancara la aplicacion wsgi
        WSGIScriptAlias / /opt/djau2019/aula/wsgi.py
        
        #Alias para contenido estatico de la app
        
        Alias /site-css/admin /opt/djau2019/aula/static/admin/
        Alias /site-css /opt/djau2019/aula/static/

        ErrorLog /var/log/apache2/djau_error.log

        #Dando acceso a apache a los directorios de la app
        <Directory /opt/djau2019/aula>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

        <Directory /opt/djau2019/aula/static/>
                Require all granted
        </Directory>


        <Directory /opt/djau2019/aula/static/admin/>
                Require all granted
        </Directory>

        LogLevel warn

        CustomLog /var/log/apache2/djau_access.log combined

        BrowserMatch ".*MSIE.*" \
                nokeepalive ssl-unclean-shutdown \
                downgrade-1.0 force-response-1.0

</VirtualHost>

```
{% endcode-tabs-item %}

{% code-tabs-item title="Segundo Escenario /etc/apache2/sites-enbled/djau\_ssl.conf" %}
```
#Recuerda cambiar lo necesario en el archivo /opt/djau2019/aula/settings_local.py
#Para que la app pueda ir por SSL (TLS)
#Tambien activa si no lo esta el modulo ssl:
# a2enmod ssl

<VirtualHost *:443>
        ServerAdmin juan@xtec.cat
        ServerName djau.local

        #Ruta del demonio WSGI (utilizamos nuestro virtualenv)
        
        WSGIDaemonProcess djaussl  python-home=/opt/djau2019/venv/bin  python-path=/opt/djau2019:/opt/djau2019/venv/lib/python3.6/sites-packages
        WSGIProcessGroup djaussl
        #Script que arrancara la aplicacion wsgi
        WSGIScriptAlias / /opt/djau2019/aula/wsgi.py

        #Alias para contenido estatico de la app

        Alias /site-css/admin /opt/djau2019/aula/static/admin/
        Alias /site-css /opt/djau2019/aula/static/

        ErrorLog /var/log/apache2/djau_ssl_error.log

        #Dando acceso a apache a los directorios de la app
        <Directory /opt/djau2019/aula>
                <Files wsgi.py>
                        Require all granted
                </Files>
        </Directory>

        <Directory /opt/djau2019/aula/static/>
                Require all granted
        </Directory>


        <Directory /opt/djau2019/aula/static/admin/>
                Require all granted
        </Directory>

        #SSL Config#########################

        # Generar SelfSignedCertificate
        # openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/ssl/private/badia-selfsigned.key -out /etc/ssl/certs/badia-selfsigned.crt

        SSLEngine on
        SSLCertificateFile /etc/ssl/certs/badia-selfsigned.crt
        SSLCertificateKeyFile /etc/ssl/private/badia-selfsigned.key
        LogLevel warn

        #SSL Config#######################


        CustomLog /var/log/apache2/djau_ssl_access.log combined

        BrowserMatch ".*MSIE.*" \
                nokeepalive ssl-unclean-shutdown \
                downgrade-1.0 force-response-1.0

</VirtualHost>

```
{% endcode-tabs-item %}
{% endcode-tabs %}

Una vez creado el VirtualHost,  deshabilitamos el Vhost que trae por defecto Apache para que no nos de problemas y reiniciamos el servidor web

```text
djau@djau:# a2dissite 000.default.conf  # potser el fitxer és diferent: 000-default.conf
djau@djau:# service apache2 reload
```

Si todo ha ido bien, la aplicación ya esta desplegada en producción , si accedemos a su dominio en mi caso "http://djau.local" o "https://djau.local" según escenario, deberá abrirse el Panel de Login de Django-Aula. **¡Felicidades!**

![](../.gitbook/assets/captura.PNG)

### Post Instalación

Es recomendable programar los siguientes Scripts en **Cron:**

{% code-tabs %}
{% code-tabs-item title="CronTab" %}
```text
0,20,40 * * * * su - djau /opt/djau2019/backup-bdd-2018.sh42 8,9,10,11,12,13,14,15,16,17,18,19,20,21 * * 1,2,3,4,5 su - www-data -c "/opt/djau2019/scripts/notifica_families.sh" >> /opt/django/log/notifica_families_`/bin/date +\%Y_\%m_\%d`.log 2>&141 00 * * 1,2,3,4,5 su - www-data -c "/opt/djau2019/scripts/preescriu_incidencies.sh" >> /opt/django/log/prescriu_incidencies_`/bin/date +\%Y_\%m_\%d`.log 2>&120,50 * * * 1,2,3,4,5 su - www-data -c "/opt/djau2019/scripts/sortides_sincronitza_presencia.sh" >>  /opt/django/log/sincro_presencia_`/bin/date +\%Y_\%m_\%d`.log 2>&1
```
{% endcode-tabs-item %}
{% endcode-tabs %}

{% hint style="info" %}
Están creados todos los scripts menos el siguiente, créalo y dale permisos de ejecución.
{% endhint %}

{% code-tabs %}
{% code-tabs-item title="/opt/django/backup-bdd-2018.sh" %}
```bash
#!/bin/bash
ara=`/bin/date +%Y%m%d%H%M`
hora=`/bin/date +%H`
dia=`/bin/date +%d`
mes=`/bin/date +%Y%m`
directori="/opt/django/djauBK/"
copia="${directori}bdd-ara-${ara}.sql"
extensio=".bz2"
mkdir $directori
/usr/bin/pg_dump -U djau2019 djau2019 > $copia
/bin/bzip2 $copia
cat "${copia}${extensio}" > "${directori}bdd-hora-${hora}.sql${extensio}" 
cat "${copia}${extensio}" > "${directori}bdd-dia-${dia}.sql${extensio}" 
cat "${copia}${extensio}" > "${directori}bdd-mes-${mes}.sql${extensio}" 
rm $copia${extensio}
```
{% endcode-tabs-item %}
{% endcode-tabs %}



