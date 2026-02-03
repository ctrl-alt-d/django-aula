#!/bin/bash
# Script d'instal·lació automàtica de Docker CE i Docker Compose a sistemes Debian/Ubuntu.

# --------------------------------------------------
# VARIABLES DE COLOR I ESTIL ANSI
# --------------------------------------------------

# Aquestes variables es troben a l'arxiu functions.sh. Caldria fer el mateix que fem amb l'instal·lador install_djau.sh
# i la funció de missatge d'error podria ser interessant incorporar-la a functions.sh i als scripts
RESET='\e[0m'
NEGRITA='\e[1m'

# Colors básics
AZUL='\e[34m'
VERDE='\e[32m'
ROJO='\e[31m'
CIANO='\e[36m'
AMARILLO='\e[33m'
MAGENTA='\e[35m'

# Estils compostos
C_EXITO="${NEGRITA}${VERDE}"       # Éxit i confirmacions (✅)
C_ERROR="${NEGRITA}${ROJO}"        # Errors o fallades (❌)
C_PRINCIPAL="${NEGRITA}${AZUL}"    # Fases principals (FASE 1, FASE 2)
C_CAPITULO="${NEGRITA}${CIANO}"    # Títuls de Capítul (1. DEFINICIÓ...)
C_SUBTITULO="${NEGRITA}${MAGENTA}" # Títuls de Subcapítul (1.1, 1.2)
C_INFO="${NEGRITA}${AMARILLO}"     # Informació important (INFO, ATENCIÓN)

# Funció per mostrar errors i sortir
finalitzar_amb_error() {
    echo -e "\n"
    echo -e "${C_ERROR}❌ ERROR: $1${RESET}"
    echo "La instal·lació s'ha aturat perquè un pas crític ha fallat."
    exit 1
}

clear

# -------------------------------------------------------------
# 1. Comprovacions, Permisos i Detecció del SO
# -------------------------------------------------------------

if [[ $EUID -ne 0 ]]; then
   echo "${C_ERROR}Aquest script s'ha d'executar amb un usuari amb permisos de 'sudo'.${RESET}"
   exit 1
fi

USUARI_SUDO=$(logname)

. /etc/os-release
OS_ID=$ID  # Detectarà el sistema operatiu, per exemple 'debian', 'ubuntu', etc

# Utilitzarà el codename d'Ubuntu si existeix, si no, el de Debian
CODENAME=${UBUNTU_CODENAME:-$VERSION_CODENAME}

echo -e "${C_INFO}-> Sistema detectat: $OS_ID ($CODENAME)${RESET}"

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

if ! apt-get install -y ca-certificates curl; then
    finalitzar_amb_error "No s'han pogut instal·lar les dependències inicials (ca-certificates i curl)."
fi

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

if ! apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; then
    finalitzar_amb_error "No s'han pogut instal·lar els paquets de Docker."
fi

echo -e "\n"
echo -e "${C_EXITO}✅ Docker instal·lat correctament a $OS_ID ($CODENAME)!${RESET}"

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
