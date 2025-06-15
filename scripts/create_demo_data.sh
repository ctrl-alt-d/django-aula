#!/bin/bash
export PYTHONIOENCODING=utf8
cd `dirname $0`/..
rm aula/db.sqlite
python manage.py migrate
./scripts/fixtures.sh
python manage.py collectstatic -c --no-input
python manage.py loaddemodata


