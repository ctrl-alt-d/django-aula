#!/bin/bash
# Script d'instal·lació automàtica de Docker CE i Docker Compose a sistemes Debian/Ubuntu.

clear

echo "---------------------------------------------------------"
echo "--- Instal·lador automàtic de Docker i Docker-Compose ---"
echo "---------------------------------------------------------"

# ------------------------------------------------------------------------------
# DEFINICIÓ DE VARIABLES, CÀRREGA DE LLIBRERIA DE FUNCIONS I VARIABLES DE COLORS
# ------------------------------------------------------------------------------

# 1. Definició de variables
# Repositori i branca per la clonació

#REPO_URL="https://github.com/ctrl-alt-d/django-aula.git"	# repositori del projecte
REPO_URL="https://github.com/rafatecno1/django-aula.git"	# repositori del projecte
GIT_BRANCH="millora-docker"						# Si es vol instal·lar una branca concreta. Exemple: "feat/upgrade-bootstrap"
#GIT_BRANCH="master"						# Si es vol instal·lar una branca concreta. Exemple: "feat/upgrade-bootstrap"

# 2. Definició de l'URL remota de la llibreria de funcions
REPO_BASE_CLEAN="${REPO_URL%.git}"
RAW_BASE="${REPO_BASE_CLEAN/https:\/\/github.com/https:\/\/raw.githubusercontent.com}"
FUNCTIONS_URL="${RAW_BASE}/${GIT_BRANCH}/setup_djau/functions.sh"
FUNCTIONS_FILE="./functions.sh"

echo -e "\n"
echo "ℹ️ Descarregant la llibreria t'ús temporal de funcions i variables compartides ($FUNCTIONS_FILE)."

# 3. Descàrrega de la llibreria de funcions amb wget
wget -q -O "$FUNCTIONS_FILE" "$FUNCTIONS_URL"

if [ $? -ne 0 ]; then
    echo -e "\n"
    echo "❌ ERROR: No s'ha pogut descarregar l'arxiu temporal de funcions des de $FUNCTIONS_URL. Sense aquestes funcions el script no pot executar-se. Sortint."
    exit 1
fi

# 4. Canvi de propietat: Assignar l'arxiu descarregat a l'usuari original que ha executat 'sudo'
if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
    chown "$SUDO_USER":"$SUDO_USER" "$FUNCTIONS_FILE"
fi

# 5. Càrrega de la llibreria de funcions
source "$FUNCTIONS_FILE"

# Variables de color ($C_EXITO, $C_ERROR, etc.) i funcions comunes disponibles.
echo -e "${C_EXITO}✅ Llibreria de funcions temporal carregada amb èxit.${RESET}"

rm "$FUNCTIONS_FILE"

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ADVERTÈNCIA:Per alguna raó desconeguda no s'ha pogut eliminar l'arxiu temporal de funcions${RESET} ${C_INFO} '$FUNCTIONS_FILE'${RESET} ${${C_ERROR}}. Caldria fer-ho manualment.${RESET}"
else
echo -e "${C_EXITO}✅ Eliminació de l'arxiu temporal de funcions.${RESET}"
fi

# Funció per mostrar errors i sortir. Podria ser interessant incorporar-la a functions.sh per fer-la servir als scripts
finalitzar_amb_error() {
    echo -e "\n"
    echo -e "${C_ERROR}❌ ERROR: $1${RESET}"
    echo "La instal·lació s'ha aturat perquè un pas crític ha fallat."
    exit 1
}

# -------------------------------------------------------------
# 1. Comprovacions, Permisos i Detecció del SO
# -------------------------------------------------------------

if [[ $EUID -ne 0 ]]; then
   echo "${C_ERROR}Aquest script s'ha d'executar amb un usuari amb permisos de 'sudo'.${RESET}"
   exit 1
fi

USUARI_SUDO=$(logname)

# Comprovar si el fitxer d'identificació del sistema existeix
if [ ! -f /etc/os-release ]; then
    finalitzar_amb_error "No s'ha trobat l'arxiu /etc/os-release. Aquest sistema no sembla seguir l'estàndard LSB i no es pot identificar la distribució."
fi

. /etc/os-release

OS_ID=$ID
CODENAME=${UBUNTU_CODENAME:-$VERSION_CODENAME}
NOM_SISTEMA=${PRETTY_NAME:-$OS_ID} # Si no hi ha PRETTY_NAME, usa l'ID

if [ -z "$CODENAME" ]; then
    finalitzar_amb_error "No s'ha pogut determinar el 'Codename' del sistema (ex: bookworm, noble). No es pot configurar el repositori de Docker."
fi

# Missatge decoratiu de detecció
echo -e "\n"
echo -e "${C_INFO}------------------------------------------------------------------------------${RESET}"
echo -e "${C_INFO}🔍 DETECCIÓ DEL SISTEMA:${RESET}"
echo -e "   ${NEGRITA}Distribució:${RESET}  $NOM_SISTEMA"
echo -e "   ${NEGRITA}Codi Versió:${RESET}  $CODENAME"
echo -e "${C_INFO}------------------------------------------------------------------------------${RESET}"

sleep 2

echo -e "\n"
echo -e "${C_PRINCIPAL}⚙️ Iniciant instal·lació de Docker i Docker Compose per a l'usuari: ${USUARI_SUDO}${RESET}"
echo -e "${C_PRINCIPAL}------------------------------------------------------------------------------${RESET}"
echo -e "\n"

# -------------------------------------------------------------
# 2. Preparació del Sistema
# -------------------------------------------------------------

echo -e "${C_SUBTITULO}-> Actualitzant paquets i instal·lant dependències...${RESET}"
if ! apt-get update -qq; then
    finalitzar_amb_error "No s'ha pogut actualitzar la llista de paquets (apt update)."
fi

sleep 2
echo -e "\n"

APT_DESC="ca-certificates i Curl"
echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
apt-get install -y \
   ca-certificates \
   curl

check_install "$APT_DESC"

sleep 2

# -------------------------------------------------------------
# 3. Afegir Repositori Oficial de Docker
# -------------------------------------------------------------

echo -e "\n"
echo -e "${C_SUBTITULO}-> Afegint repositori oficial de Docker...${RESET}"
install -m 0755 -d /etc/apt/keyrings

# Descàrrega de la clau
if ! curl -fsSL "https://download.docker.com/linux/$OS_ID/gpg" -o /etc/apt/keyrings/docker.asc; then
    finalitzar_amb_error "No s'ha pogut obtenir la clau per a $OS_ID des de download.docker.com"
fi

chmod a+r /etc/apt/keyrings/docker.asc

# Configuració del repositori estructurat (DEB822)
echo -e "${C_SUBTITULO}-> Configurant repositori oficial de Docker...${RESET}"
cat <<EOF > /etc/apt/sources.list.d/docker.sources
Types: deb
URIs: https://download.docker.com/linux/$OS_ID
Suites: $CODENAME
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF


# -------------------------------------------------------------
# 4. Instal·lació dels Paquets de Docker 
# -------------------------------------------------------------

echo -e "${C_SUBTITULO}-> Instal·lant Docker CE, CLI i Docker Compose Plugin...${RESET}"
if ! apt-get update -qq; then
    finalitzar_amb_error "El repositori de Docker no ha respost correctament per a la versió $CODENAME."
fi

sleep 2
echo -e "\n"

APT_DESC="Paquets de Docker: docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin"
echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
apt-get install -y \
   docker-ce \
   docker-ce-cli \
   containerd.io \
   docker-buildx-plugin \
   docker-compose-plugin

check_install "$APT_DESC"

echo -e "\n"
echo -e "${C_EXITO}✅ Docker instal·lat correctament a $NOM_SISTEMA ($CODENAME)!${RESET}"

sleep 2

# -------------------------------------------------------------
# 5. Finalització i Permisos
# -------------------------------------------------------------

echo -e "\n"
echo -e "${C_SUBTITULO}-> Assegurant que el servei Docker estigui actiu...${RESET}"
if ! systemctl start docker; then
    finalitzar_amb_error "No s'ha pogut arrencar el servei de Docker."
fi

systemctl enable docker >/dev/null 2>&1

# Mostrem estat
systemctl status docker | grep -E 'Loaded:|Active:'

sleep 2

echo -e "\n"
echo -e "${C_SUBTITULO}-> Afegint l'usuari ${USUARI_SUDO} al grup 'docker'...${RESET}"
if ! usermod -aG docker "${USUARI_SUDO}"; then
    finalitzar_amb_error "No s'ha pogut afegir l'usuari al grup 'docker'."
fi

sleep 1

echo -e "\n"
echo -e "${C_EXITO}✅ INSTAL·LACIÓ FINALITZADA CORRECTAMENT.${RESET}"
echo -e "\n"
sleep 1
echo -e "${C_INFO}-------------------------------------------------------------------------------------"
echo -e "${C_INFO}⚠️ ACCIÓ REQUERIDA: Perquè els nous permisos de Docker tinguin efecte, heu"
echo -e "${C_INFO}   de tancar la sessió SSH actual i tornar a connectar-vos-hi o reiniciar la màquina."
echo -e "${C_INFO}   Un cop reconnectat, podeu provar amb: docker run hello-world"
echo -e "${C_INFO}-------------------------------------------------------------------------------------${RESET}"
