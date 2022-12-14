from django.shortcuts import render, redirect, HttpResponse
from django.db import OperationalError, DatabaseError, connections
from django.contrib.auth.models import User
from copy import deepcopy
from aula.utils.my_paginator import DiggPaginator
from django.template.defaulttags import register

#auth
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

#models
from aula.apps.alumnes.models import Alumne
from aula.apps.tutoria.models import Actuacio

#forms
from aula.apps.importaActuacions.forms import dades_dboldForm

#tables
from django_tables2.config import RequestConfig
from aula.apps.importaActuacions.table2_models import Table2_llista_actuacions

# Per afegir i/o eliminar bases de dades a la configuració
from aula import settings_local


############################
# PROCEDIMENT D'IMPORTACIÓ #
############################

# 1r PAS. CONNEXIÓ DB OLD. Cal connectar-se a la base de dades del curs anterior per extreure les dades.
# 2n PAS. SINCRONITZAR PROFESSIONALS. Els usernames dels professionals del curs anterior no tenen per què coincidir
        # amb els del curs actual, encara que siguin els mateixos professionals.
# 3r PAS. EXTRACCIÓ DE DADES. Lectura de les dades significatives, tant de la BD antiga com de l'actual.
# 4t PAS. 1r CANVI. Amb les dades de la BD antiga:
    # 4.1 Substitució dels usernames antics dels professionals pels actuals usernames.
    # 4.2 Substitució de l'identificador de l'alumne pel RALC, que és universal.
    #   POSSIBLE MILLORA: Es podria contemplar el cas que un alumne no tinguin RALC? Només en aquest cas, caldria estirar les dades del nom i cognoms, però sempre és molt més insegur i amb confirmació expressa.
    # 4.3 Substitució de l'identificador del professional pel seu username.
    #   Cal assegurar-se que hi haurà el mateix username a la BD antiga i a l'actual
    #   perquè sigui universal, o bé modificant els usernames manualment en l'administració,
    #   o bé mitjançant un formulari de comparació (TO DO)
# 5é PAS. 2n CANVI. Amb les dades de la BD actual:
    # 5.1 Substitució del RALC de l'alumne pel valor de l'identificador.
    # 5.2 Substitució de l'username del professional pel seu identificador.
# 6é PAS. PREPARANT LA INSERCIÓ de les dades tractades a la BD actual.
# 7é PAS. INSERCIÓ de les actuacions antigues a la BD actual.


# Variables globals per traspassar informació entre funcions
dades_connexio_dbold = {}                           # Dades de connexió de la DB origen de les actuacions a importar
usernames_oldb_to_usernames_curs_actual_dict = []   # La correspondència dels usernames dels professionals entre bases de dades
actuacions_a_importar = []                          # Les actuacions que finalment seran importades
actuacions_pel_bulkcreate = []


def check_database_connection(request):
    global dades_connexio_dbold
    nom_dbold = dades_connexio_dbold.get('name_dbold')
    usuari_dbold = dades_connexio_dbold.get('user_dbold')

    if nom_dbold in settings_local.DATABASES:
        db_conn = connections[nom_dbold]
        try:
            cursor = db_conn.cursor()       # Create a cursor object using the database connection
            cursor.execute('SELECT 1')      # Run a query to check if the connection is working
            result = cursor.fetchone()[0]   # Fetch the result of the query
            cursor.close()
        except OperationalError:
            return render(
                request,
                '../templates/errorConnexio.html', 
                {
                'nom':nom_dbold,
                'usuari':usuari_dbold,
                },)
    else:
        return render(request,'404.html',{},)
    return None

# Per poder renderitzar en un template un diccionario que té clau variable
@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)


############################
# 1r PAS # CONNEXIÓ DB OLD #
############################

@login_required
@group_required(['direcció','administradors'])
def connexioDBold(request):
    
    if request.method == 'POST':
        
        form = dades_dboldForm(request.POST)        
        if form.is_valid():
            global dades_connexio_dbold
            dades_connexio_dbold = {
                'name_dbold':form.cleaned_data['nom'],
                'user_dbold':form.cleaned_data['usuari'],
                'pass_dbold':form.cleaned_data['contrasenya'],
                }

            settings_local.DATABASES[dades_connexio_dbold.get('name_dbold')] = {
                'ENGINE': 'django.db.backends.postgresql_psycopg2',
                'NAME': dades_connexio_dbold.get('name_dbold'),
                'USER': dades_connexio_dbold.get('user_dbold'),
                'PASSWORD': dades_connexio_dbold.get('pass_dbold'),
                'HOST': 'localhost',
                'PORT': '5432',
                'ATOMIC_REQUESTS': False,
                'AUTOCOMMIT': True,
                'CONN_MAX_AGE': 0,
                'OPTIONS': {},
                'TIME_ZONE': None
            }

            connexio = check_database_connection(request)
            if connexio is None:
                return redirect('/importaActuacions/sincronitzaProfessionals')
            else:
                return connexio
             
    else:
        head = u"Importació de les actuacions d'un altre curs al curs actual"
        titol_formulari =u"Paràmetres de connexió amb la base de dades del curs anterior."
        form = dades_dboldForm()
        
    return render(
                request,
                'connexioDBold.html',
                {
                    'form': form,
                    'head': head,
                    'titol_formulari':titol_formulari,
                },
            )

#######################################
# 2n PAS # SINCRONITZAR PROFESSIONALS #
#######################################

@login_required
@group_required(['direcció','administradors'])
def sincronitzaProfessionals(request):
    global dades_connexio_dbold
    global usernames_oldb_to_usernames_curs_actual_dict
    nom_dbold = dades_connexio_dbold.get('name_dbold')

    # Redirecció si hi ha un accès indegut i conseqüent error en la connexió a la BD antiga
    connexio = check_database_connection(request)
    if connexio is not None:
        return connexio

    head = u"Sincronització entre cursos dels professionals del centre educatiu"

    usuaris_olddb_id_username_firstname_lastname_list = list(User.objects.
        using(nom_dbold).
        values_list('id', 'username', 'first_name', 'last_name').
        exclude(username__startswith = 'almn').
        exclude(username__startswith = 'admin').
        exclude(username__startswith = 'conser').
        exclude(username = 'TP').
        order_by('username'))
        
    usuaris_id_username_firstname_lastname_list = list(User.objects.
        values_list('id', 'username', 'first_name', 'last_name').
        exclude(username__startswith = 'almn').
        exclude(username__startswith = 'admin').
        exclude(username__startswith = 'conser').
        exclude(username = 'TP').
        order_by('username'))

    actuacions_professionalid_olddb_list_tuples = list(Actuacio.objects.
        using(nom_dbold).
        values_list('professional_id'))
    
    actuacions_professionalid_olddb_list = []
    actuacions_professionalid_olddb_list = [actuacio[0] for actuacio in actuacions_professionalid_olddb_list_tuples]
    del actuacions_professionalid_olddb_list_tuples

    # Netejar la llista per quedar-se amb els valors únics.
    professionals_amb_actuacions_olddb_list = list(set(actuacions_professionalid_olddb_list))

    for i, identificador_professional in enumerate(professionals_amb_actuacions_olddb_list):
        for usuari in usuaris_olddb_id_username_firstname_lastname_list:
            if identificador_professional == usuari[0]:
                professionals_amb_actuacions_olddb_list[i] = usuari
                break

    usernames_usuaris = []              # Llista dels usernames dels usuaris actuals
    usernames_usuaris_orfes_oldb = []   # Llista dels useranames dels usuaris antics que no es troben al curs actual
    professionals_repetits = []         # Per controlar que no s'associen un professional actual amb més d'un profesional antic

    # Només em quedo els usernames. La resta per renderritzar en el template
    usernames_usuaris = [usuari[1] for usuari in usuaris_id_username_firstname_lastname_list]

    # Filtre per trobar els usuaris antics que han quedat sense relacionar
    usernames_usuaris_orfes_oldb = [usuari_oldb for usuari_oldb in professionals_amb_actuacions_olddb_list if usuari_oldb[1] not in usernames_usuaris]

    if request.method == 'POST':

        # Es recull la relació entre els professionals antics i actuals, eliminant la primera entrada.
        usernames_oldb_to_usernames_curs_actual_dict = dict(request.POST)
        usernames_oldb_to_usernames_curs_actual_dict.pop('csrfmiddlewaretoken')
        usernames_claus = list(dict.keys(request.POST))
        usernames_claus.pop(0)
        
        # Si algun professinal s'ha deixat sense relacionar, es millor que mantingui el seu propi username.
        # Els valors del diccionari son llistes d'un sol element =:-O Aprofito per eliminar aquestes llistes.  
        for clau in usernames_claus:
            username_associat_list = usernames_oldb_to_usernames_curs_actual_dict.get(clau)
            if not username_associat_list[0]: username_associat_list[0] = clau
            usernames_oldb_to_usernames_curs_actual_dict[clau] = username_associat_list[0]
        
        # Únic procediment per trobar associacions duplicades que m'ha funcionat
        visited = set()
        professionals_repetits = [x for x in list(dict.values(usernames_oldb_to_usernames_curs_actual_dict)) if x in visited or (visited.add(x) or False)]

        if not professionals_repetits:
            return redirect('/importaActuacions/importantActuacions')

    return render(
        request,
        '../templates/sincronitzaProfessionals.html', 
        {
            'head':head,
            'usuaris_orfes_oldb':usernames_usuaris_orfes_oldb,
            'usuaris_curs_actual':usuaris_id_username_firstname_lastname_list,
            'professionals_repetits':professionals_repetits,
            'assignacio_anterior':usernames_oldb_to_usernames_curs_actual_dict,
        },)


@login_required
@group_required(['direcció','administradors'])
def importantActuacions(request):

    global dades_connexio_dbold
    global usernames_oldb_to_usernames_curs_actual_dict
    nom_dbold = dades_connexio_dbold.get('name_dbold')

    # Redirecció si hi ha un accès indegut i conseqüent error en la connexió a la BD antiga
    connexio = check_database_connection(request)
    if connexio is not None:
        return connexio
    if not usernames_oldb_to_usernames_curs_actual_dict:    # Per evitar un accès amb url directe
        return render(request,'404.html',{},)
    
    head = u"Llistat detallat de les actuacions que s'importaran des d'un altre curs."

    # Informació a mostrar en el template.
    actuacions_sense_alumne_curs_actual = []    # Actuacions especials donat que NO s'importaran a la BD del curs actual.
    actuacions_sense_professional = []          # actuacions especials donat se'n modificarà el seu text i SÍ que s'importaran a la BD del curs actual.
    alumnes_desmatriculats = []                 # Alumnat que ja no hi és.
    professionals_foracentre = []               # Professionals que ja no hi son.

    ###############################
    # 3r PAS # EXTRACCIÓ DE DADES #
    ###############################

    # Dades de l'alumnat
    alumnes_id_ralc_nom_cognoms_list = list(Alumne.objects.
        values_list('id', 'ralc', 'nom', 'cognoms').
        order_by('cognoms'))

    alumnes_olddb_id_ralc_nom_cognoms_list = list(Alumne.objects.
        using(nom_dbold).
        values_list('id', 'ralc', 'nom', 'cognoms').
        order_by('cognoms'))

    # Dades dels professionals
    usuaris_username_id = dict(User.objects.
        values_list('username','id').
        exclude(username__startswith = 'almn').
        order_by('username'))

    usuaris_olddb_id_username_firstname_lastname_llista_de_tuples = list(User.objects.
        using(nom_dbold).
        values_list('id', 'username', 'first_name', 'last_name').
        exclude(username__startswith = 'almn').
        exclude(username__startswith = 'admin').
        exclude(username__startswith = 'conser').
        exclude(username = 'TP').
        order_by('username'))

    # Conversió de les tuples en llistes, per poder modificar els valors.
    usuaris_olddb_id_username_firstname_lastname_list = []
    usuaris_olddb_id_username_firstname_lastname_list = [list(usuari) for usuari in usuaris_olddb_id_username_firstname_lastname_llista_de_tuples]
    del usuaris_olddb_id_username_firstname_lastname_llista_de_tuples

    # Dades de les actuacions
    actuacions_olddb_list = list(Actuacio.objects.
        using(nom_dbold).
        values().
        order_by('id'))

    actuacions_id_data_alumneid_list = list(Actuacio.objects.
        values_list('id', 'moment_actuacio', 'alumne_id').
        order_by('id'))


    ##############################
    # 4t PAS # 1r CANVI # OLD BD #
    ##############################

    # 4.1 Substitució dels usernames antics dels professionals pels actuals usernames.
    for professional in usuaris_olddb_id_username_firstname_lastname_list:
        username_oldb_professional = professional[1]
        if usernames_oldb_to_usernames_curs_actual_dict.get(username_oldb_professional):
            username_professional = usernames_oldb_to_usernames_curs_actual_dict.get(username_oldb_professional)
            professional[1] = username_professional

    # Substitucions a les actuacions
    for actuacio in actuacions_olddb_list:

        # 4.2 Substitució de l'identificador de l'alumne pel RALC, que és universal.
        # El camps alumne_id té foreign_key amb el camp id de la taula alumnes_alumne.
        # No obstant es deixa la marca (None) si no es trobés l'alumne al llistat general d'alumnes.
        identificador_alumne = actuacio.get('alumne_id')
        for alumne in alumnes_olddb_id_ralc_nom_cognoms_list:                   
            if identificador_alumne == alumne[0]:
                ralc_alumne = alumne[1]
                nom_alumne = alumne[2]
                cognoms_alumne = alumne[3]
                actuacio.update({'alumne_id':ralc_alumne})
                actuacio.update({'nom_alumne':nom_alumne})
                actuacio.update({'cognoms_alumne':cognoms_alumne})
                

        # 4.3 Substituint l'identificador del professional per l'username,
        # El camp professional_id té foreign_key amb algun lloc que no he sabut trobar
        # No obstant es deixa la marca (None) si no es trobés el professional al llistat general d'usuaris.
        identificador_professional = actuacio.get('professional_id')
        for professional in usuaris_olddb_id_username_firstname_lastname_list:
            if identificador_professional == professional[0]:
                username_professional = professional[1]
                nom_professional = professional[2]
                cognoms_professional = professional[3]
                #Valorar si no fer-ho i afegir-ho per codi al template emprant professionals_foracentre
                actuacio.update({'professional_id':username_professional})
                actuacio.update({'nom_professional':nom_professional})
                actuacio.update({'cognoms_professional':cognoms_professional})
                

    #################################
    # 5é PAS # 2n CANVI # BD ACTUAL #
    #################################

    for actuacio in actuacions_olddb_list:

        # Substituint el ralc de l'actuació per l'identificador de l'alumne a la nova BD.
        # Si no troba l'alumne és que no s'ha maticulat, se'n guarden algunes dades
        # i es deixa la marca (None) per excloure-la més endavant amb facilitat.

        ralc_alumne = actuacio.get('alumne_id') # Després del 1r canvi, el camp alumne_id conté el ralc, no l'alumne_id
        identificador_alumne = False
        for alumne in alumnes_id_ralc_nom_cognoms_list:
            if ralc_alumne == alumne[1]:
                identificador_alumne = alumne[0]
            
        if ralc_alumne and identificador_alumne:
            actuacio.update({'alumne_id':identificador_alumne})
        elif ralc_alumne and not identificador_alumne: # Si l'alumne ja no hi és, és un alumne desmatriculat.

            # Guardem les actuacions associades a alumnes desmatriculats en una llista específica.
            actuacions_sense_alumne_curs_actual.append(deepcopy(actuacio))

            # Guardem els ralcs, noms i cognoms dels alumnes ara desmatriculats que tenen actuacions a la BD antiga
            for alumne in alumnes_olddb_id_ralc_nom_cognoms_list:
                if ralc_alumne == alumne[1]:
                    nom_alumne = alumne[2]
                    cognoms_alumne = alumne[3]
                    dades_alumne_desmatriculat = {'ralc':ralc_alumne,'nom':nom_alumne,'cognoms':cognoms_alumne}
                    if not alumnes_desmatriculats or dades_alumne_desmatriculat not in alumnes_desmatriculats:
                        alumnes_desmatriculats.append(dades_alumne_desmatriculat)
                    
            actuacio.update({'alumne_id':None}) # Marcada per a no importar-la a la BD nova

        # Substituint l'username del professional pel seu identificador a la nova BD,
        username_professional = actuacio.get('professional_id') # Després del 1r canvi, el camp professional_id conté l'username, no l'identificador del professional
        identificador_professional = usuaris_username_id.get(username_professional)
        if username_professional and identificador_professional:
            actuacio.update({'professional_id':identificador_professional})
        elif username_professional and not identificador_professional: # Si el professional ja no és al centre...

            # Guardem les actuacions sense profesional a la BD nova en una llista específica.
            actuacions_sense_professional.append(deepcopy(actuacio))

            # Guardem els usernames, noms i cognoms, dels professionals que ja no hi son al centre.
            for professional in usuaris_olddb_id_username_firstname_lastname_list:
                if username_professional == professional[1]:
                    nom_professional = professional[2]
                    cognoms_professional = professional[3]
                    dades_professional_foracentre = {'username':username_professional,'nom':nom_professional,'cognoms':cognoms_professional}
                    if not professionals_foracentre or dades_professional_foracentre not in professionals_foracentre:
                        professionals_foracentre.append(dades_professional_foracentre)

                    # S'afegeix una frase a l'inici del text de l'actuació per deixar constància de qui i quan es va fer l'actuació.
                    text_actuacio  = u'El o la professional '+nom_professional+' '+cognoms_professional
                    text_actuacio += ' ('+username_professional+')'
                    text_actuacio += ' va redactar aquesta actuació però ja no es troba al centre educatiu.'
                    text_actuacio += ' No obstant, a continuació se\'n mostra el text original: \n\n'
                    text_actuacio += actuacio.get('actuacio')

                    actuacio.update({'actuacio':text_actuacio})
                    
            
            # S'elimina l'username del camp professional_id. Aquest camp pot ser NULL a la BD.
            actuacio.update({'professional_id':None})

    ##################################
    # 6é PAS # PREPARANT LA INSERCIÓ #
    ##################################

    actuacions_ja_importades = []
    global actuacions_a_importar
    actuacions_a_importar = []

    for actuacio_olddb in actuacions_olddb_list:
        if actuacio_olddb.get('alumne_id')!=None:     # Només s'hi afegiran totes les actuacions associades a un alumne matriculat en el curs actual.

            # Comprovació para no importar una actuació que ja va ser importada per algú
            # la data exacta és gairebé impossible que es pugui repetir perquè haurien d'haver-hi dues actuacions creades en el mateix segon.
            data_actuacio_a_importar = actuacio_olddb.get('moment_actuacio')
            coincidencia = False
            for actuacio in actuacions_id_data_alumneid_list:
                data_actuacio_curs_actual = actuacio[1]
                if data_actuacio_a_importar == data_actuacio_curs_actual:
                    coincidencia = True
                
            if not coincidencia:
                actuacions_a_importar.append(actuacio_olddb)
            else:
                actuacions_ja_importades.append(actuacio_olddb)

    return render(
        request,
        '../templates/importacio.html', 
        {
        'nom_dbold':nom_dbold,
        'head':head,
        'alumnes_desmatriculats':alumnes_desmatriculats,
        'actuacions_sense_alumne_curs_actual':actuacions_sense_alumne_curs_actual,
        'professionals_foracentre':professionals_foracentre,
        'actuacions_sense_professional':actuacions_sense_professional,
        'actuacions_olddb_list':actuacions_olddb_list, 
        'actuacions_ja_importades': actuacions_ja_importades,
        'actuacions_a_importar': actuacions_a_importar,
        },)


#####################
# 7é PAS # INSERCIÓ #
#####################

@login_required
@group_required(['direcció','administradors'])
def importacio(request):

    global actuacions_a_importar
    global actuacions_pel_bulkcreate

    head = u"Resultats de la importació de les actuacions d'un curs anterior"

    # Redirecció si hi ha un accès indegut i conseqüent error en la connexió a la BD antiga
    connexio = check_database_connection(request)
    if connexio is not None:
        return connexio
    if not actuacions_a_importar:
        return render(request,'404.html',{},)
    
    if request.method == 'POST':
        actuacions_pel_bulkcreate.clear()

        # Es decideix afegir-hi l'id per facilitar esborrar les actuacions afegides si quelcom ha anat malament.
        # PERFER: Una taula amb checkbox per esborrar les actuacions afegides, habilitant el checkbox només d'aquestes actuacions.
        ultim_id_abans_actualitzacio = (Actuacio.objects.last()).id
        identificador_nova_actuacio = ultim_id_abans_actualitzacio + 1

        # Preparació de les dades a inserir
        for actuacio in actuacions_a_importar:
            act = Actuacio(
                id = identificador_nova_actuacio,
                moment_actuacio = actuacio.get('moment_actuacio'),
                qui_fa_actuacio = actuacio.get('qui_fa_actuacio'),
                amb_qui_es_actuacio = actuacio.get('amb_qui_es_actuacio'),
                assumpte = actuacio.get('assumpte'),
                actuacio = actuacio.get('actuacio'),
                alumne_id = actuacio.get('alumne_id'),
                professional_id = actuacio.get('professional_id'),
            )
            actuacions_pel_bulkcreate.append(act)
            identificador_nova_actuacio += 1

        # Inserció de les actuacions de la BD antiga a la BD actual (per fi, badum txas!)
        Actuacio.objects.bulk_create(actuacions_pel_bulkcreate)

    # PER ARREGLAR: Renderitzar dues taules paginades amb table2 al mateix template provoca que quan es pagina una taula, l'altra es pagina igual.

    # Per mostrar, un últim cop, les actuacions que s'han importat.
    table_actuacions_importades = Table2_llista_actuacions(actuacions_pel_bulkcreate) 
    table_actuacions_importades.order_by = '-id_actuacio'  
    RequestConfig(request, paginate={"paginator_class":DiggPaginator , "per_page": 20}).configure(table_actuacions_importades)

    # Per mostrar cóm ha queat finalment la taula de les actuacions
    actuacions = Actuacio.objects.all()
    table = Table2_llista_actuacions(actuacions) 
    table.order_by = '-id_actuacio'  
    RequestConfig(request, paginate={"paginator_class":DiggPaginator , "per_page": 20}).configure(table)

    return render(
                    request,
                    '../templates/resultatImportacio.html', 
                    {
                        'head': head,
                        'table': table,
                        'table_actuacions_importades': table_actuacions_importades,
                    }
                )