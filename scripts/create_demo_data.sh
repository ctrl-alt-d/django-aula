#!/bin/bash
cd ..
rm aula/db.sqlite
python manage.py syncdb --noinput
./scripts/fixtures.sh
python manage.py loaddemodata


