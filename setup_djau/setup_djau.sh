#!/bin/bash
# setup_djau.sh
# Configura l'entorn virtual, la base de dades PostgreSQL,
# i personalitza el fitxer settings_local.py per a l'aplicació Django.
# HA D'EXECUTAR-SE des de l'usuari que instal·la l'aplicatiu.

clear

# ----------------------------------------------------------------------
# CÀRREGA DE VARIABLES I FUNCIONS COMUNS ALS SCRIPTS D'AUTOMATITZACIÓ
# ----------------------------------------------------------------------
echo -e "\n"
echo -e "Executant script setup_djau.sh."
echo -e "\n"

echo -e "${C_SUBTITULO}--- Carregant variables i funcions comunes per a la instal·lació ---${RESET}"
echo -e "${C_SUBTITULO}--------------------------------------------------------------------${RESET}"
echo -e "\n"

echo -e "Llegint functions.sh i config_vars.sh."
echo -e "\n"

# 1. CARREGAR LLIBRERIA DE FUNCIONS
source "./functions.sh"

# 2. CARREGAR VARIABLES DE CONFIGURACIÓ
CONFIG_FILE="./config_vars.sh"

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo -e "${C_EXITO}☑️ Variables de configuració carregades.${RESET}"
else
    # Usar variables de color si estan definides en functions.sh
    echo -e "${C_ERROR}❌ ERROR: Fitxer de configuració ($CONFIG_FILE) no trobat. Sortint.${RESET}"
    echo -e "\n"
    exit 1
fi

echo -e "\n\n"
echo -e "${C_PRINCIPAL}=============================================================="
echo -e "${C_PRINCIPAL}--- CONFIGURACIÓ DE DJANGO I BASE DE DADES${RESET} ${CIANO}(setup_djau.sh)${RESET} ${C_PRINCIPAL}---"
echo -e "${C_PRINCIPAL}==============================================================${RESET}"

echo -e "\n\n"
echo -e "${C_CAPITULO}========================================================="
echo -e "${C_CAPITULO}--- 1. ENTORN VIRTUAL (venv) DE DJANGO I REQUERIMENTS ---"
echo -e "${C_CAPITULO}=========================================================${RESET}"
echo -e "\n"

echo -e "${C_SUBTITULO}--- 1.1 Creant Entorno Virtual (venv) ---${RESET}"
echo -e "${C_SUBTITULO}-----------------------------------------${RESET}"

cd "$FULL_PATH"

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip wheel

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR: Fallada en instal·lar l'entorno virtual (venv) o pip o wheel. Sortint.${RESET}"
	echo -e "\n"
    deactivate
	echo -e "\n"
    exit 1
fi
echo -e "\n"
echo -e "${C_EXITO}✅ Entorn virtual creat i els paquets pip i wheel instal·lats.${RESET}"
echo -e "\n"


echo -e "${C_SUBTITULO}--- 1.2 Instal·lant requeriments de Django-Aula ---${RESET}"
echo -e "${C_SUBTITULO}---------------------------------------------------${RESET}"

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR: Fallada en instal·lar les dependències de Python requerides per Django-Aula. Sortint.${RESET}"
	echo -e "\n"
    deactivate
	echo -e "\n"
    exit 1
fi
echo -e "\n"
echo -e "${C_EXITO}✅ Dependències de Python requerides per Django-Aula instal·lades.${RESET}"
echo -e "\n"
sleep 3

echo -e "\n"
echo -e "${C_CAPITULO}=========================================================================="
echo -e "${C_CAPITULO}--- 2. POSTGRESQL, PARÁMETRES PER LA BASE DE DADES I LA SEVA GENERACIÓ ---"
echo -e "${C_CAPITULO}==========================================================================${RESET}"
echo -e "\n"

# 2.1 Sol·licitud de Paràmetres de la Base de Dades

echo -e "${C_SUBTITULO}--- 2.1 Sol·licitud de paràmetres per a la base de dades a PostgreSQL ---${RESET}"
echo -e "${C_SUBTITULO}-------------------------------------------------------------------------${RESET}"

read_prompt "Introduïu el NOM de la BASE DE DADES a PostgreSQL (per defecte: djau_db): " DB_NAME "djau_db"
read_prompt "Introduïu l'USUARI de la BASE DE DADES a PostgreSQL (per defecte: djau): " DB_USER "djau"

# Validació de contrasenyes

read_password_confirm "Introduïu la CONTRASENYA per a l'usuari $DB_USER de la BD a PostgreSQL: " DB_PASS

echo -e "\n"
echo -e "${C_EXITO}☑️ Els paràmetres de la Base de Dades a PostgreSQL han estat definits.${RESET}"
echo -e "\n"
sleep 3

# 2.2 Creació i configuració interna de la base de dades a PostgreSQL

echo -e "${C_SUBTITULO}--- 2.2 Creació i configuració interna de la base de dades a PostgreSQL ---${RESET}"
echo -e "${C_SUBTITULO}---------------------------------------------------------------------------${RESET}"


# Crear l'script SQL temporal
SQL_FILE="temp_setup_${DB_NAME}.sql"

cat << EOF > "$SQL_FILE"
DROP DATABASE IF EXISTS $DB_NAME;
DROP ROLE IF EXISTS $DB_USER;
CREATE DATABASE $DB_NAME;
CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
ALTER DATABASE $DB_NAME OWNER TO $DB_USER;
EOF

echo -e "\n"
echo -e "${C_INFO}--- Executant Script SQL amb 'psql' (NOPASSWD) ---${RESET}"

# S'executa amb NOPASSWD configurat a l'script pare, la sortida es redirigeix a /dev/null
sudo -u postgres psql -t -f "$SQL_FILE" > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR: Fallada en configurar PostgreSQL. Revisi la regla NOPASSWD o la sintaxi SQL.${RESET}"
    rm "$SQL_FILE"
    deactivate
    echo -e "\n"
    exit 1
fi
rm "$SQL_FILE"

echo -e "\n"
echo -e "${C_EXITO}✅ Base de dades '$DB_NAME' i usuari '$DB_USER' configurats a PostgreSQL.${RESET}"
sleep 3

# ----------------------------------------------------------------------
# 3. PERSONALITZACIÓ DEL FITXER settings_local.py
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}========================================================"
echo -e "${C_CAPITULO}--- 3. PERSONALITZACIÓ DEL FITXER${RESET} ${CIANO}settings_local.py${RESET} ${C_CAPITULO}---"
echo -e "${C_CAPITULO}========================================================${RESET}"
echo -e "\n"

# --- 3.1 Sol·licitud de Paràmetres de l'Aplicació (Usuari) ---

echo -e "${C_SUBTITULO}--- 3.1 Preguntes per a la definició de variables i paràmetres crítics per a l'aplicació ---${RESET}"
echo -e "${C_SUBTITULO}--------------------------------------------------------------------------------------------${RESET}"

# 0. Obtenir les dades del centre educatiu
read_prompt "Introduïu el nom del CENTRE EDUCATIU (per defecte: Centre de Demo): " NOM_CENTRE "Centre de Demo"
read_prompt "Introduïu la LOCALITAT del centre educatiu (per defecte: Badia del Vallés): " LOCALITAT "Badia del Vallés"
read_prompt "Introduïu el CODI del centre (per defecte: 00000000): " CODI_CENTRE "00000000"

# 1. Obtenir el domini base (net)
read_prompt "Introduïu el nom de DOMINI o SUBDOMINI per a l'aplicació (ex: djau.elteudomini.cat): " DOMAIN_NAME_CLEAN "djau.elteudomini.cat"

# 2. Definir com estarà funcionant l'entorn on l'aplicació. Tindrà un ús Intern (xarxa local) o serà Públic (exposat a internet)
echo -e "${C_INFO}Quan l'aplicació estigui en producció pot ser servida de dues maneres:${RESET}"
echo -e "${C_INFO}    - o en una XARXA INTERNA (Servidor local dins d'un edifici) per HTTP sense certificats de seguretat SSL.${RESET}"
echo -e "${C_INFO}    - o des d'internet, de forma PÚBLICA per HTTPS, amb certificats auto-signats sense confiança pública o amb certificats gratuïts Let's Encrypt de confiança.${RESET}"
echo -e "\n"

read_prompt "Com vol servir l'aplicació, des d'una XARXA INTERNA (HTTP sense certificats de seguretat SSL) o des d'internet de forma PÚBLICA (HTTPS amb certificats)? Per defecte: PUB (int/PUB): " INSTALL_TYPE "PUB"
INSTALL_TYPE_LOWER=$(echo "$INSTALL_TYPE" | tr '[:upper:]' '[:lower:]')

# 3. Netejar el domini introduït per l'usuari i Definir l'URL d'Accés segons el seu protocol d'accés (PROTOCOL_URL i DOMAIN_CLEAN)
# Neteja forçada: Assegura que no hi ha protocol a DOMAIN_CLEAN, per si l'usuari l'havia afegit.
DOMAIN_CLEAN=$(echo "$DOMAIN_NAME_CLEAN" | sed -e 's|^http[s]*://||')

# Definir l'URL completa (amb protocol http o https), basant-se en el tipus d'instal·lació
if [[ "$INSTALL_TYPE_LOWER" == "int" ]]; then
    PROTOCOL_URL="http://$DOMAIN_CLEAN"
else
    # Per defecte, PÚBLIC sempre utilitza HTTPS (fins i tot si Certbot falla, utilitzarà el Self-Signed)
    PROTOCOL_URL="https://$DOMAIN_CLEAN"
fi

# 4. Generar la llista de ALLOWED_HOSTS (incloent www. ,127.0.0.1 i localhost)
# ----------------------------------------------------------------------------

# 4.1. Comprovació de la variant WWW: Si el domini net NO comença per 'www.', l'afegim.
if [[ "$DOMAIN_CLEAN" != www.* ]]; then
    WWW_DOMAIN="www.$DOMAIN_CLEAN"
else
    WWW_DOMAIN="" # La variant WWW ja és el domini principal.
fi

# 4.2. Construir la llista final d'ALLOWED_HOSTS
ALLOWED_HOSTS_LIST="127.0.0.1,localhost,$DOMAIN_CLEAN"

if [ -n "$WWW_DOMAIN" ]; then
    ALLOWED_HOSTS_LIST="$ALLOWED_HOSTS_LIST,$WWW_DOMAIN"
fi

echo -e "${C_INFO}ℹ️ Llista d'ALLOWED_HOSTS generada: ${CIANO}$ALLOWED_HOSTS_LIST${RESET}"
echo -e "${C_INFO}ℹ️ URL d'Accés generada: ${CIANO}$PROTOCOL_URL${RESET}"
echo -e "\n"

# 5. Definir el correu de l'administrador del domini
read_prompt "Introduïu l'adreça de CORREU de l'administrador (per defecte: ui@mega.cracs.cat): " ADMIN_EMAIL "ui@mega.cracs.cat"

echo -e "${C_EXITO}☑  Variables i paràmetres generals definits.${RESET}"
echo -e "\n"
sleep 2

# --- 3.2 Paràmetres de Correu SMTP (Google/Contrasenya d'Aplicació) ---

echo -e "${C_SUBTITULO}--- 3.2 Paràmetres de Correu SMTP (Google/Contrasenya d'Aplicació) ---${RESET}"
echo -e "${C_SUBTITULO}----------------------------------------------------------------------${RESET}"

echo -e "${C_INFO}ℹ️ Per a l'enviament de correus es requereix una contrasenya d'aplicació de Google.${RESET}"
echo -e "    La informació es pot trobar aquí: ${C_SUBTITULO}'https://support.google.com/mail/answer/185833?hl=es'${RESET}\n"

read_email_confirm "Introduïu el CORREU d'usuari SMTP (EMAIL_HOST_USER): " EMAIL_HOST_USER "djau@elteudomini.cat"
read_password_confirm "Introduïu la CONTRASENYA d'aplicació SMTP (EMAIL_HOST_PASSWORD): " EMAIL_HOST_PASS
read_prompt "Introduïu el CORREU del servidor (SERVER_EMAIL/DEFAULT_FROM_EMAIL) (per defecte: $EMAIL_HOST_USER): " SERVER_MAIL "$EMAIL_HOST_USER"

echo -e "${C_EXITO}☑️ Paràmetres SMTP definits.${RESET}\n"
echo -e "\n"
sleep 2

# --- 3.3 Generant Clau Secreta de Django ---

echo -e "${C_SUBTITULO}--- 3.3 Generant Clau Secreta de Django ---${RESET}"
echo -e "${C_SUBTITULO}-------------------------------------------${RESET}"
echo

# Caràcters a eliminar de forma preventiva per evitar problemes amb SED i Python: '|', '#', '/', '&', '\', '$', i les cometes simples o dobles.
FILTER_CHARS='|#/&\\'\''"$'
MIN_LENGTH=40
MAX_ATTEMPTS=5

echo -e "${C_INFO}ℹ️ A continuació es generarà una clau secreta de 40 caràcters de longitud mínima i s'empraran un màxim de ${MAX_ATTEMPTS} intents per aconseguir-ho. El més habitual és que s'aconsegueixi a la primera.${RESET}"

# ATTEMPT ha de ser 0 per comptar el primer intent com a 1.
ATTEMPT=0
SECRET_KEYPASS_FILTERED=""

# Bucle per intentar generar i filtrar una clau que compleixi la longitud mínima
while [ ${#SECRET_KEYPASS_FILTERED} -lt $MIN_LENGTH ]; do

    ATTEMPT=$((ATTEMPT + 1))

    if [ $ATTEMPT -gt $MAX_ATTEMPTS ]; then
        echo -e "${C_ERROR}❌ ERROR CRÍTIC: No es va poder generar una clau secreta vàlida després de ${MAX_ATTEMPTS} intents. Sortint.${RESET}"
        deactivate
        echo -e "\n"
        exit 1
    fi

    case "$ATTEMPT" in
        1) ORDINAL="1r" ;;
        2) ORDINAL="2n" ;;
        3) ORDINAL="3r" ;;
        4) ORDINAL="4t" ;;
        5) ORDINAL="5è" ;;
        *) ORDINAL="${ATTEMPT}è" ;;
    esac

    # Genera 50 bytes aleatoris, els codifica en base64, i agafa els primers 50 caràcters.
    SECRET_KEYPASS_RAW=$(openssl rand -base64 50 | head -c 50)

    # Filtratge
    SECRET_KEYPASS_FILTERED=$(printf "%s" "$SECRET_KEYPASS_RAW" | tr -d "$FILTER_CHARS")

    # Missatge de l'intent actual
    echo -e "${ORDINAL} intent: Longitud de la clau: ${#SECRET_KEYPASS_FILTERED}"

done

echo -e "${C_EXITO}✅ Clau secreta generada automàticament en el ${ORDINAL} intent amb una longitud de ${#SECRET_KEYPASS_FILTERED} caràcters.${RESET}"
echo -e "\n"
sleep 3

# 3.4 Copiar i Aplicar Substitucions

echo -e "${C_SUBTITULO}--- 3.4 Aplicant Substitucions amb 'sed' ---${RESET}"
echo -e "${C_SUBTITULO}--------------------------------------------${RESET}"

SETTINGS_LOCAL_SAMPLE_FILE="aula/settings_local.sample"
SETTINGS_LOCAL_FINAL_FILE="aula/settings_local.py"

if [ ! -f "$SETTINGS_LOCAL_SAMPLE_FILE" ]; then
    echo -e "${C_ERROR}❌ ERROR: No s'ha trobat l'arxiu d'exemple (sample) a '$SETTINGS_LOCAL_SAMPLE_FILE'. Sortint.${RESET}"
    deactivate
	echo -e "\n"
    exit 1
fi

cp "$SETTINGS_LOCAL_SAMPLE_FILE" "$SETTINGS_LOCAL_FINAL_FILE"

# Aplicant substitucions

#Base de Datos
sed -i "s#^        'NAME': 'djau2025',#        'NAME': '$DB_NAME',#" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s#^        'USER': 'djau2025',#        'USER': '$DB_USER',#" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s#^        'PASSWORD': \"XXXXXXXXXX\",#        'PASSWORD': \"$DB_PASS\",#" "$SETTINGS_LOCAL_FINAL_FILE"

# Variables de l'aplicació:
sed -i "s#^NOM_CENTRE = 'Centre de Demo'#NOM_CENTRE = u'$NOM_CENTRE'#" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s#^LOCALITAT = u\"Badia del Vallés\"#LOCALITAT = u\"$LOCALITAT\"#" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s#^CODI_CENTRE = u\"00000000\"#CODI_CENTRE = u\"$CODI_CENTRE\"#" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s#^URL_DJANGO_AULA = r'http://elteudomini.cat'#URL_DJANGO_AULA = r'$PROTOCOL_URL'#" "$SETTINGS_LOCAL_FINAL_FILE"

# ALLOWED_HOSTS
ALLOWED_HOSTS_PYTHON_LIST="'${ALLOWED_HOSTS_LIST//,/\', \'}'"
sed -i "s#^ALLOWED_HOSTS = \[ 'elteudomini.cat', '127.0.0.1', \]#ALLOWED_HOSTS = [ $ALLOWED_HOSTS_PYTHON_LIST, ]#" "$SETTINGS_LOCAL_FINAL_FILE"

# Clau Secreta i Dades Privades
sed -i "s|^SECRET_KEY = .*|SECRET_KEY = '$SECRET_KEYPASS_FILTERED'|" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s#^PRIVATE_STORAGE_ROOT =.*#PRIVATE_STORAGE_ROOT = '$PATH_DADES_PRIVADES'#" "$SETTINGS_LOCAL_FINAL_FILE"

# Dades d'Email/Admin
sed -i "s#('admin', 'ui@mega.cracs.cat'),#('admin', '$ADMIN_EMAIL'),#" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s#^EMAIL_HOST_USER='el-meu-centre@el-meu-centre.net'#EMAIL_HOST_USER='$EMAIL_HOST_USER'#" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s#^EMAIL_HOST_PASSWORD='xxxx xxxx xxxx xxxx'#EMAIL_HOST_PASSWORD='$EMAIL_HOST_PASS'#" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s#^SERVER_EMAIL='el-meu-centre@el-meu-centre.net'#SERVER_EMAIL='$SERVER_MAIL'#" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s#^DEFAULT_FROM_EMAIL = 'El meu centre <no-reply@el-meu-centre.net>'#DEFAULT_FROM_EMAIL = '$NOM_CENTRE - NO RESPONDER - <$SERVER_MAIL>'#" "$SETTINGS_LOCAL_FINAL_FILE"
sed -i "s/EMAIL_SUBJECT_PREFIX = .*/EMAIL_SUBJECT_PREFIX = '[Comunicació $NOM_CENTRE]'/" "$SETTINGS_LOCAL_FINAL_FILE"

# Lògica per SSL en Django Settings (SESSION/CSRF_COOKIE_SECURE)
if [[ "$INSTALL_TYPE_LOWER" == "int" ]]; then
    # Entorn Intern (HTTP)
    sed -i "s/^SESSION_COOKIE_SECURE=True/SESSION_COOKIE_SECURE=False/" "$SETTINGS_LOCAL_FINAL_FILE"
    sed -i "s/^CSRF_COOKIE_SECURE=True/CSRF_COOKIE_SECURE=False/" "$SETTINGS_LOCAL_FINAL_FILE"
else
    # Entorn Públic (HTTPS)
    sed -i "s/^SESSION_COOKIE_SECURE=False/SESSION_COOKIE_SECURE=True/" "$SETTINGS_LOCAL_FINAL_FILE"
    sed -i "s/^CSRF_COOKIE_SECURE=False/CSRF_COOKIE_SECURE=True/" "$SETTINGS_LOCAL_FINAL_FILE"
fi

echo -e "${C_EXITO}✅ settings_local.py configurat i personalitzat de forma bàsica però funcional.${RESET}"
sleep 3
echo -e "\n"

# 3.5 Opcions avançades de configuracó (settings_local.py)

echo -e "${C_SUBTITULO}--- 3.5 Opcions avançades de configuracó (settings_local.py) ---${RESET}"
echo -e "${C_SUBTITULO}----------------------------------------------------------------${RESET}"

echo -e "${C_INFO}ℹ️ A continuació es poden afegir al fitxer ${NEGRITA}settings_local.py$${RESET}els paràmetres de configuració addicionals (comentats amb el símbol (#).${RESET}"

echo -e "${C_INFO}   Aquests paràmetres inclouen ${NEGRITA}funcionalitats que poden ser clau per l'aplicatiu${RESET}${C_INFO} com ara:${RESET}"
echo -e "${C_INFO}   * ${NEGRITA}Llindars d'alerta automàtica${RESET}${C_INFO} (p. ex., faltes d'assistència que generen avisos).${RESET}"
echo -e "${C_INFO}   * ${NEGRITA}Comportament específic de la lògica de negoci${RESET}${C_INFO} pel centre educatiu.${RESET}"
echo -e "${C_INFO}   * Configuració avançada de logs o cache.${RESET}"
echo -e "\n"
echo -e "${C_INFO}   ${NEGRITA}Recomanació:${RESET} Generalment, és millor incloure'ls (${NEGRITA}SI${RESET}), ja que estaran comentats i no tindran cap efecte, però ${NEGRITA}facilitaran la personalització posterior${RESET} de l'aplicatiu conjuntament amb l'equip directiu.${RESET}"
echo -e "\n"

# --- OPCIONS AVANÇADES DE CONFIGURACIÓ ---
read_prompt "⚙️ Voleu afegir les opcions de parametrització avançada , omentades amb el símbol #, a settings_local.py? (per defecte SI) [SI/no]: " ADVANCED_PARAMS_CHOICE "SI"
ADVANCED_PARAMS_CHOICE_LOWER=$(echo "$ADVANCED_PARAMS_CHOICE" | tr '[:upper:]' '[:lower:]')

if [[ "$ADVANCED_PARAMS_CHOICE_LOWER" == "s" || "$ADVANCED_PARAMS_CHOICE_LOWER" == "si" ]]; then

    echo -e "${C_INFO}ℹ️ Afegint parametritzacions avançades, comentades amb el símbol #, a settings_local.py...${RESET}"

    # 1. Definicions de Rutes (utilitzant les rutes absolutes globals)
    ADVANCED_FILE="$SETUP_DIR/advanced_settings.py"
    LOCAL_SETTINGS_PATH="$FULL_PATH/aula/settings_local.py"

    # 2. Comprovació d'existència (Molt recomanable mantenir-la per evitar errors)
    if [ ! -f "$LOCAL_SETTINGS_PATH" ] || [ ! -s "$ADVANCED_FILE" ]; then
        echo -e "${C_ERROR}❌ ERROR: No s'han trobat els fitxers d'origen/destí per a les parametritzacions avançades. Saltant.${RESET}"
        return 1
    fi

    # 3. Afegir un separador al final de settings_local.py
    echo -e "\n\n# ---------------------------------------------------------------------------------" | sudo -u "$APP_USER" tee -a "$LOCAL_SETTINGS_PATH" > /dev/null
    echo -e "# --- PARAMETRITZACIONS AVANÇADES (Variables del fitxer 'advanced_settings.py') ---" | sudo -u "$APP_USER" tee -a "$LOCAL_SETTINGS_PATH" > /dev/null
    echo -e "# ---------------------------------------------------------------------------------" | sudo -u "$APP_USER" tee -a "$LOCAL_SETTINGS_PATH" > /dev/null

    # 4. Copiar contingut d'advanced_settings.py.
    #    - S'assumeix que advanced_settings.py ja està COMPLETAMENT comentat perquè la importació no afegirà el símbol # davant de cada línia.
    #    - Eliminem el preamble, els imports i la funció 'location' amb 'sed'.
    cat "$ADVANCED_FILE" | sed '1,/location = lambda x: os.path.join(PROJECT_DIR, x)/d' | sudo -u "$APP_USER" tee -a "$LOCAL_SETTINGS_PATH" > /dev/null

    echo -e "${C_EXITO}✅ Parametritzacions afegides. Es trobaran al final de settings_local.py. Descomeni, treient el símbol #, aquelles que siguin necessàries pel seu centre educatiu i modifiqui els seus valors segons les seves necessitats.${RESET}"

else
    echo "⏭️ No s'afegiran les parametritzacions avançades per decissió de l'usuari instal·lador. Sempre es poden afegir manualment després de la instal·lació les que calgui, però ho harurà de fer manualment. Recordi, totes es troben dins de l'arxiu *advanced_settings.py*${RESET}"
fi
# --- FI OPCIONS AVANÇADES ---


# ----------------------------------------------------------------------
# 4. MIGRACIONS I CONFIGURACIÓ D'USUARIS
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}=========================================================="
echo -e "${C_CAPITULO}--- 4. APLICACIÓ DE MIGRACIONS I CONFIGURACIÓ D'USUARI ---"
echo -e "${C_CAPITULO}==========================================================${RESET}"
echo -e "\n"

echo -e "${C_SUBTITULO}--- 4.1 Aplicant Migracions de Base de Dades ---${RESET}"
echo -e "${C_SUBTITULO}------------------------------------------------${RESET}"

python manage.py migrate --noinput

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR: Fallada en aplicar les migraciones. Revisa la connexió de la Base de Dades.${RESET}"
	echo -e "\n"
    deactivate
	echo -e "\n"
    exit 1
fi
echo -e "\n"
echo -e "${C_EXITO}✅ Migracions aplicades correctament.${RESET}"
echo -e "\n"
sleep 3

echo -e "${C_SUBTITULO}--- 4.2 Ejecutant l'script${RESET} ${CIANO}fixtures.sh${RESET} ${C_SUBTITULO}---${RESET}"
echo -e "${C_SUBTITULO}------------------------------------------${RESET}"

if [ -f "scripts/fixtures.sh" ]; then
    bash scripts/fixtures.sh
	echo -e "\n"
    if [ $? -ne 0 ]; then
        echo -e "${C_ERROR}❌ Advertència: Fallada en executar 'scripts/fixtures.sh'.${RESET}"
    fi
    echo -e "${C_EXITO}✅ Fixtures executats.${RESET}"
else
    echo -e "${C_ERROR}❌ scripts/fixtures.sh no s'ha trobat al directori scripts. Pas omès.${RESET}"
fi

echo -e "\n"
sleep 3

echo -e "${C_SUBTITULO}--- 4.3 Creació de Superusuari 'admin' a l'aplicació DJANGO ---${RESET}"
echo -e "${C_SUBTITULO}---------------------------------------------------------------${RESET}"


# 1. Sol·licitar el correu i validar-ne la contrasenya
read_prompt "Introduïu el CORREU ELECTRÒNIC per al superusuari 'admin' de l'aplicació DJANGO: " ADMIN_EMAIL
read_password_confirm "Introduïu la CONTRASENYA per al superusuari 'admin': " ADMIN_PASS

echo -e "${C_INFO}--- Creant Superusuari 'admin' automàticament ---${RESET}\n"

# 2. Crear l'script temporal de Python

PYTHON_SCRIPT="temp_create_admin.py"

cat << EOF > "$PYTHON_SCRIPT"
from django.contrib.auth.models import User
import sys

try:
    # 1. Intentar obtenir l'usuari. Si no existeix, llança l'excepció DoesNotExist.
    try:
        user = User.objects.get(username='admin')

        # 2. Si existeix, actualitzar les seves credencials.
        user.email = '${ADMIN_EMAIL}'
        user.set_password('${ADMIN_PASS}') # set_password gestiona el hashing de la contrasenya
        user.is_superuser = True
        user.is_staff = True
        user.save()
        sys.stdout.write("☑️ Superusuari 'admin' actualitzat correctament.\n")

    except User.DoesNotExist:
        # 3. Si no existeix, crear-lo.
        User.objects.create_superuser(
            username='admin',
            email='${ADMIN_EMAIL}',
            password='${ADMIN_PASS}'
        )
        sys.stdout.write("✅ Superusuari 'admin' creat automàticament.\n")

except Exception as e:
    sys.stdout.write(f"❌ Error en processar superusuari: {e}\n")
    sys.exit(1)
EOF

# 3. execució de l'script

python3 manage.py shell < "$PYTHON_SCRIPT"

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ Error en executar l'script de creació de superusuari. Revisi el log.${RESET}"
fi

rm "$PYTHON_SCRIPT"

echo -e "\n"


echo -e "${C_SUBTITULO}--- 4.4 Creant Grups i assignant l'usuari administrador de Django-Aula 'admin' ---${RESET}"
echo -e "${C_SUBTITULO}----------------------------------------------------------------------------------${RESET}"

PYTHON_SCRIPT="temp_setup_groups.py"

cat << EOF > "$PYTHON_SCRIPT"
from django.contrib.auth.models import User, Group
try:
    g1, _ = Group.objects.get_or_create( name = 'direcció' )
    g2, _ = Group.objects.get_or_create( name = 'professors' )
    g3, _ = Group.objects.get_or_create( name = 'professional' )
    admin_user = User.objects.get( username = 'admin' )
    admin_user.groups.set( [ g1, g2, g3 ] )
    admin_user.save()
    print("✅ Grups creats i assignats a l'usuari 'admin' correctament.")
except Exception as e:
    print(f"❌ Error en configurar grups: {e}")
    exit(1)
EOF

python manage.py shell < "$PYTHON_SCRIPT" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ Fallda en executar l'scriipt de configuració de grups.${RESET}"
fi

rm "$PYTHON_SCRIPT"

echo -e "${C_EXITO}✅ Grups configurats.${RESET}"
sleep 3

# ----------------------------------------------------------------------
# 5. RECOLECCIÓ D'ESTÁTICS I FINALITZACIÓ
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}======================================="
echo -e "${C_CAPITULO}--- 5. RECOLECCIÓ D'ARXIUS ESTÀTICS ---"
echo -e "${C_CAPITULO}=======================================${RESET}"
echo -e "\n"

python manage.py collectstatic -c --no-input

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR: Fallada en recol·lectar arxius estatics.${RESET}"
    deactivate
	echo -e "\n"
    exit 1
fi
echo -e "${C_EXITO}✅ Arxius estàtics recol·lectats.${RESET}"

deactivate
sleep 3

# ===================================================================
# 6. DESAR VARIABLES A config_vars.sh QUE ES FARAN SERVIR DESPRÉS
# ===================================================================

echo -e "\n\n"
echo -e "${C_CAPITULO}====================================================================================="
echo -e "${C_CAPITULO}--- 6. ACTUALITZACIÓ DE L'ARXIU DE VARIABLES COMUNS PELS SCRIPTS D'AUTOMATITZACIÓ ---"
echo -e "${C_CAPITULO}=====================================================================================${RESET}"
echo -e "\n"

echo -e "${C_INFO}--- Afegint variables al fitxer${RESET} ${CIANO}config_vars.sh${RESET} ${C_INFO}automàticament ---${RESET}\n"

# Afegir la nova informació al fitxer (utilitzem >> per a append)
# El fitxer està a $SETUP_DIR

echo "export DB_NAME='$DB_NAME'" >> "$SETUP_DIR/config_vars.sh"
echo "export DB_USER='$DB_USER'" >> "$SETUP_DIR/config_vars.sh"
echo "export LOCALITAT='$LOCALITAT'" >> "$SETUP_DIR/config_vars.sh"

echo "export DOMAIN_CLEAN='$DOMAIN_CLEAN'" >> "$SETUP_DIR/config_vars.sh"                           # El domini pur per a Apache VHosts.
echo "export PROTOCOL_URL='$PROTOCOL_URL'" >> "$SETUP_DIR/config_vars.sh"                           # L'URL amb http o https per al missatge final.
echo "export ALLOWED_HOSTS_LIST='$ALLOWED_HOSTS_LIST'" >> "$SETUP_DIR/config_vars.sh"               # Llista per a ús general/informatiu en Bash (separada per comes).
echo "export ALLOWED_HOSTS_PYTHON_LIST='$ALLOWED_HOSTS_PYTHON_LIST'" >> "$SETUP_DIR/config_vars.sh" # Llista amb format Python per injectar a settings.py (separada per cometes).
echo "export INSTALL_TYPE_LOWER='$INSTALL_TYPE_LOWER'" >> "$SETUP_DIR/config_vars.sh"               # Per a la lògica condicional en un servidor web com Apache.

# Reassignar permisos de forma preventiva
chmod 600 "$SETUP_DIR/config_vars.sh"
chown "$APP_USER":"$APP_USER" "$SETUP_DIR/config_vars.sh"

echo -e "${C_EXITO}✅ Credencials de BD afegides a${RESET} ${CIANO}config_vars.sh${RESET}${C_EXITO}.${RESET}"
echo -e "\n"

echo -e "\n"
echo -e "${C_CAPITULO}===========================================${RESET}"
echo -e "${C_CAPITULO}--- 7. VERIFICACIÓ DE CORREU (Opcional) ---${RESET}"
echo -e "${C_CAPITULO}===========================================${RESET}"
echo -e "\n"

# 1. Donar permisos d'execució al nou script
cd "$SETUP_DIR"
chmod +x ./test_email.sh

read_prompt "¿Vol executar l'script de prova de correu (./test_email.sh) ara? Per defecte NO. (sí/NO): " TEST_EMAIL_NOW "no"

TEST_EMAIL_NOW_LOWER=$(echo "$TEST_EMAIL_NOW" | tr '[:upper:]' '[:lower:]')

if [[ "$TEST_EMAIL_NOW_LOWER" == "sí" ]] || [[ "$TEST_EMAIL_NOW_LOWER" == "si" ]]; then
    echo -e "${C_INFO}ℹ️ Iniciant una prova del sistema de correu configurat per a $EMAIL_HOST_USER...${RESET}"
    bash test_email.sh
else
    echo -e "${C_INFO}ℹ️ Ometent la prova inicial del sistema de correu configurat per a $EMAIL_HOST_USER.${RESET}"
fi

# 2. Informar l'usuari sobre el possible ús futur del fitxer de test de correu.
echo -e "${C_INFO}Sempre pot executar l'script de prova de correu en qualsevol moment des del terminal de Linux amb:${RESET} ${C_SUBTITULO}cd $SETUP_DIR; bash test_email.sh${RESET}"
echo -e "\n"
sleep 2

echo -e "\n"
echo -e "${C_PRINCIPAL}======================================================================================"
echo -e "${C_PRINCIPAL}--- COMPLETADA LA CONFIGURACIÓ BÀSICA GESTIONADA PER A DJANGO-AULA${RESET} ${CIANO}(setup_djau.sh)${RESET} ${C_PRINCIPAL}---"
echo -e "${C_PRINCIPAL}Retornant el control a l'script${RESET} ${CIANO}(install_djau.sh)${RESET}"
echo -e "${C_PRINCIPAL}======================================================================================${RESET}"
echo -e "\n"
