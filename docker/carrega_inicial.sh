#!/bin/bash
set -e

wait-for-it db:5432 --timeout=30 --strict

if [ ! -f /app/storage/.inicialitzat ]; then
  echo "Inicialitzant dades ..."
  python manage.py migrate
  python manage.py collectstatic --noinput
  ./scripts/fixtures.sh
  python manage.py loaddemodata
  touch /app/storage/.inicialitzat
else
  echo "Dades ja inicialitzades."
fi

exec python manage.py runserver 0.0.0.0:8000

