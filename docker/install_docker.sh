#!/bin/bash
# Script d'instal·lació automàtica de Docker CE i Docker Compose a sistemes Debian/Ubuntu.

clear

echo "---------------------------------------------------------"
echo "--- Instal·lador automàtic de Docker i Docker-Compose ---"
echo "---------------------------------------------------------"

# ---------------------------------------------------------------------------------
# 1. DEFINICIÓ DE VARIABLES, CÀRREGA DE LLIBRERIA DE FUNCIONS I VARIABLES DE COLORS
# ---------------------------------------------------------------------------------

# Definició de variables
# Repositori i branca per la clonació
REPO_USER="ctrl-alt.d"
REPO_NAME="django-aula"
REPO_BRANCA="master"

# URLs
REPO_URL="https://github.com/${REPO_USER}/${REPO_NAME}.git" # Repositori del projecte

# Definició de l'URL remota de la llibreria de funcions
REPO_BASE_CLEAN="${REPO_URL%.git}"
RAW_BASE="${REPO_BASE_CLEAN/https:\/\/github.com/https:\/\/raw.githubusercontent.com}"
FUNCTIONS_URL="${RAW_BASE}/${REPO_BRANCA}/setup_djau/functions.sh"
FUNCTIONS_FILE="./functions.sh"

echo -e "\n"
echo "Descarrregant la llibreria d'ús temporal de funcions i variables compartides ($FUNCTIONS_FILE)."

# Descàrrega de la llibreria de funcions amb wget
wget -q -O "$FUNCTIONS_FILE" "$FUNCTIONS_URL"

if [ $? -ne 0 ]; then
    echo -e "\n"
    echo "❌ ERROR: No s'ha pogut descarregar l'arxiu temporal de funcions des de $FUNCTIONS_URL. Sense aquestes funcions el script no pot executar-se. Sortint."
    exit 1
fi

# Canvi de propietat: Assignar l'arxiu descarregat a l'usuari original que ha executat 'sudo'
if [ -n "$SUDO_USER" ] && [ "$SUDO_USER" != "root" ]; then
    chown "$SUDO_USER":"$SUDO_USER" "$FUNCTIONS_FILE"
fi

# Càrrega de la llibreria de funcions
if [ ! -f "$FUNCTIONS_FILE" ]; then
    echo -e "\n\e[31m\e[1m❌ ERROR CRÍTIC:\e[0m No s'ha trobat l'arxiu $FUNCTIONS_FILE."
    echo "No es pot continuar sense la llibreria de funcions."
    exit 1
fi

source "$FUNCTIONS_FILE"

# Variables de color ($C_EXITO, $C_ERROR, etc.) i funcions comunes disponibles.
echo -e "${C_EXITO}✅ Llibreria de funcions temporal carregada amb èxit.${RESET}"

rm "$FUNCTIONS_FILE"

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ADVERTÈNCIA:Per alguna raó desconeguda no s'ha pogut eliminar l'arxiu temporal de funcions${RESET} ${C_INFO} '$FUNCTIONS_FILE'${RESET} ${${C_ERROR}}. Caldria fer-ho manualment.${RESET}"
else
echo -e "${C_EXITO}✅ Eliminació de l'arxiu temporal de funcions.${RESET}"
fi

# -------------------------------------------------------------------------------------
# 2. COMPROVACIONS PRÈVIES, PERMISOS, DETECCIÓ DEL SO I DE LA COMPATIBILITAT AMB DOCKER
# -------------------------------------------------------------------------------------

# Avís de Compatibilitat
echo -e "\n"
echo -e "${C_INFO}ℹ️  AVÍS: Aquest instal·lador està dissenyat exclusivament per a sistemes"
echo -e "    basats en Debian o Ubuntu (utilitza el gestor de paquets APT).${RESET}"
echo -e "${C_INFO}------------------------------------------------------------------------------${RESET}"
echo -e "\n"

# Comprovació tècnica: El sistema té APT?
if ! command -v apt-get &> /dev/null; then
    finalitzar_amb_error "Aquest sistema no utilitza 'apt-get'. L'instal·lador no és compatible."
fi

sleep 1

# Comprovació usuari d'execució amb permisos sudo
if [[ $EUID -ne 0 ]]; then
   echo "${C_ERROR}Aquest script s'ha d'executar amb un usuari amb permisos de 'sudo'.${RESET}"
   exit 1
fi

USUARI_SUDO=$(logname)

# Comprovar si el fitxer d'identificació del sistema (os-release) existeix
if [ ! -f /etc/os-release ]; then
    finalitzar_amb_error "No s'ha trobat l'arxiu /etc/os-release. Aquest sistema no sembla seguir l'estàndard LSB i no es pot identificar la distribució."
fi

# Importació de les variables de l'arxiu os-release per configurar el repositori de docker
. /etc/os-release

# Definició de Fallbacks (Manteniment fàcil). Si el sistema és massa nou, farem servir aquestes versions "segures"
FALLBACK_UBUNTU="noble"   # Ubuntu 24.04
FALLBACK_DEBIAN="trixie"  # Debian 13

# Determinar el CODENAME base (Primer pas de detecció)
if [ -n "$UBUNTU_CODENAME" ]; then
    CODENAME=$UBUNTU_CODENAME
elif [ -n "$DEBIAN_CODENAME" ]; then
    CODENAME=$DEBIAN_CODENAME
else
    CODENAME=$VERSION_CODENAME
fi

# Determinar l'OS_ID base
OS_ID=$ID
case "$OS_ID" in
    ubuntu|debian|raspbian|centos|fedora|rhel|sles) ;;
    *)
        if [[ "$ID_LIKE" == *"ubuntu"* ]]; then
            OS_ID="ubuntu"
        elif [[ "$ID_LIKE" == *"debian"* ]]; then
            OS_ID="debian"
        else
            finalitzar_amb_error "Sistema no suportat ($ID). No s'ha trobat base Ubuntu/Debian."
        fi
        ;;
esac

# Update i instal·lció de Curl
echo -e "${C_SUBTITULO}-> Preparant el sistema i instal·lant eines de xarxa...${RESET}"

rm -f /etc/apt/sources.list.d/docker.sources /etc/apt/sources.list.d/docker.list

if ! apt-get update -qq; then
    finalitzar_amb_error "L'actualització de la llista de paquets (apt update) ha informat d'un error. Verifiqui si hi ha altres repositoris trencats al sistema."
fi

echo -e "\n"

APT_DESC="ca-certificates i Curl"
echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
apt-get install -y \
   ca-certificates \
   curl

check_install "$APT_DESC"

sleep 2


# Validació del repositori
echo -e "${C_INFO}ℹ️ Sistema $PRETTY_NAME. Verificant disponibilitat al repositori de Docker per a '$CODENAME'...${RESET}"

CHECK_URL="https://download.docker.com/linux/$OS_ID/dists/$CODENAME/Release"

# Obtenim només el codi d'estat HTTP (ex: 200, 404, 403)
HTTP_STATUS=$(curl -o /dev/null -s -w "%{http_code}" "$CHECK_URL")

if [ "$HTTP_STATUS" != "200" ]; then
    echo -e "${C_INFO}⚠️  ATENCIÓ: La versió '$CODENAME' no s'ha trobat (HTTP $HTTP_STATUS) a Docker ($OS_ID).${RESET}"
    
    CODENAME_OLD="$CODENAME"
    if [[ "$OS_ID" == "ubuntu" ]]; then
        CODENAME=$FALLBACK_UBUNTU
    else
        CODENAME=$FALLBACK_DEBIAN
    fi
    
    echo -e "${C_EXITO}🔄 Es farà servir la versió compatible (fallback) més propera: ${NEGRITA}$CODENAME${RESET}"
else
    echo -e "${C_EXITO}✅ Confirmació que la versió '$CODENAME' es troba al repositori de Docker.${RESET}"
fi

# Missatge informatiu per a l'usuari
echo -e "\n${C_INFO}------------------------------------------------------------------------------${RESET}"
echo -e "${C_INFO}🔍 DETECCIÓ DEL SISTEMA:${RESET}"
echo -e "   ${NEGRITA}Distribució Real:${RESET}  $PRETTY_NAME ($ID)"
echo -e "   ${NEGRITA}Repositori Docker:${RESET}  https://download.docker.com/linux/$OS_ID"
echo -e "   ${NEGRITA}Codi Versió:${RESET}  $CODENAME"
echo -e "${C_INFO}------------------------------------------------------------------------------${RESET}"

sleep 2

echo -e "\n"
echo -e "${C_PRINCIPAL}⚙️ Iniciant instal·lació de Docker i Docker Compose per a l'usuari: ${USUARI_SUDO}${RESET}"
echo -e "${C_PRINCIPAL}------------------------------------------------------------------------------${RESET}"
echo -e "\n"

# -------------------------------------------------------------
# 3. AFEGIR REPOSITORI OFICIAL DE DOCKER
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
# 4. INSTAL·LACIÓ DELS PAQUETS DE DOCKER 
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
echo -e "${C_EXITO}✅ Docker instal·lat correctament a $PRETTY_NAME ($CODENAME)!${RESET}"

sleep 2

# -------------------------------------------------------------
# 5. COMPROVACIONS FINALS
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

# Comprovem si l'usuari ja pertany al grup per no repetir l'acció
if id -nG "$USUARI_SUDO" | grep -qw "docker"; then
    echo -e "${C_INFO}ℹ️ L'usuari ${USUARI_SUDO} ja forma part del grup 'docker'.${RESET}"
else
    if ! usermod -aG docker "${USUARI_SUDO}"; then
        finalitzar_amb_error "No s'ha pogut afegir l'usuari al grup 'docker'."
    fi
    echo -e "${C_EXITO}✅ Usuari afegit al grup 'docker' correctament.${RESET}"
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
