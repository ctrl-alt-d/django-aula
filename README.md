django-aula
===========

Gestió de presencia, incidències i més per a Instituts, Escoles i Acadèmies.

School Attendance Software

![Imgur](http://i.imgur.com/YlCRTap.png)

**[Llicència i Crèdits](https://github.com/ctrl-alt-d/django-aula/blob/master/LICENSE)**

Quick demo
=========

On Ubuntu Server 14.04 LTS 64 bits:
* apt-get install python-virtualenv python-pip libxml2-dev libxslt-dev python-libxml2 python-dev lib32z1-dev git
* mkdir djau
* cd djau
* virtualenv venv
* source venv/bin/activate
* git clone https://github.com/ctrl-alt-d/django-aula.git
* cd django-aula
* pip install -r requirements.txt
* ./scripts/create_demo_data.sh  #this take for a while ( > 7 minutes of fake data )
* python manage.py runserver 127.0.0.1:8000   # or your 
* Open browser at http://127.0.0.1:8000 ( User M1, M2, ..., T1, T2, .. .All passwd 'dAju' )

Documentation
==============
https://django-aula.gitbook.io/documentation/
