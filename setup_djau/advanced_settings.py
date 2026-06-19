# --- PARAMETRITZACIONS AVANÇADES DE DJAU (Per ser descomentades i personalitzades) ---
# Aquestes variables permeten sobreescriure les configuracions per defecte definides a common.py i settings.py.

# Si no s'han afegit a l'arxiu settings_local.py de forma automàtica en el procés d'instal·lació automatitzat,
# sempre pot copiar i enganxar només les que necessiti i afegir-les a l'arxiu /aula/settings_local.py.

# Els valors aquí reflectits són els valors per defecte de l'aplicació o els més habituals per als centres.

import os
# La funció location s'utilitza per definir rutes de fitxers relatius.
location = lambda x: os.path.join(PROJECT_DIR, x)

# ------------------------------------------------------------------------------------
# 1. SEGURETAT I ACCÉS
# ------------------------------------------------------------------------------------

# Quantitat, per defecte, de logins errònis abans de bloquejar l'usuari (sobreescriu el 3 de common.py)
# LIMITLOGIN = 5

# Temps màxim d'inactivitat (en segons) abans de tancar la sessió.
# CUSTOM_TIMEOUT = 900 # 15 minuts

# Timeout per grup d'usuaris (sobreescriu CUSTOM_TIMEOUT si l'usuari és del grup)
# CUSTOM_TIMEOUT_GROUP = {
#     'consergeria': 4 * 60 * 60,  # 4h
#     'professors': 15 * 60,  # 15'
# }

# ------------------------------------------------------------------------------------
# 2. GESTIÓ D'INCIDÈNCIES I FALTES
# ------------------------------------------------------------------------------------

# Si True, activa la possibilitat de classificar les incidències per tipus.
# Afecta la pantalla d'alertes i el valor unicode de les incidències.
# CUSTOM_TIPUS_INCIDENCIES = False

# Si True, cada retard registrat genera automàticament una incidència.
# CUSTOM_RETARD_PROVOCA_INCIDENCIA = False

# Defineix el tipus d'incidència que genera un retard si l'opció anterior és True.
# CUSTOM_RETARD_TIPUS_INCIDENCIA = {"tipus": "Incidència", "es_informativa": False}

# Frase de la incidència generada automàticament per un retard.
# CUSTOM_RETARD_FRASE = "Ha arribat tard a classe."

# Nombre de dies que es permet crear o modificar una incidència antiga.
# CUSTOM_PERIODE_CREAR_O_MODIFICAR_INCIDENCIA = 90

# Si True, l'acumulació d'incidències obliga al professor que li ha posat a expulsar l'alumne.
# CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO = True

# Nombre de dies que es permet modificar l'assistència (per correcció de professors).
# CUSTOM_PERIODE_MODIFICACIO_ASSISTENCIA = 90

# Dies en els que les incidencies prescriuen.
# CUSTOM_DIES_PRESCRIU_INCIDENCIA = 30

# Dies en els que les expulsions prescriuen.
# CUSTOM_DIES_PRESCRIU_EXPULSIO = 90

# Si True, només el tutor pot justificar faltes dels seus alumnes.
# CUSTOM_NOMES_TUTOR_POT_JUSTIFICAR = True

# Si True, permet copiar el llistat d'assistència des d'una altra hora.
# CUSTOM_PERMET_COPIAR_DES_DUNA_ALTRE_HORA = False

# Si True, gestiona el retard de primera hora pel tutor (en lloc de consergeria/administració).
# CUSTOM_RETARD_PRIMERA_HORA_GESTIONAT_PEL_TUTOR = False

# Faltes d'absència no justificades (en dies) per tal de generar carta base.
# CUSTOM_FALTES_ABSENCIA_PER_CARTA = 15

# Número de faltes no justificades per tal de generar carta, segons el tipus.
# Els tipus de carta es troben a aula/apps/tutoria/business_rules/cartaaabsentisme.py
# CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA = { 'tipus1': 20 }

# Permet concretar quantes faltes són necessàries segons el nivell i el número de la carta.
# Si existeix, invalida CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA.
# CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA = {  # nivell: [faltes per carta1, faltes per carta 2, ...]
#     "ESO": [10, 15, 20],
#     "BTX": [5, 10, 15],
#     "CICLES": [15, 25, 35],
#    # "INFORMATICA": [0],
# }


# ------------------------------------------------------------------------------------
# 3. MÒDULS I FUNCIONALITAT
# ------------------------------------------------------------------------------------

# Activa el mòdul de gestió de sortides i activitats.
# CUSTOM_MODUL_SORTIDES_ACTIU = True

# Si True, deixa ocultes les sortides a les famílies.
# Només s'ha de fer servir si el centre educatiu té un sistema de notificacions i pagaments propi i no vol fer servir el Djau,
# però igualment vol definir les sortides i gestionar l'alumnat i professorat afectat.
# CUSTOM_SORTIDES_OCULTES_A_FAMILIES = False

# Si True, activa si es permet fer servir les quotes.
# CUSTOM_QUOTES_ACTIVES = False

# Nom del tipus de quota per als pagaments de matrícula. Ha d'estar definit a la BD.
# CUSTOM_TIPUS_QUOTA_MATRICULA = None  # Exemple: 'material'

# Si True, permet utilitzar una única definició de quota per a tot l'alumnat de matrícula.
# CUSTOM_QUOTA_UNICA_MATRICULA = False

# Si True, permet que la família pugui modificar els seus paràmetres a l'aplicació.
# CUSTOM_FAMILIA_POT_MODIFICAR_PARAMETRES = False

# Si True, permet a la família enviar comunicats.
# CUSTOM_FAMILIA_POT_COMUNICATS = False

# Si True, activa el mòdul de presència setmanal (graella amb faltes).
# CUSTOM_MODUL_PRESENCIA_SETMANAL_ACTIU = False

# Si False, desactiva la comprovació de "és presència" en el control (només per a configuració avançada)
# CUSTOM_NO_CONTROL_ES_PRESENCIA = False

# Si True, permet als tutors tenir accés als informes de seguiment de faltes i incidències.
# CUSTOM_TUTORS_INFORME = False

# Activa el filtre per mostrar la ruleta d'alumnes a la pantalla de passar llista.
# CUSTOM_RULETA_ACTIVADA = True

# Permet mostrar si l'alumne és major d'edat i quina marca utilitzar.
# CUSTOM_MOSTRAR_MAJORS_EDAT = False
# CUSTOM_MARCA_MAJORS_EDAT = " (^18)"

# Indica la descripció i l'adreça del tutorial per a les famílies.
#    = u"Tutorial disponible a [LA TEVA URL AQUÍ]"

# ------------------------------------------------------------------------------------
# 4. PAGAMENTS I COMERÇ ELECTRÒNIC
# ------------------------------------------------------------------------------------

# Si True, permet realitzar pagaments online (requereix configuració Redsys/entitat)
# CUSTOM_SORTIDES_PAGAMENT_ONLINE = False

# Entorn Redsys: True per a real, False per a proves.
# CUSTOM_REDSYS_ENTORN_REAL = False

# Preu mínim per una sortida per activar el pagament online.
# CUSTOM_PREU_MINIM_SORTIDES_PAGAMENT_ONLINE = 1

# Si True, activa si es permet fer pagament per caixer.
# CUSTOM_SORTIDES_PAGAMENT_CAIXER = True

# Si True, utilitza un formulari de dades reduït per a pagaments.
# CUSTOM_FORMULARI_SORTIDES_REDUIT = True

# Textos d'instruccions de pagament: (S'han mantingut els teus exemples)
# CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT = """Podeu fer el pagament amb targeta de crèdit a qualsevol caixer de CaixaBank, amb el codi de barres o amb el codi entitat: XXXXXXXXXX"""
# CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ENTITAT_BANCARIA = """El pagament s'ha de realitzar als Caixers del Banc Sabadell (qualsevol targeta de qualsevol entitat funciona per realitzar el pagament, no cal tenir compte al Banc) a pagament a tercers i posar el codi de pagament: 5805."""
# CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_EFECTIU = """El pagament s'ha de realitzar en efectiu al professor organitzador de la sortida o al tutor."""
# CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ONLINE = """El pagament s'ha de realitzar a través d'aquesta mateixa plataforma"""

# ------------------------------------------------------------------------------------
# 5. DIVERSOS I LOCALITZACIÓ
# ------------------------------------------------------------------------------------

# Permet definir l'estructura de nivells del centre. (Amb els teus exemples de CICLES)
# CUSTOM_NIVELLS = {
#     "ESO": ["ESO"],
#     "BTX": ["BTX"],
#     "CICLES": ['GA','AF','SMX','DAW','FCT',"CFA","CFI",],
#     "INFORMATICA": ['SMX','DAW'],
# }

# Permet reordenar la llista d'assistència (alumne, grup, cognoms...)
# S'han afegit els teus comentaris d'explicació.
# CUSTOM_ORDER_PRESENCIA = ['alumne']
# Es pot triar entre ['alumne___cognoms','alumne__nom, 'alumne__grup', 'alumne']
# 'alumne': Ordena primer per grup i després per cognom de l'alumnat (alumnes de diferents grups)
# 'alumne nom': Ordena l'alumnat per nom
# 'alumne_cognom': Ordena l'alumant per cognoms

# Formats de temps i data. S'activa a nivell de sistema operatiu.
# CUSTOM_LC_TIME = 'ca_ES.utf8'
# CUSTOM_DATE_FORMAT = "%-d %B de %Y"  # Exemple: '5 d'abril de 1999'

# Quantitat màxima de destinataris per cada email, depèn del servidor de correu
# CUSTOM_MAX_EMAIL_RECIPIENTS = 100

# Per afegir altres dades dels alumnes des de Sincronitza / Dades addicionals alumnat.
# CUSTOM_DADES_ADDICIONALS_ALUMNE = [
#     {
#         'label': 'Drets imatge',
#         'esautoritzacio': True,
#         'visibilitat': ['Familia','Professor'],
#     },
#     {
#         'label': 'Autorització sortides',
#         'esautoritzacio': True,
#         'visibilitat': ['Familia','Professor'],
#     },
#     {
#         'label': 'Salut i Escola',
#         'esautoritzacio': True,
#         'visibilitat': ['Familia','Professor'],
#     },
#     {
#         'label': 'Responsable Preferent',
#         'esautoritzacio': False,
#         'visibilitat': ['Tutor'],
#     },
#     {
#         'label': 'Dades mèdiques',
#         'esautoritzacio': False,
#         'visibilitat': ['Familia','Professor'],
#     },
# ]

# ------------------------------------------------------------------------------------
# 6. CONFIGURACIÓ TÈCNICA AVANÇADA
# ------------------------------------------------------------------------------------

# Llista de grups d'usuaris que poden veure les fotos d'alumnes.
# CUSTOM_GRUPS_PODEN_VEURE_FOTOS = ["direcció", "professors", "consergeria"]

# Tipus MIME permesos per a les fotos.
# CUSTOM_TIPUS_MIME_FOTOS = ["image/gif", "image/jpeg", "image/png"]

# Per al càlcul d'indicadors: Alumnes amb absències de més del <percentatge> de les hores lectives del trimestre.
# CUSTOM_INDICADORS = [
#     # [inici_curs, Final 1Trim, Final 2Trim, Final 3Trim, nivell, %, controls ],
#     # Exemple 1: Compta Faltes (F) i Justificades (J) per ESO.
#     ['13/09/2024', '29/11/2024', '06/03/2025', '19/06/2025', 'ESO', 25],
#     # Exemple 2: Només compta les Faltes (F) per ESO.
#     ['13/09/2024', '29/11/2024', '06/03/2025', '19/06/2025', 'ESO', 5, ('F')],
#     # Exemple 3: Compta Faltes (F), Justificades (J) i Retards (R) per CICLES.
#     ['13/09/2024', '29/11/2024', '06/03/2025', '29/05/2025', 'CICLES', 10, ('F','J','R')],
# ]
