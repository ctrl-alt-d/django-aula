#!/bin/bash
# -------------------------------------------------------------
# Script per a la instal·lació ràpida de la Demo Docker de django-aula.
# Descarrega els fitxers de configuració essencials i comprova la base de dades.
# -------------------------------------------------------------

# --- 1. Informació del repositori ---

REPO="ctrl-alt-d/django-aula"
BRANCA="master"
URL_BASE="https://raw.githubusercontent.com/${REPO}/refs/heads/${BRANCA}/docker"

clear
echo -e "⚙️  Iniciant instal·lació ràpida de la Demo en Docker...\n"
echo

# --- 2. Fitxers a descarregar ---

FILES_TO_DOWNLOAD=(
    "docker-compose.demo.automatica.yml"
    "Makefile.demo.automatica"
    "env.demo.automatica"
    "dades_demo.sql"
)
DEST_FILES=(
    "docker-compose.yml"
    "Makefile"
    ".env"
    "dades-demo-sql/dades_demo.sql"
)


# --- 3. Descarregar fitxers de configuració i dades ---

echo "📦 Descarregant fitxers necessaris..."
mkdir -p dades-demo-sql

for i in "${!FILES_TO_DOWNLOAD[@]}"; do
    ORIGIN="${FILES_TO_DOWNLOAD[$i]}"
    DEST="${DEST_FILES[$i]}"
    URL="${URL_BASE}/${ORIGIN}"

    # Crear el directori si no existeix
    mkdir -p "$(dirname "${DEST}")"

    echo "  -> Descarregant ${ORIGIN} com a ${DEST}..."
    if wget -q -O "${DEST}" "${URL}"; then
        echo "     ✅ Fitxer ${DEST} descarregat correctament."
    else
        echo "     ❌ Error en descarregar ${ORIGIN}."
        exit 1
    fi

    # Assignar permisos adequats
    if [[ "${DEST}" == *.sql ]]; then
        chmod 644 "${DEST}"
    fi

    echo
done

echo "✅ Tots els fitxers s'han descarregat correctament."
echo

ls -lah docker-compose.yml Makefile .env dades-demo-sql/dades_demo.sql
echo


# --- 4. Instal·lar make si cal ---

echo "🔧 Comprovant que 'make' estigui instal·lat..."
if ! command -v make &> /dev/null; then
    echo "   Instal·lant 'make'..."
    sudo apt-get update -y >/dev/null 2>&1 && sudo apt-get install -y make
else
    echo "   ✅ 'make' ja està disponible."
fi


# --- 5. Pregunta pel domini o IP ---

echo
echo "🌍 Si la Demo ha de funcionar en una xarxa local cal definir quina IP té. Si es vol instal·lar en un servidor en internet (VPS) caldrà informar de la seva IP pública i del domini o subdomini, si n'hi ha."
echo -e "\n"
read -p "Vol afegir un domini o IP a **DEMO_ALLOWED_HOSTS** per poder accedir-hi externament a la Demo? (y/n): " REPLY

if [[ $REPLY =~ ^[Yy]$ ]]; then
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

echo
echo "🕓 Posant en marxa els contenidors de la Demo i de la Base de Dades PostgreSQL..."
echo
make serve
echo

# --- 7. Esperar que la base de dades estigui llesta ---

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
echo "    ✅ PostgreSQL està llest!"


# --- 8. Comprovació del fitxer SQL ---

echo
echo "🔍 Comprovant si s'ha carregat el fitxer SQL de dades de la demo..."
DB_LOGS=$(docker logs demo_db 2>&1 | grep -E "docker-entrypoint-initdb.d/.*\.sql" | tail -n 1)

if [[ "$DB_LOGS" == *".sql"* ]]; then
        echo "    ✅ Base de dades inicialitzada correctament!"
        echo "       Fragment del log:"
        echo "       $DB_LOGS"
    else
        echo "⚠️  No s'ha trobat cap evidència que s'hagi executat dades_demo.sql"
        echo "   -> Revisa amb: docker logs demo_db | less"
        echo "   -> o torna a reiniciar amb: make down && make serve"
fi

# --- 9. Missatge final ---

echo
echo
echo "Finalització de l'automatització!"

echo
echo "--------------------------------------------"
echo "📦  Estat final de l'estat dels contenidors"
echo "--------------------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo "--------------------------------------------"
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

