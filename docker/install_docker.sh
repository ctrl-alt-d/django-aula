#!/bin/bash
# Script d'instal·lació automàtica de Docker CE i Docker Compose a sistemes Debian/Ubuntu.

# -------------------------------------------------------------
# 1. Comprovacions i Permisos
# -------------------------------------------------------------

# Determinar si s'està executant amb privilegis de root (necessari per instal·lar).
if [[ $EUID -ne 0 ]]; then
   echo "Aquest script s'ha d'executar amb un usuari amb permisos de 'sudo'."
   exit 1
fi

USUARI_SUDO=$(logname)

clear
echo -e "\n"
echo "⚙️ Iniciant instal·lació de Docker i Docker Compose per a l'usuari: ${USUARI_SUDO}"
echo "------------------------------------------------------------------"
echo -e "\n"

# -------------------------------------------------------------
# 2. Preparació del Sistema
# -------------------------------------------------------------

echo "-> Actualitzant paquets i instal·lant dependències..."
apt-get update -qq >/dev/null
apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release

# -------------------------------------------------------------
# 3. Afegir Repositori Oficial de Docker
# -------------------------------------------------------------

echo -e "\n"
echo "-> Afegint repositori oficial de Docker..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Afegim el repositori, ajustant la versió de codi de Debian/Ubuntu.
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# -------------------------------------------------------------
# 4. Instal·lació dels Paquets
# -------------------------------------------------------------

echo -e "\n"
echo "-> Instal·lant Docker CE, CLI i Docker Compose Plugin..."
apt-get update -qq >/dev/null
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# -------------------------------------------------------------
# 5. Finalització i Permisos
# -------------------------------------------------------------

echo -e "\n"
echo "-> Assegurant que el servei Docker estigui actiu i habilitat a l'engegada de la màquina..."
systemctl start docker
systemctl enable docker >/dev/null 2>&1

# Mètode per mostrar només les línies Loaded i Active (la comprovació d'èxit)
systemctl status docker | grep -E 'Loaded:|Active:'

echo -e "\n"
echo "-> Afegint l'usuari ${USUARI_SUDO} al grup 'docker'..."
usermod -aG docker "${USUARI_SUDO}"

echo -e "\n"
echo "------------------------------------------------------------------"
echo "✅ INSTAL·LACIÓ FINALITZADA CORRECTAMENT."
echo "   ⚠️ ACCIÓ REQUERIDA: Perquè els nous permisos de Docker tinguin efecte,"
echo "   heu, o bé tancar la sessió SSH actual i tornar a connectar-vos-hi, o bé reiniciar la màquina."
echo "   Un cop reconnectat, podeu provar amb: docker run hello-world"
