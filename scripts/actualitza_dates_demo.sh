#!/bin/bash
cd `dirname $0`/..
cp aula/db.sqlite.seg aula/db.sqlite
source ../venv3/bin/activate
python manage.py decala_dates
