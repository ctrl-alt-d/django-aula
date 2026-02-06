#!/bin/bash
# -------------------------------------------------------------
# Script per a la instal·lació de la Demo Docker de django-aula.
# Descarrega els fitxers de configuració i comprova la base de dades.
# -------------------------------------------------------------

# --- 0. Configuració de rutes i repositori

# Ruta on s'executa el script (Directori arrel de la instal·lació)
BASE_DIR=$(pwd)

# Dades del repositori
#REPO_USER="ctrl-alt-d"
REPO_USER="rafatecno1"
REPO_NAME="django-aula"
REPO_BRANCA="millora-demo"
#REPO_BRANCA="master"

# Rutes locals
DJAU_PATH="${BASE_DIR}/djau"
DOCKER_SRC="${DJAU_PATH}/docker"
FUNCTION_PATH="${DJAU_PATH}/setup_djau"

# URLs
REPO_URL="https://github.com/${REPO_USER}/${REPO_NAME}.git"

clear
echo "---------------------------------------------------------------"
echo "--- Instal·lador automàtic de la Demo Docker de django-aula ---"
echo "--- Branca: $REPO_BRANCA | Arrel: $BASE_DIR ---"
echo "---------------------------------------------------------------"
echo
sleep 1

# --- 1. Clonació del repositori

# Instal·lar git, si cal.

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
echo -e "\n"

# COMPROVACIÓ: El directori existeix i no està buit?
if [ -d "$DJAU_PATH" ] && [ "$(ls -A "$DJAU_PATH")" ]; then
    rm -Rf $DJAU_PATH
fi

echo -e "Clonant $REPO_URL, branca '$REPO_BRANCA' en $DJAU_PATH."
echo

# Clonar el repositori com l'usuari de l'aplicació, forçant la branca especificada i amb profunditat mínima (no interessa tot l'historial)
git clone --depth 1 -b "$REPO_BRANCA" "$REPO_URL" "$DJAU_PATH"

if [ $? -ne 0 ]; then
    echo -e "❌ ERROR: Fallida en clonar la branca '$REPO_BRANCA' del repositori '$REPO_URL'."
    echo "Comprovi la URL, conexió a internet o permisos de l'usuari."
    echo -e "\n"
    exit 1
fi
echo
echo -e "✅ Repositori clonat (Branca: $REPO_BRANCA) a '$DJAU_PATH'."

echo -e "\n"
sleep 2

# Carrega de la llibreria de funcions
echo "Important variables de colors i funcions de la llibreria 'functions.sh'"
if [ -f "$FUNCTION_PATH/functions.sh" ]; then
    source "$FUNCTION_PATH/functions.sh"
    echo -e "${C_EXITO}✅ Llibreria de funcions carregada amb èxit.${RESET}"
else
    echo -e "\n\e[31m\e[1m❌ ERROR:\e[0m No s'ha trobat l'arxiu functions.sh dins el directori $FUNCTION_PATH."
    echo "No es pot continuar sense la llibreria de funcions."
    exit 1
fi
echo -e "\n"

# --- 2. Fitxers a descarregar ---

FILES_ORIGIN=(
    "Dockerfile"
    "docker-compose.demo.automatica.yml"
    "Makefile.demo.automatica"
    "env.demo.automatica"
)
FILES_DEST=(
    "Dockerfile"
    "docker-compose.yml"
    "Makefile"
    ".env"
 )

# --- 3. Descarregar fitxers de configuració i dades ---

echo -e "${C_INFO}📦 Preparant fitxers pel desplegament des de ${DOCKER_SRC}...${RESET}"
echo

for i in "${!FILES_ORIGIN[@]}"; do
    SRC="${DOCKER_SRC}/${FILES_ORIGIN[$i]}"
    DST="${BASE_DIR}/${FILES_DEST[$i]}"

    if [ -f "$SRC" ]; then
        cp "$SRC" "$DST"
        echo -e "${C_EXITO}   ✅ ${FILES_DEST[$i]} preparat.${RESET}"
    else
        echo -e "${C_ERROR}   ❌ No s'ha trobat l'origen: ${FILES_ORIGIN[$i]}${RESET}"
        exit 1
    fi
done

echo
echo -e "${C_EXITO}✅ Tots els fitxers s'han descarregat correctament. Com a comprovació es llista el contingut del directori:${RESET}"
ls -lah Dockerfile docker-compose.yml Makefile .env

echo

# --- 4. Instal·lar make si cal ---

echo -e "${C_INFO}🔧 Comprovant que 'make' estigui instal·lat...${RESET}"
if ! command -v make &> /dev/null; then
    echo -e "${C_INFO}   Instal·lant 'make'...${RESET}"
    sudo apt-get update -y >/dev/null 2>&1
    sudo apt-get install -y make
    if ! command -v make &> /dev/null; then
        finalitzar_amb_error "   Error a la instal·lació de 'make'"
    fi
else
    echo -e "${C_EXITO}   ✅ 'make' ja està disponible.${RESET}"
fi

# --- 5. Pregunta pel domini o IP ---

echo
echo -e "${C_INFO}🌍 Si la Demo ha de funcionar en una xarxa local cal definir quina IP té. Si es vol instal·lar en un servidor en internet (VPS) caldrà informar de la seva IP pública i del domini o subdomini, si n'hi ha.${RESET}"
echo
read_prompt "Vol afegir un domini o IP a **DEMO_ALLOWED_HOSTS** per poder accedir-hi externament a la Demo? (Per defecte NO: sí/NO): " REPLY "no"
RESPONSE_LOWER=$(echo "$REPLY" | tr '[:upper:]' '[:lower:]')
#read -p "Vol afegir un domini o IP a **DEMO_ALLOWED_HOSTS** per poder accedir-hi externament a la Demo? (S/n): " REPLY

if [[ "$RESPONSE_LOWER" = "sí" ]] || [[ "$RESPONSE_LOWER" = "si" ]] || [[ "$RESPONSE_LOWER" = "s" ]]; then
    read -p "👉 Introdueix els dominis o IPs separats per comes (ex: demo.elteudomini.cat,192.168.1.46): " HOSTS
    if [ -n "$HOSTS" ]; then
        sed -i "s|^DEMO_ALLOWED_HOSTS=.*|DEMO_ALLOWED_HOSTS=${HOSTS}|" .env
        echo -e "${C_EXITO}✅ Fitxer .env actualitzat amb DEMO_ALLOWED_HOSTS=${HOSTS}${RESET}"
    else
        echo -e "${C_INFO}⚠️ No s'ha introduït cap domini/IP. Es manté buit.${RESET}"
    fi
else
    echo -e "${C_INFO}ℹ️ No s'ha modificat DEMO_ALLOWED_HOSTS. Es manté buit.${RESET}"
fi

# --- 6. Posar en marxa els contenidors ---

# Comprovant que l'arxiu .env existeix
if [ -f .env ]; then
    set -a
    source .env # carregar DB_USER, etc.
    set +a
else
    finalitzar_amb_error "⚠️  No s'ha trobat el fitxer .env. No es pot comprovar l'estat de la base de dades."
fi

echo
echo -e "${C_INFO}🕓 Posant en marxa els contenidors de la Demo i de la Base de Dades PostgreSQL...${RESET}"
echo
make build
make serve
echo

# --- 7. Informació sobre els contenidors en marxa ---

echo
echo -e "${C_INFO}--------------------------------------------${RESET}"
echo -e "${C_INFO}📦  Estat final de l'estat dels contenidors ${RESET}"
echo -e "${C_INFO}--------------------------------------------${RESET}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo -e "${C_INFO}--------------------------------------------${RESET}"
echo
echo

# --- 8. Espera a la finalització de la preparació ---

echo -e "${C_INFO}Progrès de preparació de la base de dades i del servidor de la demo (logs).${RESET}"
echo -e "${C_INFO}El procés finalitzarà automàticament quan el servidor estigui llest.${RESET}"
echo -e "${C_INFO}---------------------------------------------------------------------------${RESET}"
echo -e "\n"

# Iniciem el bucle de lectura de logs
docker logs -f demo_web 2>&1 | while read -r line; do

    # 1. Bloc per ocultar els SyntaxWarning, per neteja visual. Si, per dev, es vol veure tota la sortida cal fer make logs
    if [[ "$line" == *"SyntaxWarning"* ]]; then
        continue
    fi

    # 2. Imprimim la línia en gris per diferenciar-la del script
    echo -e "${GRIS}${line}${RESET}"

    # 3. Condició de sortida: Quan Django ens diu que ja escolta al port 8000
    if [[ "$line" == *"Starting development server at"* ]]; then
        echo -e "${C_INFO}----------------------------------------------------------------------------------------${RESET}"
        echo -e "\n"
        echo -e "${C_EXITO}✅ EL SERVIDOR ESTÀ PREPARAT.${RESET}"
        # Matem el procés 'docker logs' per sortir del bucle 'while'
        pkill -P $$ -f "docker logs"
        break
    fi
done

# --- 9. Missatge final ---

echo -e "\n"
sleep 1

echo -e "${C_INFO}----------------------------------------------------------------------------------------"
echo -e "ℹ️ Informació addicional${RESET}"
echo -e "\n"
echo -e "${C_INFO}Instruccions disponibles amb la comanda **make** per la Demo:${RESET}"
echo -e "${C_INFO}   1. Si no està en marxa, executi: ${RESET}${CIANO}make serve${RESET}"
echo -e "${C_INFO}   2. Per veure els logs:           ${RESET}${CIANO}make logs${RESET}"
echo -e "${C_INFO}   3. Per detenir la Demo:          ${RESET}${CIANO}make stop${RESET}"
echo -e "${C_INFO}   4. Per eliminar els contenidors: ${RESET}${CIANO}make down${RESET}${C_INFO} i després -> docker system prune -a"

echo
echo -e "🌐 Si ha definit IP o dominis a DEMO_ALLOWED_HOSTS, provi ara d'accedir-hi al navegador!"
echo -e "   (p. ex. http://demo.elteudomini.cat:8000 o http://IP:8000)${RESET}"
echo
