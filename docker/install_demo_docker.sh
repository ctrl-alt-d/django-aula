#!/bin/bash
# -------------------------------------------------------------
# Script per a la instal·lació de la Demo Docker de django-aula.
# Descarrega els fitxers de configuració i comprova la base de dades.
# -------------------------------------------------------------

# --- 0. Configuració de rutes, repositori, mode normal o Dev

# Ruta on s'executa el script (Directori arrel de la instal·lació)
BASE_DIR=$(pwd)

# Dades del repositori
REPO_USER="rafatecno1" #"ctrl-alt-d"
REPO_NAME="django-aula"
REPO_BRANCA="neteja-docker" #"master"

# Rutes locals
DOCKER_SRC="${BASE_DIR}/docker"
FUNCTION_PATH="${BASE_DIR}/setup_djau"

# URLs
REPO_URL="https://github.com/${REPO_USER}/${REPO_NAME}.git"

# Funció d'ajuda
mostrar_ajuda() {
    echo
    echo "Instal·lador de la Demo Docker de django-aula"
    echo
    echo "Ús: $0 [opcions]"
    echo
    echo "Opcions:"
    echo "  -h, --help    Mostra aquest missatge d'ajuda."
    echo "  -d, --dev     Instal·la l'entorn de DESENVOLUPAMENT (amb volums en viu)."
    echo
    echo "Si no s'especifica cap flag, s'instal·larà la DEMO estàndard."
    echo
    exit 0
}

# Captura d'arguments (Flags)
IS_DEV=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -h|--help) mostrar_ajuda ;;
        -d|--dev)  IS_DEV=true ;;
        *) echo "Opció desconeguda: $1. Usa -h per ajuda."; exit 1 ;;
    esac
    shift
done

# Definició de noms segons el mode

if [ "$IS_DEV" = true ]; then
    MODE_LABEL="DEMO desenvolupament (DEV)"
    MAKE_BUILD="make dev-build"
    MAKE_SERVE="make dev-serve"
    CONTAINER_NAME="dev_web"
else
    MODE_LABEL="DEMO standard"
    MAKE_BUILD="make build"
    MAKE_SERVE="make serve"
    CONTAINER_NAME="demo_web"
fi

clear
echo "---------------------------------------------------------------"
echo "--- Instal·lador automàtic de la Demo Docker de django-aula ---"
echo "--- Branca: $REPO_BRANCA | Arrel: $BASE_DIR ---"
echo "--- Mode: $MODE_LABEL ---"
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
echo -e "Clonant $REPO_URL, branca '$REPO_BRANCA' en un directori temporal $BASE_DIR/temp_repo"
echo

# Clonar el repositori com l'usuari de l'aplicació, forçant la branca especificada
# i amb profunditat mínima (no interessa tot l'historial) a un directori temporal
git clone --depth 1 -b "$REPO_BRANCA" "$REPO_URL" "$BASE_DIR/temp_repo"

if [ $? -ne 0 ]; then
    echo -e "❌ ERROR: Fallida en clonar la branca '$REPO_BRANCA' del repositori '$REPO_URL'."
    echo "Comprovi la URL, conexió a internet o permisos de l'usuari."
    echo -e "\n"
    exit 1
fi

# Moguent repositori clonat del directori temporal a la seva ubicació definitiva
mv "${BASE_DIR}/temp_repo/"* "${BASE_DIR}/"					# Mou arxius no ocults
mv "${BASE_DIR}/temp_repo/".* "${BASE_DIR}/" 2>/dev/null	# Mou arxius ocults
rmdir "${BASE_DIR}/temp_repo"
echo
echo -e "✅ Repositori clonat de forma definitiva (Branca: $REPO_BRANCA) a '$BASE_DIR'."

echo -e "\n"
sleep 2

# Càrrega de la llibreria de funcions
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

# --- 2. Còpia i reubicació d'arxius necessaris per fer el "Deploy" ---

FILES=(
    "Dockerfile"
    "docker-compose.yml"
    "docker-compose.dev.yml"
    "Makefile"
    ".env"
    ".dockerignore"
)

echo -e "${C_INFO}📦 Preparant fitxers pel desplegament des de ${DOCKER_SRC}...${RESET}"
echo

for FILE in "${FILES[@]}"; do
    if [ -f "${DOCKER_SRC}/${FILE}" ]; then
        cp "${DOCKER_SRC}/${FILE}" "${BASE_DIR}/"
        echo -e "${C_EXITO}   ✅ $FILE ${RESET}${C_INFO}preparat.${RESET}"
    else
        echo -e "${C_ERROR}   ❌ No s'ha trobat: $FILE${RESET}"
        exit 1
    fi
done

echo
echo -e "${C_EXITO}✅ Tots els fitxers s'han descarregat correctament. Com a comprovació es llista el contingut del directori:${RESET}"
ls -lah "${FILES[@]}"
echo

# --- 3. Instal·lar make, si cal ---

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

# --- 4. Personalització del domini o IP on aixecar el servei ---

echo
echo -e "${C_INFO}🌍 Si la Demo ha de funcionar en una xarxa local cal definir quina IP té. Si es vol instal·lar en un servidor en internet (VPS) caldrà informar de la seva IP pública i del domini o subdomini, si n'hi ha.${RESET}"
echo
read_prompt "Vol afegir un domini o IP a **DEMO_ALLOWED_HOSTS** per poder accedir-hi externament a la Demo? (Per defecte NO: sí/NO): " REPLY "no"
RESPONSE_LOWER=$(echo "$REPLY" | tr '[:upper:]' '[:lower:]')

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

# --- 5. Posar en marxa els contenidors ---

# Comprovant que l'arxiu .env existeix
if [ -f .env ]; then
    set -a
    source .env # carregar DB_USER, etc.
    set +a
else
    finalitzar_amb_error "⚠️  No s'ha trobat el fitxer .env. No es pot comprovar l'estat de la base de dades."
fi

# Creant i aixecant els contenidors
echo
echo -e "${C_INFO}🕓 Posant en marxa els contenidors en mode ${MODE_LABEL}...${RESET}"
echo
$MAKE_BUILD
$MAKE_SERVE
echo

# --- 6. Informació sobre els contenidors en marxa ---

echo
echo -e "${C_INFO}--------------------------------------------${RESET}"
echo -e "${C_INFO}📦  Estat final de l'estat dels contenidors ${RESET}"
echo -e "${C_INFO}--------------------------------------------${RESET}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo -e "${C_INFO}--------------------------------------------${RESET}"
echo
echo

# --- 7. Espera a la finalització de la preparació ---

echo -e "${C_INFO}Progrès de preparació de la base de dades i del servidor de la demo (logs).${RESET}"
echo -e "${C_INFO}El procés finalitzarà automàticament quan el servidor estigui llest.${RESET}"
echo -e "${C_INFO}---------------------------------------------------------------------------${RESET}"
echo -e "\n"

# Iniciem el bucle de lectura de logs
docker logs -f $CONTAINER_NAME 2>&1 | while read -r line; do

    # 1. Bloc per ocultar els SyntaxWarning, per neteja visual. És codi temporal fins que no s'arreglin.
    # Si, per dev, es vol veure tota la sortida cal fer make logs
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

# Generació i càrrega opcional de les dades fictícies per la Demo (Només en mode DEV) 
if [ "$IS_DEV" = true ]; then
    echo
    read_prompt "Vol carregar les dades de la demo ara mateix (és un procés que triga una estona) (Per defecte NO: sí/NO): " REPLY "no"
    RESPONSE_LOWER=$(echo "$REPLY" | tr '[:upper:]' '[:lower:]')
    if [[ "$RESPONSE_LOWER" = "sí" ]] || [[ "$RESPONSE_LOWER" = "si" ]] || [[ "$RESPONSE_LOWER" = "s" ]]; then
        echo -e "${C_INFO}📦 Carregant dades...${RESET}"
        make dev-load_demo_data
    else
        echo -e "${C_INFO}👍 D'acord. Pots fer-ho més tard amb: make dev-load_demo_data${RESET}"
    fi
fi

# --- 8. Missatge final ---

echo -e "\n"
sleep 1

echo -e "${C_INFO}----------------------------------------------------------------------------------------"
echo -e "ℹ️ Informació addicional${RESET}"
echo -e "\n"

if [ "$IS_DEV" = true ]; then
    echo -e "${C_INFO}Comandes **make** disponibles pel desplegament de la demo en mode DESENVOLUPAMENT:${RESET}"
    echo -e "  ${CIANO}make dev-serve${RESET}           Aixeca l'entorn amb volums en viu"
    echo -e "  ${CIANO}make dev-build${RESET}           Construeix la imatge de dev"
    echo -e "  ${CIANO}make dev-stop${RESET}            Atura els contenidors de dev"
    echo -e "  ${CIANO}make dev-down${RESET}            Elimina contenidors i xarxes de dev"
    echo -e "  ${CIANO}make dev-logs${RESET}            Mostra logs del contenidor web"
    echo -e "  ${CIANO}make dev-load_demo_data${RESET}  Carrega fixtures i dades de la Demo"
    echo -e "  ${CIANO}make dev-makemigrations${RESET}  Comprova models i crea migracions"
    echo -e "  ${CIANO}make dev-shell${RESET}           Entra a la consola de Django"
    echo -e "  ${CIANO}make dev-bash${RESET}            Entra al terminal del contenidor"
else
    echo -e "${C_INFO}Comandes **make** disponibles per la Demo:${RESET}"
    echo -e "  ${CIANO}make serve${RESET}     Aixeca la demo"
    echo -e "  ${CIANO}make build${RESET}     Construeix la imatge de la demo"
    echo -e "  ${CIANO}make stop${RESET}      Atura la demo"
    echo -e "  ${CIANO}make down${RESET}      Elimina els contenidors de la demo. Per eliminar les imatges 'docker system prune -a'."
    echo -e "  ${CIANO}make logs${RESET}      Mostra logs de la demo"
fi
echo
echo

echo -e "${C_INFO}----------------------------------------------------------------------------------------${RESET}"

if [ -z "$HOSTS" ]; then
    echo -e "🌐 Accés al navegador:${RESET}"
    echo -e "   👉 ${CIANO}http://localhost:8000${RESET}"
    echo -e "   ${GRIS}Nota: Si estàs en un servidor remot, usa http://IP_DEL_SERVIDOR:8000${RESET}"
else
    echo -e "La variable ${GROC}DEMO_ALLOWED_HOSTS${RESET} ha estat configurada amb els següents dominis o IPs:"
    echo -e "${GRIS}$HOSTS${RESET}"
    echo
    echo -e "🌐 Accés a la Demo des del navegador:${RESET}"
    
    # Separem els hosts per la coma i creem un enllaç per a cadascun
    IFS=',' read -ra ADDR <<< "$HOSTS"
    for host in "${ADDR[@]}"; do
        # Eliminem possibles espais en blanc que hagi pogut posar l'usuari
        host=$(echo $host | xargs)
        echo -e "   👉 ${CIANO}http://${host}:8000${RESET}"
    done
fi

echo -e "${C_INFO}----------------------------------------------------------------------------------------${RESET}\n"
echo
