<#!/bin/bash
# -------------------------------------------------------------
# Script per a la instal·lació de la Demo Docker de django-aula.
# Descarrega els fitxers de configuració i comprova la base de dades.
# -------------------------------------------------------------

# --- 1. Informació del repositori ---

REPO="rafatecno1/django-aula"
#REPO="ctrl-alt-d/django-aula"
#BRANCA="master"
BRANCA="millora-demo"
URL_BASE="https://raw.githubusercontent.com/${REPO}/refs/heads/${BRANCA}/docker"

clear
echo -e "⚙️  Iniciant instal·lació de la Demo en Docker...\n"
echo

# ----------------------------------------------------------------------
# --- 1.1. CLONACIÓ DEL REPOSITORI
# ----------------------------------------------------------------------

echo "------- Clonant repositori ----------------------------"
echo "-------------------------------------------------------"
echo -e "\n"

# --- Instal·lar git si cal ---

echo "🔧 Comprovant que 'git' estigui instal·lat..."
if ! command -v git &> /dev/null; then
    echo "   Instal·lant 'git'..."
    sudo apt-get update -y >/dev/null 2>&1
    sudo apt-get install -y git
    if ! command -v git &> /dev/null; then
        echo "   ERROR a la instal·lació de 'git'"
        exit 1
    fi
else
    echo "   ✅ 'git' ja està disponible."
fi

FULL_PATH="./djau"
REPO_URL="https://github.com/${REPO}.git"	# repositori del projecte
GIT_BRANCH=${BRANCA}						# Si es vol instal·lar una branca concreta. Exemple: "feat/upgrade-bootstrap"

# COMPROVACIÓ: El directori existeix i no està buit?
if [ -d "$FULL_PATH" ] && [ "$(ls -A "$FULL_PATH")" ]; then
    rm -Rf $FULL_PATH
fi
echo -e "Clonant $REPO_URL, branca '$GIT_BRANCH' en $FULL_PATH."

# Clonar el repositori com l'usuari de l'aplicació, forçant la branca especificada
git clone -b "$GIT_BRANCH" "$REPO_URL" "$FULL_PATH"

if [ $? -ne 0 ]; then
    echo -e "❌ ERROR: Fallida en clonar la branca '$GIT_BRANCH' del repositori '$REPO_URL'."
    echo "Comprovi la URL, conexió a internet o permisos de l'usuari."
    echo -e "\n"
    exit 1
fi
echo -e "✅ Repositori clonat (Branca: $GIT_BRANCH) a '$FULL_PATH'."


echo -e "\n"
sleep 3

# Carrega de la llibreria de funcions
if [ -f "{FULL_PATH}/setup_djau/functions.sh" ]; then
    source "{FULL_PATH}/setup_djau/functions.sh"
    echo -e "${C_EXITO}✅ Llibreria de funcions carregada amb èxit.${RESET}"
else
    echo -e "\n\e[31m\e[1m❌ ERROR:\e[0m No s'ha trobat l'arxiu functions.sh dins el directori {FULL_PATH}/setup_djau/."
fi

# --- 2. Fitxers a descarregar ---

FILES_TO_DOWNLOAD=(
    "Dockerfile"
    "docker-compose.demo.automatica.yml"
    "Makefile.demo.automatica"
    "env.demo.automatica"
)
DEST_FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "Makefile"
    ".env"
 )


# --- 3. Descarregar fitxers de configuració i dades ---

echo "📦 Descarregant fitxers necessaris..."

for i in "${!FILES_TO_DOWNLOAD[@]}"; do
    ORIGIN="${FILES_TO_DOWNLOAD[$i]}"
    DEST="${DEST_FILES[$i]}"

    # Crear el directori si no existeix
    mkdir -p "$(dirname "${DEST}")"

    echo "  -> Descarregant ${ORIGIN} com a ${DEST}..."
    if cp "${FULL_PATH}/docker/${ORIGIN}" "${DEST}"; then
        echo "     ✅ Fitxer ${DEST} descarregat correctament."
    else
        echo "     ❌ Error en descarregar ${ORIGIN}."
        exit 1
    fi

    echo
done

echo "✅ Tots els fitxers s'han descarregat correctament."
echo

ls -lah Dockerfile docker-compose.yml Makefile .env

echo


# --- 4. Instal·lar make si cal ---

echo "🔧 Comprovant que 'make' estigui instal·lat..."
if ! command -v make &> /dev/null; then
    echo "   Instal·lant 'make'..."
    sudo apt-get update -y >/dev/null 2>&1
    sudo apt-get install -y make
    if ! command -v make &> /dev/null; then
        echo "   ERROR a la instal·lació de 'make'"
        exit 1
    fi
else
    echo "   ✅ 'make' ja està disponible."
fi


# --- 5. Pregunta pel domini o IP ---

echo
echo "🌍 Si la Demo ha de funcionar en una xarxa local cal definir quina IP té. Si es vol instal·lar en un servidor en internet (VPS) caldrà informar de la seva IP pública i del domini o subdomini, si n'hi ha."
echo -e "\n"
read -p "Vol afegir un domini o IP a **DEMO_ALLOWED_HOSTS** per poder accedir-hi externament a la Demo? (S/n): " REPLY

if [[ $REPLY =~ ^[Ss]$ ]]; then
    read -p "👉 Introdueix els dominis o IPs separats per comes (ex: demo.elteudomini.cat,192.168.1.46): " HOSTS
    if [ -n "$HOSTS" ]; then
        sed -i "s|^DEMO_ALLOWED_HOSTS=.*|DEMO_ALLOWED_HOSTS=${HOSTS}|" .env
        echo "✅ Fitxer .env actualitzat amb DEMO_ALLOWED_HOSTS=${HOSTS}"
    else
        echo "⚠️ No s'ha introduït cap domini/IP. Es manté buit."
    fi
else
    echo "ℹ️ No s'ha modificat DEMO_ALLOWED_HOSTS. Es manté buit."
fi


# --- 6. Posar en marxa els contenidors ---

# Comprovant que l'arxiu .env existeix
if [ -f .env ]; then
    set -a
    source .env # carregar DB_USER, etc.
    set +a
else
    echo "⚠️  No s'ha trobat el fitxer .env. No es pot comprovar l'estat de la base de dades."
    exit 1
fi

echo
echo "🕓 Posant en marxa els contenidors de la Demo i de la Base de Dades PostgreSQL..."
echo
make build
make serve
echo

# --- 7. Esperar que la base de dades estigui llesta ---

echo
echo "⌛ Esperant que la base de dades estigui llesta (pot trigar uns segons)..."
TIMEOUT=60
COUNT=0
until docker exec demo_db pg_isready -U "$DB_USER" >/dev/null 2>&1; do
    sleep 2
    ((COUNT+=2))
    if [ $COUNT -ge $TIMEOUT ]; then
        echo "❌ Error: la base de dades no ha respost en $TIMEOUT segons."
        echo "   Revisa els logs amb: docker logs demo_db"
        exit 1
    fi
done
echo "       L'espera ha sigut de $COUNT segons."
echo "    ✅ PostgreSQL està llest!"

echo
echo "--------------------------------------------"
echo "📦  Estat final de l'estat dels contenidors"
echo "--------------------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo "--------------------------------------------"
echo
echo

# --- 8. Espera a la finalització de la preparació ---

#echo "Premi qualsevol tecla per continuar i mostrar el progrés de la preparació de la demo."
#read -p "posteriorment CTRL-C per deixar de mostrar la informació." -n1 -s

#docker logs -f demo_web

echo "AQUÍ CAL POSAR UN BON MISSATGE PER INDICAR QUE MOSTRAREM ELS LOGS"
echo "Comença la prova"


echo -e "\n"
info "S'està preparant la base de dades i el servidor..."
echo -e "${C_PRINCIPAL}Aquest procés finalitzarà automàticament quan el servidor estigui llest.${RESET}"
echo -e "${C_PRINCIPAL}------------------------------------------------------------------------${RESET}"

# Iniciem el bucle de lectura de logs
# Filtrem els "SyntaxWarning" per no embrutar la sortida si vols
docker logs -f demo_web 2>&1 | while read -r line; do
    
    # 1. Ignorem els SyntaxWarning per netaeja visual. NO VULL IGORNAR-LOS
    #if [[ "$line" == *"SyntaxWarning"* ]]; then
    #    continue
    #fi

    # 2. Imprimim la línia en gris per diferenciar-la del script
    echo -e "${CIANO}${line}${RESET}"

    # 3. Condició de sortida: Quan Django ens diu que ja escolta al port 8000
    if [[ "$line" == *"Starting development server at"* ]]; then
        echo -e "${C_PRINCIPAL}----------------------------------------------------------------------${RESET}"
        echo -e "\n"
        success "EL SERVIDOR ESTÀ PREPARAT!"
        
        # Matem el procés 'docker logs' per sortir del bucle 'while'
        # Ho fem d'una manera neta cercant el procés fill
        pkill -P $$ -f "docker logs"
        break
    fi
done


# --- 9. Missatge final ---

echo
echo
echo "Finalització de l'automatització!"

echo
echo 
echo "ℹ️ Informació addicional"
echo
echo "Instruccions disponibles amb la comanda **make** per la Demo:"
echo "   1. Si no està en marxa, executi: make serve"
echo "   2. Per veure els logs:           make logs"
echo "   3. Per detenir la Demo:          make stop"
echo "   4. Per eliminar els contenidors: make down i després -> docker system prune -a"

echo
echo "🌐 Si ha definit IP o dominis a DEMO_ALLOWED_HOSTS, provi ara d'accedir-hi al navegador!"
echo "   (p. ex. http://demo.elteudomini.cat:8000 o http://IP:8000)"
echo

