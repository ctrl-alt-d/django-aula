#!/bin/bash
cd `dirname $0`/..
rm aula/db.sqlite
python manage.py syncdb --noinput
./scripts/fixtures.sh
python manage.py loaddemodata


