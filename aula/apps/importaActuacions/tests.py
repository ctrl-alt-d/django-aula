from django.test import TestCase
from django.shortcuts import render
from django.db import connections, OperationalError, DatabaseError

# Create your tests here.

from aula.apps.alumnes.models import Alumne, Curs
from aula.apps.tutoria.models import Actuacio
from django.contrib.auth.models import User

# Per afegir i/o eliminar bases de dades a la configuració
from aula import settings_local

def tests(request):

    # Obtens una llista i cada posició d'aquesta és un diccionari que té els valors de cada registre
    #alumnes_list = list(Alumne.objects.values().order_by('id'))

    # Si només es volen uns camps i que no es pugui modificar, amb list s'obté una llista de tuples com [(203, '11980595110'), (204, '6966295004')...
    # Si només es volen uns camps però que sí que es puguin modificar, amb dict s'obté un diccionari com {203: '11980595110', 204: '6966295004'...
    #alumnes_ralc_id = dict(Alumne.objects.values_list('ralc', 'id').order_by('id'))
    
    #usuaris_username_id = dict(User.objects.values_list('username','id').exclude(username__startswith = 'almn').order_by('username'))
    #usuaris_olddb_id_username = dict(User.objects.using(dades_connexio_bd['nom']).values_list('id', 'username').exclude(username__startswith = 'almn').order_by('id'))

    # Llista de tuples per poder informar del professorat que ja no hi és al centre
    #usuaris_olddb_username_firstname_lastname_list = list(User.objects.using(dades_connexio_bd['nom']).values_list('username', 'first_name', 'last_name').exclude(username__startswith = 'almn').order_by('username'))

    # Obtens una llista d'actuacions. Si volem tots els valors, cada registre es un diccionari.
    #actuacions_list = list(Actuacio.objects.order_by('id').values())
    #actuacions_olddb_list = list(Actuacio.objects.using(dades_connexio_bd['nom']).values().order_by('id'))
    #actuacions_olddb_list_modificada = deepcopy(actuacions_olddb_list) # ELIMINAR. Creada per a debug
 
    # Obtens una llista d'usuaris. Si volem tots els valors, cada registre es un diccionari.
    #usuaris_list = list(User.objects.values().order_by('id'))
    #usuaris_olddb_list = list(User.objects.using(dades_connexio_bd['nom']).values().order_by('id'))

    # Modificar el valor d'un camp d'un registre concret
    #alumnes_list[0].update({'observacions': ''})
 
    # Mostra el valor del camp d'un registre
    #debug = alumnes_list[0].get('ralc')

    # Mostra el primer registre de la taula, com a diccionari
    #debug = alumnes_olddb_list[0]

    # Obtenir les claus del diccionari, és a dir, els noms dels camps.
    # claus_list = list(dict.keys(alumnes_list[0]))

    #debug = actuacions_olddb_list_modificada[0].get('alumne_id')
    #debug2 = alumnes_olddb_id_ralc[debug]

    settings_local.DATABASES['djau2021'] = {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'name',
        'USER': 'user',
        'PASSWORD': 'XXXX',
        'HOST': 'localhost',
        'PORT': '5432',
        'ATOMIC_REQUESTS': False,
        'AUTOCOMMIT': True,
        'CONN_MAX_AGE': 0,
        'OPTIONS': {},
        'TIME_ZONE': None
    }


    return render(
    request,
    '../templates/test.html', 
        {
            'debug': '',
            'debug2': '',
        },
    )


'''
##########
# DJANGO #
##########

# Elimina la base de dades antiga del llistat de bases de dades accessibles
# DATABASES.pop('djau2021')

# Els filtres en les cerques en Django
# https://docs.djangoproject.com/en/3.0/ref/models/querysets/#gte


#######
# SQL #
#######

# Eliminar les dades d'una taula es fa millor amb TRUNCATE. Vigilar si té foreigns-keys

# Per esborrar alguns registres...
# DELETE FROM public.tutoria_actuacio WHERE id > 71

# SELECT * FROM public.auth_user WHERE username NOT LIKE ('almn%') ORDER BY username ASC

# Coneixer l'ultim id de la taula que té un registre
# SELECT last_value FROM tutoria_actuacio_id_seq
# https://selleo.com/til/posts/cjxmsvjf0a-how-to-get-a-next-id-for-object

# Obliga al pk de tutoria_actuacio quan l'últim registre és el 71
# ALTER SEQUENCE tutoria_actuacio_id_seq RESTART WITH 72;
# SELECT setval('tutoria_actuacio_id_seq', 71);
# SELECT setval('tutoria_actuacio_id_seq', 72, false);


    #nova_lista = [x for x in [1,2,3,4,5,6] if x < 5]
    #Fica a la bossa els mitjons vermells que hi ha en aquell calaix 
    #bossa = mitjo for mitjo in calaix if mitjo == "vermell"
    #IMPLEMENTAR AIXÒ ON ES PUGUI, que és molt net.
    #actuacions_None = [act for act in actuacions_olddb_list if not act.get('alumne_id')]



'''