#!/bin/bash
set -e
echo "Mostrant 'logs'..."
echo
echo "⌛ Esperant que la base de dades estigui operativa..."

TIMEOUT=60
COUNT=0

# Utilitzem pg_isready per minimitzar el temps d'espera fent la comprovació amb motor de postgres
until pg_isready -h db -U "$DB_USER" >/dev/null 2>&1; do
    sleep 1
    ((COUNT+=1))
    
    if [ $COUNT -ge $TIMEOUT ]; then
        echo "❌ ERROR: La base de dades no ha respost en $TIMEOUT segons."
        echo "   El procés d'inicialització s'ha aturat. Revisa els logs amb: 'docker logs demo_db' o amb 'make logs'."
        exit 1
    fi
done

echo "✅ PostgreSQL està llest! (El procés de preparació ha trigat $COUNT segons)"
echo
echo "📦 Aplicant migracions i preparant dades..."
echo

if [ ! -f /app/storage/.inicialitzat ]; then
  echo "Inicialitzant dades ..."
  python manage.py migrate
  echo -e "\n"
  python manage.py collectstatic --noinput
  echo -e "\n"
  ./scripts/fixtures.sh
  echo -e "\n"
  python manage.py loaddemodata
  touch /app/storage/.inicialitzat
else
  echo "Les dades ja s'havien inicialitzant anteriorment."
fi
echo
echo "Engengant el servidor de desenvolupament..."
echo
exec python manage.py runserver 0.0.0.0:8000

