#!/bin/bash
cd `dirname $0`/..
source env/bin/activate
python manage.py exporta_bi
