#!/bin/bash
cd `dirname $0`/..
for i in extKronowin incidencies presencia assignatures horaris seguimentTutorial missatgeria usuaris
do
    python manage.py loaddata aula/apps/$i/fixtures/dades.json
done
