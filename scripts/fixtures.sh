#!/bin/bash
cd `dirname $0`/..
FILES=`find ./aula -name 'dades.json'`
for i in $FILES
do
        python manage.py loaddata $i
done
