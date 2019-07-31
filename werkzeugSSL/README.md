Servidor SSL
==============

Per tal d'executar amb servidor SSL i poder fer proves sense necessitat de tenir apache instal·lat.

[Basat en](https://django-extensions.readthedocs.io/en/latest/runserver_plus.html)

Concretament ho he fet servir per fer proves amb el mòbil.

Per instal·lar i executar
==============================

Cal situar-se en el directori del fitxer manage.py

```bash

pip install Werkzeug
pip install pyOpenSSL

source werkzeugSSL/executaSSL.bash 

```


