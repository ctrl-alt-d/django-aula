#!/bin/bash
# install_djau.sh
# Script Principal per la Instal·lació de l'aplicatiu Django-Aula.
# S'encarrega de la configuració del sistema, usuaris i permisos, i de descarregar tot allò necessari pel funcionament de l'aplicatiu.
# Ha d'executar-se amb privilegis de root (p. ej., sudo bash install_djau.sh).

clear

# ------------------------------------------------------------------------------
# DEFINICIÓ DE VARIABLES, CÀRREGA DE LLIBRERIA DE FUNCIONS I VARIABLES DE COLORS
# ------------------------------------------------------------------------------


# 1. Definició de variables
# Repositori i branca per la clonació
REPO_URL="https://github.com/ctrl-alt-d/django-aula.git"	# repositori del projecte
GIT_BRANCH="master"						# Si es vol instal·lar una branca concreta. Exemple: "feat/upgrade-bootstrap"

# Definició de sistema d'inicialització de processos del Sistema Operatiu (SysVinit vs Systemd)
IS_SYSTEMD=0 # Per defecte, assumim que no és systemd (Debian, etc.)

if command -v systemctl >/dev/null 2>&1; then
    # La comanda systemctl s'ha trobat: és un sistema amb systemd (Debian, Ubuntu o derivats)
    IS_SYSTEMD=1
fi


echo "---------------------------------------------------------------------------------------------------------"
echo "--- Descàrrega de la llibreria functions.sh. Es farà servir temporalment a l'inici de la instal·lació ---"
echo "---------------------------------------------------------------------------------------------------------"

# 1. Definició de l'URL remota de la llibreria de funcions
REPO_BASE_CLEAN="${REPO_URL%.git}"
RAW_BASE="${REPO_BASE_CLEAN/https:\/\/github.com/https:\/\/raw.githubusercontent.com}"
FUNCTIONS_URL="${RAW_BASE}/${GIT_BRANCH}/setup_djau/functions.sh"
FUNCTIONS_FILE="./functions.sh"


echo -e "\n"
echo "ℹ️ Descarregant la llibreria temporal de funcions i variables compartides ($FUNCTIONS_FILE). El contingut de l'arxiu és important pel bon funcionament de tots els scripts que calen per la instal·lació automàtica de Django-Aula."
echo "  Aquesta descàrrega tindrà un ús temporal, donat que l'arxiu definitiu romandrà permanentment dins un directori de la instal·lació de l'aplicatiu, un cop s'hagi clonat des del repositori oficial."

# 2. Descàrrega de la llibreria de funcions amb wget
wget -q -O "$FUNCTIONS_FILE" "$FUNCTIONS_URL"

if [ $? -ne 0 ]; then
    echo -e "\n"
    echo "❌ ERROR: No s'ha pogut descarregar l'arxiu temporal de funcions des de $FUNCTIONS_URL. Sense aquestes funcions el script no pot executar-se. Sortint."
    exit 1
fi

# 3. Canvi de propietat: Assignar l'arxiu descarregat a l'usuari original que ha executat 'sudo'
if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
    chown "$SUDO_USER":"$SUDO_USER" "$FUNCTIONS_FILE"
fi

# 4. Càrrega de la llibreria de funcions
source "$FUNCTIONS_FILE"

# Variables de color ($C_EXITO, $C_ERROR, etc.) i funcions comunes disponibles.
echo -e "\n"
echo -e "${C_EXITO}✅ Llibreria de funcions temporal carregada amb èxit.${RESET}"

rm "$FUNCTIONS_FILE"

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ADVERTÈNCIA:Per alguna raó desconeguda no s'ha pogut eliminar l'arxiu temporal de funcions${RESET} ${C_INFO} '$FUNCTIONS_FILE'${RESET} ${${C_ERROR}}. Caldria fer-ho manualment.${RESET}"
else
echo -e "${C_EXITO}❌ Un cop importat el contingut de la l'arxiu temporal de funcions s'ha procedit a la seva automàtica eliminació.${RESET}"
fi

echo -e "\n\n"

echo -e "${C_INFO}Detecció del sistema d'inici del sistema operatiu instal·lat (Systemd vs SysVinit).${RESET}"
echo

if [ "$IS_SYSTEMD" -eq 1 ]; then
    # 🟢 Sistema systemd (Ubuntu, Debian modern)
    echo "ℹ️ S'ha detectat un sistema operatiu basat en Systemd (Debian modern, Ubuntu i derivats)"
else
    # 🟡 Sistema SysVinit (Devuan) o similar
    echo "ℹ️ S'ha detectat un sistema operatiu basat en SysVinit. (Probablement Devuan o similar)".
fi
echo

echo -e "\n\n"

read -p "Premi qualsevol tecla per veure la informació sobre el procés d'instal·lació de Django-Aula" -n1 -s

clear

echo -e "\n"
echo -e "${C_CAPITULO}===================================================================${RESET}"
echo -e "${C_CAPITULO}--- FLUX D'INSTAL·LACIÓ AUTOMATIZADA DE L'APLICACIÓ DJANGO-AULA ---${RESET}"
echo -e "${C_CAPITULO}===================================================================${RESET}"
echo -e "\n"

echo -e "${C_EXITO}--- FASE 1: INSTAL·LACIÓ I CONFIGURACIÓ DE DJANGO-AULA, AMB LES SEVES DEPENDÈNCIES I BASE DE DADES ---${RESET}"
echo -e "    ${NEGRITA}PRIMERA ACCIÓ:${RESET} Execució inicial de l'script mestre, obtingut directament del repositori de Github."
echo -e "      \$ ${C_SUBTITULO}sudo bash install_djau.sh${RESET}"
echo -e "    ${VERDE}FUNCIÓ:${RESET} Crea directoris, configura permisos d'usuaris, instal·la dependèncias i clona el repositori."
echo -e "\n"
echo -e "    ${NEGRITA}SEGONA ACCIÓ:${RESET} S'executa automàticament l'script ${C_INFO}setup_djau.sh${RESET} (sense haver-ho de fer l'usuari instal·lador)."
echo -e "    ${VERDE}FUNCIÓ:${RESET} Crea la Base de Dades (BD) en PostgreSQL, configura l'entor virtual de Python (venv), personalitza ${C_INFO}settings_local.py${RESET},"
echo -e "            du a terme les migracions, crea el superusuari de Django i prepara la BD pel centre educatiu."
echo -e "\n"

echo -e "${C_EXITO}--- FASE 2: SERVIDOR WEB I CERTIFICATS SSL ---${RESET}"
echo -e "    ${NEGRITA}ACCIÓ:${RESET} L'usuari ha de canviar manualment al directori on ha instal·lat Django-Aula, com exemple ${C_INFO}/opt/djau/setup_djau${RESET} i executar el següent script:"
echo -e "      \$ ${C_SUBTITULO}sudo bash setup_apache.sh${RESET}"
echo -e "    ${VERDE}FUNCIÓ:${RESET} Instal·la el servidor web Apache, crea els arxius de connexió ${NEGRITA}VHOST${RESET} per la instal·lació triada (xarxa local o pública amb domini),"
echo -e "            i crea els certificats SSL per connexions segures encriptades, autosignats o amb l'entitat certificadora gratuïta de Let's Encrypt."
echo -e "\n"

echo -e "${C_EXITO}--- FASE 3: TASQUES PROGRAMADES (CRON) ---${RESET}"
echo -e "    ${NEGRITA}ACCIÓ:${RESET} Dins el mateix directori haurà d'executar el següent script:"
echo -e "      \$ ${C_SUBTITULO}sudo bash setup_cron.sh${RESET}"
echo -e "    ${VERDE}FUNCIÓ:${RESET} ${NEGRITA}Configura l'automatització de les tasques programades${RESET} (CRON) en el servidor, como la creació de còpies de seguretat ${NEGRITA}backup${RESET} de la base de dades"
echo -e "            i l'execució d'altres scripts necessaris pel funcionament del Django-Aula quan es troba en producció."
echo -e "\n"

read -p "Premi una tecla per a continuar" -n1 -s

clear

echo -e "\n"
echo -e "${C_PRINCIPAL}================================================================"
echo -e "${C_PRINCIPAL}--- FASE 1: INSTAL·LACIÓ BASE I DEPENDÈNCIES${RESET} ${CIANO}install_djau.sh${RESET} ${C_PRINCIPAL}---"
echo -e "${C_PRINCIPAL}================================================================${RESET}"

# ----------------------------------------------------------------------
# 1. DIRECTORIS I USUARIS
# ----------------------------------------------------------------------

echo -e "\n"
echo -e "${C_CAPITULO}================================================="
echo -e "${C_CAPITULO}--- 1. DEFINICIÓ DE DIRECTORIS I USUARIS CLAU ---"
echo -e "${C_CAPITULO}=================================================${RESET}"
echo -e "\n"

echo -e "${C_INFO}ℹ️  **ATENCIÓ**${RESET} Quan s'indigui que hi ha un valor per defecte, si ho desitja podrà premer la tecla *Enter* per acceptar-lo.\n"

echo -e "\n"
echo -e "${C_SUBTITULO}--- 1.1 Sol·licitud de paràmetres de ruta ---${RESET}"
echo -e "${C_SUBTITULO}---------------------------------------------${RESET}"

# 1. Directori de projecte
INSTALL_DIR="/opt"
read_prompt "Introdueixi el nom del DIRECTORI del projecte, que es situarà dins el directori $INSTALL_DIR (per defecte: djau): " PROJECT_FOLDER "djau"
FULL_PATH="$INSTALL_DIR/$PROJECT_FOLDER"

echo -e "La ruta completa d'instal·ació serà: ${NEGRITA}'$FULL_PATH'${RESET}."
echo -e "\n"
sleep 1

# 2. Directori per dades sensibles
read_prompt "Introdueixi el nom del DIRECTORI que contindrà dades privades o sensibles de l'alumnat, que es trobarà també en $INSTALL_DIR, al mateix nivell que el directori triat $PROJECT_FOLDER (per defecte: djau-dades-privades): " DADES_PRIVADES "djau-dades-privades"
PATH_DADES_PRIVADES="$INSTALL_DIR/$DADES_PRIVADES"

echo -e	"La ruta completa per les dades privades serà: ${NEGRITA}'$PATH_DADES_PRIVADES'${RESET}."
echo -e "\n"
sleep 1

echo -e "\n"
echo -e "${C_SUBTITULO}--- 1.2 Sol·licitud i validació de l'usuari instal·lador de l'aplicatiu ---${RESET}"
echo -e "${C_SUBTITULO}---------------------------------------------------------------------------${RESET}"


# 3. Usuari instal·lador
read_prompt "Introdueixi el nom de l'USUARI DE LINUX que instal·lará l'aplicatiu (Ha d'existir i tenir permissos *sudo*) (per defecte: $SUDO_USER): " APP_USER "$SUDO_USER"

# Verifica si l'usuari existeix abans de continuar (Verificació crucial)
if id -u "$APP_USER" >/dev/null 2>&1; then
    # Codi de sortida = 0; L'usuari exixteix
    echo -e "${C_EXITO}✅ L'usuari '$APP_USER' ha estat verificat i es troba disponible en el sistema.${RESET}"

    # Provar si l'usuari pot executar sudo sense necessitat de contrasenya
    if sudo -u "$APP_USER" -n true 2>/dev/null; then
        echo -e "${C_EXITO}✅ L'usuari '$APP_USER' té permisos sudo actius (sense demanar contrasenya).${RESET}"
    else
        echo -e "${C_ERROR}❌ ERROR: L'usuari '$APP_USER' NO té permisos sudo configurats o es requereix contrasenya.${RESET}"
        echo -e "${C_INFO}ℹ️ Si us plau, assegureu que l'usuari té permisos sudo sense contrasenya (NOPASSWD) configurats o pertany al grup 'sudoers'.$ Tot el procés es troba documentat al repositori de l'aplicatiu.{RESET}"
        exit 1
    fi

else
    # Codi de sortida > 0; L'usuari NO exixteix
    echo -e "${C_ERROR}❌ ERROR: L'usuari '$APP_USER' no existeix en el sistema.${RESET}"
    echo -e "${C_INFO}ℹ️ Si us plau, ha de crear l'usuari abans de continuar i asseguri que pertany al grup 'sudoers'. Tot el procés es troba documentat al repositori de l'aplicatiu.${RESET}"
    exit 1
fi
sleep 2

# ----------------------------------------------------------------------
# 2. CONFIGURACIÓ DE POSTGRESQL I SUDOERS
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}========================================================"
echo -e "${C_CAPITULO}--- 2. CONFIGURACIÓ DE SEGURETAT (Permisos NOPASSWD) ---"
echo -e "${C_CAPITULO}========================================================${RESET}"
echo -e "\n"

echo -e "${C_SUBTITULO}--- Configurant permisos NOPASSWD per a PostgreSQL ---${RESET}"
echo -e "${C_SUBTITULO}------------------------------------------------------${RESET}"

PSQL_PATH="/usr/bin/psql"
PGDUMP_PATH="/usr/bin/pg_dump"

SUDOERS_RULE="/etc/sudoers.d/90-djau-psql"
PSQL_RULE="$APP_USER ALL=(postgres) NOPASSWD: $PSQL_PATH, $PGDUMP_PATH"

# Concedir a l'usuari instal·lador permís per a executar 'psql' i 'pg_dump' com a usuari 'postgres' sense contrasenya
printf "%s\n" "$PSQL_RULE" | sudo tee $SUDOERS_RULE > /dev/null

# Assegurar els permisos segurs per l'arxiu sudoers
sudo chmod 0440 $SUDOERS_RULE

echo -e "${C_EXITO}✅ Permisos NOPASSWD configurats per a '$APP_USER' per a psql i pg_dump.${RESET}"
sleep 2

# ----------------------------------------------------------------------
# 3. INSTAL·LACIÓ DE DEPENDÈNCIAS DEL SISTEMA I CREACIÓ DE DIRECTORIS
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}============================================================="
echo -e "${C_CAPITULO}--- 3. INSTAL·LACIÓ DE DEPENDÈNCIAS I PREPARACIÓ DE RUTES ---"
echo -e "${C_CAPITULO}=============================================================${RESET}"
echo -e "\n"

echo -e "${C_SUBTITULO}--- 3.1 Instal·lant dependèncias del sistema (Python, Git, PostgreSQL, etc). Ara no s'instal·lará el servidor web ---${RESET}"
echo -e "${C_SUBTITULO}---------------------------------------------------------------------------------------------------------------------${RESET}"

# 1. Actualitzar la llista de paquets
echo -e "${C_INFO}ℹ️ Actualiztzant la llista de paquets (apt-get update)...${RESET}"
apt-get update
echo -e "\n"

# 2. Actualitzar els paquets existents
echo -e "${C_INFO}ℹ️ Actualiztzant el sistema (apt-get upgrade -y)...${RESET}"
apt-get upgrade -y

if [ $? -ne 0 ]; then
    echo -e "\n"
    echo -e "${C_ERROR}❌ ERROR: Hi ha hagut un problema en actualitzar els paquets existents (apt-get upgrade).${RESET}"
    echo -e "${C_INFO}⚠️ EAquest fet pot indicar dependències trencades o problemes de sistema, però també pot ser un error de xarxa temporal.${RESET}"
    echo -e "\n"

    # Pregunta de continuació
    read_prompt "¿Desitja continuar igualment amb la instal·lació de dependències? (Per defecte NO: sí/NO): " CONTINUE_ACTION "no"

    RESPONSE_LOWER=$(echo "$CONTINUE_ACTION" | tr '[:upper:]' '[:lower:]')

    if [[ "$RESPONSE_LOWER" != "sí" ]] && [[ "$RESPONSE_LOWER" != "si" ]]; then
        echo -e "${C_ERROR}🛑 Instal·lació cancel·lada per l'usuari.${RESET}"
		echo -e "\n"
        exit 1
    fi
    echo -e "\n"
fi
echo -e "\n"

# 3. Instalar les dependèncias necessàries

echo -e "${C_INFO}ℹ️ Instala·lant dependències del sistema. Tingui paciència...${RESET}"
echo -e "\n"

# -----------------------------------------------------------------
# NÚCLI DE L'APLICACIÓ DJANGO I EINES DE PYTHON
# -----------------------------------------------------------------
APT_DESC="Núcli Django i Python"
echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
apt-get install -y \
    python3 \
    python3-venv \
    python3-dev \
    lib32z1-dev \
    libxml2-dev \
    libxslt-dev \
    python3-lxml \
    python3-libxml2 \
    libgl1 \
    libglib2.0-0t64

check_install "$APT_DESC"

# --------------------------------------------------------------------
# GESTIÓ DE CÓDI (per actualitzacions posteriores de la instal·lació)
# --------------------------------------------------------------------
APT_DESC="Gestió de codi (git)"
echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
apt-get install -y git
check_install "$APT_DESC"

# -----------------------------------------------------------------
# GESTOR DE BASE DE DADES
# -----------------------------------------------------------------
APT_DESC="Gestor de base de dates (PostgreSQL)"
echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
apt-get install -y postgresql
check_install "$APT_DESC"

# -----------------------------------------------------------------
# UTILITATS ADMINISTRATIVES
# -----------------------------------------------------------------
APT_DESC="Utilitats d'administratives"
echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
apt-get install -y \
    openssh-server \
    nano \
    htop \
    btop \
    ncdu

check_install "$APT_DESC"

# -----------------------------------------------------------------
# SEGURETAT I CONFIGURACIÓ DEL SISTEMA
# -----------------------------------------------------------------


if [ "$IS_SYSTEMD" -eq 1 ]; then
    # Instal·lació normal amb sistemes basats en systemd
    APT_DESC="Seguretat, Cron i Locales (fail2ban, locales, haveged)"
    echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
    apt-get install -y \
    cron \
    fail2ban \
    locales \
    haveged # Generador de Entropía

else
    # Excepció per a Devuan/No-systemd
    APT_DESC="Cron i Locales (locales, haveged)"
    echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
    apt-get install -y \
    cron \
    locales \
    haveged # Generador de Entropía
    echo
    echo -e "${C_ADVERTENCIA}⚠️ ADVERTÈNCIA: S'ha detectat un sistema noperatiu no basat en systemd (Com Devuan o similar). Fail2Ban no s'instal·larà automàticament.${RESET}"
    echo -e "${C_ADVERTENCIA}   Aquest paquet pot generar errors crítics en la instal·lació en certs entorns SysVinit/nucli minimalista.${RESET}"
    echo -e "${C_ADVERTENCIA}   Per raons de seguretat, es recomana a l'usuari instal·lar i configurar Fail2Ban manualment després de la instal·lació.${RESET}"
fi

check_install "$APT_DESC"

# NOTA: btop no está siempre en los repositorios por defecto de Debian/Ubuntu. 
# Si falla, se puede quitar o el usuario lo instalará por su cuenta.

echo -e "\n"
echo -e "${C_EXITO}✅ Totes les dependèncias del sistema instal·lades i sistema actualitzat correctament.${RESET}"
echo -e "\n"
sleep 2

echo -e "${C_SUBTITULO}--- 3.2 Configurant Fail2Ban ---${RESET}"
echo -e "${C_SUBTITULO}--------------------------------${RESET}"

if [ "$IS_SYSTEMD" -eq 1 ]; then

   # Còpia de la configuració per defecte a local per evitar canvis en l'arxiu original
   if [ ! -f /etc/fail2ban/jail.local ]; then
       echo -e "${C_INFO}ℹ️ Creant jail.local per a configuració local...${RESET}"
       cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
   fi

   echo -e "${C_INFO}ℹ️ Esperant 5 segons per tal que Fail2Ban iniciï completament el socket...${RESET}"
   sleep 5
   echo -e "\n"

   # Reiniciar per assegurat que la configuració està activa
   systemctl restart fail2ban

   echo -e "${C_EXITO}✅ Fail2Ban instal·lat i servei reiniciat. Protegint SSH.${RESET}"
   echo -e "\n"
   echo -e "${C_INFO}ℹ️ Pot verificar l'estat del sistema en qualsevol moment amb:${RESET}"
   echo -e "\n"
   echo -e "${C_INFO}sudo systemctl status fail2ban${RESET}"
   systemctl status fail2ban | grep Active
   echo -e "\n"
   sleep 2
   echo -e "${C_INFO}sudo fail2ban-client status${RESET}"
   fail2ban-client status
   echo -e "\n"
   sleep 2
   echo -e "${C_INFO}sudo fail2ban-client status sshd${RESET}"
   fail2ban-client status sshd
   echo -e "\n"
   sleep 2
else
   echo
   echo -e "${C_INFO}ℹ️ Fail2Ban no hs'ha instal·lat per defecte en aquest sistema basat en SysVinit. S'aconsella protegir el servidor amb Fail2Ban i ho hauria de fer manualment.${RESET}"
fi
echo

echo -e "${C_SUBTITULO}--- 3.3 Creació del directori del projecte DJANGO-AULA i el de les dades privades ---${RESET}"
echo -e "${C_SUBTITULO}-------------------------------------------------------------------------------------${RESET}"


# Directori del projecte
mkdir -p "$FULL_PATH"
if [ ! -d "$FULL_PATH" ]; then
    echo -e "${C_ERROR}❌ ERROR: No s'ha pogut crear el directori del projecte '$FULL_PATH'. Sortint.${RESET}"
	echo -e "\n"
    exit 1
fi

# Directori de dades privades
mkdir -p "$PATH_DADES_PRIVADES"
if [ ! -d "$PATH_DADES_PRIVADES" ]; then
    echo -e "${C_ERROR}❌ ERROR: No s'ha pogut crear el directori de dades privades '$PATH_DADES_PRIVADES'. Sortint.${RESET}"
	echo -e "\n"
    exit 1
fi
echo -e "${C_EXITO}✅ Directoris creats: '$FULL_PATH' i '$PATH_DADES_PRIVADES'.${RESET}"
echo -e "\n"
sleep 2

echo -e "${C_SUBTITULO}--- 3.4 Assignació de permisos d'arxius ---${RESET}"
echo -e "${C_SUBTITULO}-------------------------------------------${RESET}"

# Permisos per al directori del projecte (propietat de l'usuari de l'aplicatiu)
chown -R "$APP_USER":"$APP_USER" "$FULL_PATH"
echo -e "${C_EXITO}✅ Permisos per a '$FULL_PATH' assignats a l'usuari '$APP_USER'.${RESET}"
echo -e "\n"

sleep 2

# ----------------------------------------------------------------------
# 3.5 Generació i configuració del Locale (ca_ES.utf8)
# ----------------------------------------------------------------------

echo -e "${C_SUBTITULO}--- 3.5 Generant i configurant el Locale (ca_ES.utf8) ---${RESET}"
echo -e "${C_SUBTITULO}---------------------------------------------------------${RESET}"
echo -e "\n"

TARGET_LOCALE="ca_ES.UTF-8"
LOCALE_GEN_FILE="/etc/locale.gen"

# ----------------------------------------------------------------------------------
# PAS 1: Neteja i preparació del fitxer /etc/locale.gen
# ----------------------------------------------------------------------------------

echo -e "${C_INFO}ℹ️ Ajustant ${LOCALE_GEN_FILE} per a una generació ràpida i conservadora...${RESET}"
echo -e "${C_INFO}   Només es deixaran actius (descomentats) els locals ${NEGRITA}${TARGET_LOCALE}${RESET}${C_INFO} i espanyol d'Espanya, la resta es comentaran amb el símbol #.${RESET}"

# 1. Comentar totes les línies que no siguin un comentari (#) o línies buides.
# Això desactiva els locals que venen per defecte en distros d'escriptori.
# Comencem per una còpia de seguretat.
sudo cp "$LOCALE_GEN_FILE" "$LOCALE_GEN_FILE.bak"
sudo sed -i -r '/^\s*[a-zA-Z]/ s/^/#/' "$LOCALE_GEN_FILE"

# 2. Descomentar (activar) el local requerit per DjAu.
# Es busca la línia 'ca_ES.UTF-8 UTF-8' i se li elimina el possible '#' inicial.
sudo sed -i '/^#\s*ca_ES.UTF-8/ s/^#\s*//' "$LOCALE_GEN_FILE"

# 3. Descomentar (activar) el local per espanyol (es_ES).
sudo sed -i '/^#\s*es_ES.UTF-8/ s/^#\s*//' "$LOCALE_GEN_FILE"

echo -e "${C_EXITO}✅ Fitxer ${LOCALE_GEN_FILE} preparat. Només s'activaran els locals necessaris.${RESET}"
echo
sleep 1

# ----------------------------------------------------------------------------------
# PAS 2: Execució de locale-gen (Generació ràpida)
# ----------------------------------------------------------------------------------

echo -e "${C_INFO}ℹ️ Executant locale-gen (Generarà només els locals seleccionats, serà ràpid)...${RESET}"
sudo locale-gen

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR CRÍTIC: La generació dels locals ha fallat. Revisi si el paquet 'locales' està instal·lat.${RESET}"
    exit 1
fi
echo -e "${C_EXITO}✅ Generació de locals completada.${RESET}"
sleep 1

# ----------------------------------------------------------------------------------
# PAS 3: Fixar el local del sistema a 'ca_ES.UTF-8'
# ----------------------------------------------------------------------------------

echo -e "\n"
echo -e "${C_INFO}⚠️ ATENCIÓ: Per a que l'aplicatiu DjAu funcioni correctament amb la codificació i ordenació de dades (collation) del sistema operatiu, ${NEGRITA}es fixarà el local del sistema a ${TARGET_LOCALE}.${RESET}"

echo -e "${C_INFO}ℹ️ Configurant el locale del sistema a '${TARGET_LOCALE}'...${RESET}"
sudo update-locale LANG="$TARGET_LOCALE"

# Comprovar si el fitxer ha estat generat (locale -a)
if locale -a | grep -q -i "ca_es.utf8"; then
    # Comprovar si la variable LANG s'ha escrit correctament a /etc/default/locale
    if grep -q "LANG=$TARGET_LOCALE" /etc/default/locale; then
        echo -e "${C_EXITO}✅ Locale 'ca_ES.utf8' assegurat i configurat correctament.${RESET}"
    else
        echo -e "${C_ERROR}❌ ADVERTÈNCIA CRÍTICA: El local 'ca_ES.UTF-8' s'ha generat, però la variable de sistema no s'ha pogut fixar a /etc/default/locale. Reviseu-ho manualment.${RESET}"
    fi
else
    # El local no s'ha generat
    echo -e "${C_ERROR}❌ ADVERTENCIA CRÍTICA: El locale 'ca_ES.utf8' no s'ha pogut generar. Revisi manualment /etc/locale.gen. Recordi que s'ha fet una còpia de serguretat de l'arxiu original en $LOCALE_GEN_FILE.bak${RESET}"
fi

sleep 2

# ----------------------------------------------------------------------
# 4. CLONACIÓ DEL REPOSITORI
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}================================================="
echo -e "${C_CAPITULO}--- 4. CLONACIÓ DEL REPOSITORI DE L'APLICACIÓ ---"
echo -e "${C_CAPITULO}=================================================${RESET}"
echo -e "\n"

echo -e "${C_SUBTITULO}--- 4.1 Clonant repositori amb l'usuari '$APP_USER' ---${RESET}"
echo -e "${C_SUBTITULO}-------------------------------------------------------${RESET}"
echo -e "\n"

# Aquesta instal·lació NO està pensada per a actualitzar; si el directori existeix, s'aborta per seguretat.
# Si cal actualitzar, s'ha d'esborrar el directori o utilitzar el procés manual.

# COMPROVACIÓ: El directori existeix I no està buit?
if [ -d "$FULL_PATH" ] && [ "$(ls -A "$FULL_PATH")" ]; then
    # ⛔ CAS 1: Directori existeix i no està buit -> ABORTAR
    echo -e "${C_ERROR}❌ ERROR CRÍTIC: El directori '$FULL_PATH' ja existeix.${RESET}"
    echo "L'script 'install_djau.sh' està dissenyat per a una instal·lació nova."
    echo "Si vol actualitzar l'aplicatiu cal que segueixi les instruccions específiques del repositori de Github. Alternativament, si realment vol instal·lar l'aplicatiu sencer en $FULL_PATH, pot esborrar-los manualment i provar-ho de nou."
    echo -e "\n"
    exit 1
else
    echo -e "${C_INFO}Clonant $REPO_URL, branca '$GIT_BRANCH' en $FULL_PATH.${RESET}"

    # Clonar el repositori com l'usuari de l'aplicació, forçant la branca especificada
    sudo -u "$APP_USER" git clone -b "$GIT_BRANCH" "$REPO_URL" "$FULL_PATH"

    if [ $? -ne 0 ]; then
        echo -e "${C_ERROR}❌ ERROR: Fallda en clonar la branca '$GIT_BRANCH' del repositori '$REPO_URL'.${RESET}"
        echo "Comprovi la URL, conexió a internet o permisos de l'usuari '$APP_USER'."
        echo -e "\n"
        exit 1
    fi
    echo -e "${C_EXITO}✅ Repositori clonat (Branca: $GIT_BRANCH) a '$FULL_PATH'.${RESET}"
fi

echo -e "\n"
sleep 3


# -------------------------------------------------------------------------------------------------
# CREACIÓ DE L'ARXIU config_vars.sh AMB LES VARIABLES COMUNS PER LA INSTAL·LACIÓ DE L'APLICACIÓ
# -------------------------------------------------------------------------------------------------

SETUP_DIR="$FULL_PATH/setup_djau"
CONFIG_FILE="$SETUP_DIR/config_vars.sh"

echo -e "${C_SUBTITULO}--- 4.2 Creació de l'arxiu${RESET} ${CIANO}config_vars.sh${RESET} ${C_SUBTITULO}dins el directori${RESET} ${CIANO}$SETUP_DIR${RESET} ${C_SUBTITULO} ---${RESET}"
echo -e "${C_SUBTITULO}--------------------------------------------------------------------------------------${RESET}"

cat << EOF > "$CONFIG_FILE"

export APP_USER="$APP_USER"
export PROJECT_FOLDER="$PROJECT_FOLDER"
export FULL_PATH="$FULL_PATH"
export SETUP_DIR="$SETUP_DIR"
export PATH_DADES_PRIVADES="$PATH_DADES_PRIVADES"
export IS_SYSTEMD="$IS_SYSTEMD"
EOF

chown -R "$APP_USER":"$APP_USER" "$CONFIG_FILE"

# ----------------------------------------------------------------------
# 5. DELEGACIÓ AL SCRIPT DE CONFIGURACIÓ DE DJANGO-AULA
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}============================================================="
echo -e "${C_CAPITULO}--- 5. INICI DE LA CONFIGURACIÓ ESPECÍFICA DE DJANGO-AULA ---"
echo -e "${C_CAPITULO}=============================================================${RESET}"
echo -e "\n"

echo -e "--- A partir d'ara, l'usuari ${C_INFO}'$APP_USER'${RESET} executarà automàticament l'script ${C_INFO}setup_djau.sh${RESET}."
echo -e "    Aquest script es troba a ${C_INFO}'$SETUP_DIR'${RESET}."
echo -e "\n"

# Transferint l'execució a l'script de configuració de Django-Aula DINS el repositori i branca clonats
cd "$SETUP_DIR"
#chmod +x setup_djau.sh
#chmod +x setup_apache.sh
#chmod +x setup_cron.sh
#chmod +x functions.sh
#chown "$APP_USER":"$APP_USER" functions.sh

echo -e "${C_INFO}ℹ️  **ATENCIÓ:**${RESET} La instal·lació no serà desatesa. Haurà de respondre preguntes per configurar la base de dades i l'aplicatiu."
echo -e "\n"

read -p "Premi qualsevol tecla per a continuar" -n1 -s

sudo -u "$APP_USER" bash setup_djau.sh

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR: No s'ha pogut executar de forma automàtica l'script de configuració de Django-Aula (setup_djau.sh). Revisi els directoris clonats, especialment el directori $SETUP_DIR.${RESET}"
	echo -e "\n"
    exit 1
fi


echo -e "\n\n"
echo -e "${C_PRINCIPAL}==========================================================="
echo -e "${C_PRINCIPAL}--- FASE 1 COMPLETADA (install_djau.sh i setup_djau.sh) ---"
echo -e "${C_PRINCIPAL}===========================================================${RESET}"
echo -e "\n"

echo -e "${C_INFO}--- SEGÜENT FASE: FASE 2 - CONFIGURACIÓ DEL SERVIDOR WEB APACHE ---${RESET}"
echo -e "\n"

echo -e "Per a continuar amb la configuració del servidor web Apache, ${NEGRITA}executi les següents ordres (Copiar/Enganxar)${RESET}:"
echo -e "\n"

echo "   1. Vagi al directori del projecte:"
echo -e "      \$ ${C_SUBTITULO} cd \"$SETUP_DIR\"${RESET}"
echo -e "\n"

echo "   2. Executi l'script de configuració del servidor web Apache (HA DE SER amb sudo):"
echo -e "      \$ ${C_SUBTITULO} sudo bash setup_apache.sh${RESET}"
echo -e "\n"
