#!/bin/bash
# Script d'instal·lació automàtica de Docker CE i Docker Compose a sistemes Debian/Ubuntu.

# Funció per mostrar errors i sortir
finalitzar_amb_error() {
    echo -e "\n❌ ERROR: $1"
    echo "La instal·lació s'ha aturat perquè un pas crític ha fallat."
    exit 1
}

# -------------------------------------------------------------
# 1. Comprovacions, Permisos i Detecció del SO
# -------------------------------------------------------------

if [[ $EUID -ne 0 ]]; then
   echo "Aquest script s'ha d'executar amb un usuari amb permisos de 'sudo'."
   exit 1
fi

USUARI_SUDO=$(logname)

. /etc/os-release
OS_ID=$ID  # Detectarà 'debian' o 'ubuntu'
# Utilitzarà el codename d'Ubuntu si existeix, si no, el de Debian
CODENAME=${UBUNTU_CODENAME:-$VERSION_CODENAME}

echo "-> Sistema detectat: $OS_ID ($CODENAME)"

echo -e "\n"
echo "⚙️ Iniciant instal·lació de Docker i Docker Compose per a l'usuari: ${USUARI_SUDO}"
echo "------------------------------------------------------------------"

# -------------------------------------------------------------
# 2. Preparació del Sistema
# -------------------------------------------------------------

echo "-> Actualitzant paquets i instal·lant dependències..."
if ! apt-get update -qq; then
    finalitzar_amb_error "No s'ha pogut actualitzar la llista de paquets (apt update)."
fi

if ! apt-get install -y ca-certificates curl; then
    finalitzar_amb_error "No s'han pogut instal·lar les dependències inicials (ca-certificates i curl)."
fi

# -------------------------------------------------------------
# 3. Afegir Repositori Oficial de Docker
# -------------------------------------------------------------

echo -e "\n"
echo "-> Afegint repositori oficial de Docker..."
install -m 0755 -d /etc/apt/keyrings

# Descàrrega de la clau
if ! curl -fsSL "https://download.docker.com/linux/$OS_ID/gpg" -o /etc/apt/keyrings/docker.asc; then
    finalitzar_amb_error "No s'ha pogut obtenir la clau per a $OS_ID des de download.docker.com"
fi

chmod a+r /etc/apt/keyrings/docker.gpg

# Configuració del repositori estructurat (DEB822)
echo "-> Configurant repositori oficial de Docker..."
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

echo -e "\n"
echo "-> Instal·lant Docker CE, CLI i Docker Compose Plugin..."
if ! apt-get update -qq; then
    finalitzar_amb_error "El repositori de Docker no ha respost correctament per a la versió $CODENAME."
fi

if ! apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin; then
    finalitzar_amb_error "No s'han pogut instal·lar els paquets de Docker."
fi

echo -e "\n✅ Docker instal·lat correctament a $OS_ID ($CODENAME)!"

# -------------------------------------------------------------
# 5. Finalització i Permisos
# -------------------------------------------------------------

echo -e "\n"
echo "-> Assegurant que el servei Docker estigui actiu..."
if ! systemctl start docker; then
    finalitzar_amb_error "No s'ha pogut arrencar el servei de Docker."
fi

systemctl enable docker >/dev/null 2>&1

# Mostrem estat
systemctl status docker | grep -E 'Loaded:|Active:'

echo -e "\n"
echo "-> Afegint l'usuari ${USUARI_SUDO} al grup 'docker'..."
if ! usermod -aG docker "${USUARI_SUDO}"; then
    finalitzar_amb_error "No s'ha pogut afegir l'usuari al grup 'docker'."
fi

echo -e "\n"
echo "------------------------------------------------------------------"
echo "✅ INSTAL·LACIÓ FINALITZADA CORRECTAMENT."
echo "   ⚠️ ACCIÓ REQUERIDA: Perquè els nous permisos de Docker tinguin efecte, heu"
echo "   de tancar la sessió SSH actual i tornar a connectar-vos-hi o reiniciar la màquina."
echo "   Un cop reconnectat, podeu provar amb: docker run hello-world"
