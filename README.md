django-aula
===========

Gestió de presència, incidències i més per a Instituts, Escoles i Acadèmies.

School Attendance Software

![Imgur](http://i.imgur.com/YlCRTap.png)

**[Llicència i Crèdits](LICENSE)** **EL PROGRAMA NO TÉ CAP GARANTIA, UTILITZEU-LO SOTA LA VOSTRA RESPONSABILITAT.**

Using Docker
============

```
cp env.example .env
make build
make start

# If you want to import demo data
make load_demo_data

# If you want to clean the DB
make down
make start
```

Quick demo
=========

On Ubuntu Server 24.04 LTS:

```bash
sudo apt-get update
sudo apt-get install python3 python3-venv python3-dev git
sudo apt-get install python3-lxml python3-libxml2 libxml2-dev libxslt-dev lib32z1-dev
mkdir djau
cd djau
git clone --single-branch --branch master https://github.com/ctrl-alt-d/django-aula.git django-aula
cd django-aula
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
./scripts/create_demo_data.sh
python manage.py runserver

```

Open browser at http://127.0.0.1:8000 ( User M1, M2, ..., T1, T2, .. .All passwd 'dAju' )

Deployment Docs
=============

[Documentació pas a pas per a fer el desplegament.](docs/Wiki/README.md)

Vols col·laborar-hi com a #DEV?
=============

Aquestes són les [issues prioritàries](https://github.com/ctrl-alt-d/django-aula/issues?q=is%3Aissue%20state%3Aopen%20label%3APrioritari)

Hi estàs interessat?

[FAQs](https://github.com/ctrl-alt-d/django-aula/issues?utf8=%E2%9C%93&q=is%3Aissue+label%3AFAQ+)

Necessites ajuda?
============

[Issues/Formularis d'ajuda](https://github.com/ctrl-alt-d/django-aula/issues/new/choose)
