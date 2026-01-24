# Guía per la construcció de la imatge de la Demo de Django-Aula amb Docker

**Aquesta guia** reuneix el coneixement adquirit i **serveix per crear la imatge que, actualment, fa el desplegamet de la Demo amb docker** de forma ràpida i no és el mètode recomanat per instal·lar la Demo basada en Docker.

**Serveix per crear exclusivament l'entorn de desenvolupament de la imatge Demo amb Docker i per a proves** 

---
# Índex

- [1. Requisits](#id1)
- [2. Instruccions de funcionament](#id2)
   * [2.1 Pas 1: Preparació (Clonar i Configurar Entorn)](#id21)
      + [2.1.1. Clona el repositori (inclou Makefile, Dockerfile, docker-compose.yaml i env.example)](#id211)
      + [2.1.2. Còpia dels arxius necessaris per construir la imatge de la demo de Docker](#id212)
      + [2.1.3 Edició (opcional) del fitxer de variables d'entorn](#id213)
      + [2.1.4. Ajustar la ubicació d'alguns arxius](#id214)
   * [2.2 Pas 2: Construir la imatge i Iniciar l'Entorn](#id22)
      + [2.2.1 Construir la imatge per la Demo de django-aula](#id221)
      + [2.2.2 Iniciar l'entorn i servir la Demo (runserver)](#id222)
   * [2.3 Pas 3: Carregar les Dades de Demostració](#id23)
   * [2.4 Pas 4: Accés a la Demo de Django-Aula](#id24)
   * [2.5 Pas 5: Extracció de les dades carregades en format sql i reubicar-les](#id25)

---

<a name="id1"></a>
## 1. Requisits

* **Sistema Operatiu:** Ubuntu Server 22.04 LTS o Debian 13.
* **Accés:** Es requereix un usuari amb accés a `sudo`.  
  **[Documentació per crear un nou usuari amb permisos de `sudo`](../ajuda-install/USUARI_SUDO.md)** 

<a name="id2"></a>
## 2. Instruccions de funcionament

El projecte fa servir l'arxiu `Makefile` com a capa d'abstracció. Aixó significa que en lloc d'escriure comandes llargues de `docker compose`, s'utilitzen targets senzills de `make` que executen les instruccions complexes de fons. Algunes d'aquests instruccions s¨®n:

| Comanda `make` | Qu¨¨ fa realment (Comanda `docker-compose`) | Propòsit |
| :--- | :--- | :--- |
| **`make build`** | `docker compose -f docker-compose.demo.yml build --no-cache web` | Construeix la imatge que utilitzarà el contenidor per la Demo de Django-Aula). |
| **`make start`** | `docker compose -f docker-compose.demo.yml up` | Construeix i inicia els contenidors (Web per Django-Aula i DB per PostgreSQL). |
| **`make serve`** | `docker compose -f docker-compose.demo.yml up -d` | Construeix i inicia els contenidors, com make start, però deixant el terminal operatiu. |
| **`make stop`** | `docker compose -f docker-compose.demo.yml stop` | Atura el funcionament dels contenidors Web i DB en funcionament. |
| **`make down`** | `docker compose -f docker-compose.demo.yml down -v` | Atura i elimina els contenidors i la xarxa, ideal per netejar l'entorn. |
| **`make load_demo_data`** | `docker compose -f docker-compose.demo.yml exec web python manage.py loaddemodata` | Genera i carrega les dades de demostració al contenidor DB de PostgreSQL. |

<a name="id21"></a>
### 2.1 Pas 1: Preparació (Clonar i Configurar Entorn)

<a name="id211"></a>
#### 2.1.1. Clona el repositori (inclou Makefile, Dockerfile, docker-compose.yaml i env.example)

La següent comanda clonarà el repositori i crearà una carpeta anomenada `django-aula`.

```bash
git clone https://github.com/ctrl-alt-d/django-aula.git django-aula
cd django-aula
```

Dins el repositori trobarem el directori `docker` que conté tots els arxius relacionats amb aquest entorn. Haurem de copiar els que necessitem al directori arrel del projecte clonat.

<a name="id212"></a>
#### 2.1.2. Còpia dels arxius necessaris per construir la imatge de la demo de Docker

Necessitem que al directori arrel del projecte hi hagi els següents arxius:
- **Dockerfile**: El creador de la imatge de la Demo de Django-Aula.
- **.dockerignore**: Dins d'aquest arxiu s'explicita quins arxius del repositori clonat es volen excloure de la imatge de la Demo que generarà l'arxiu Dockerfile.
- **docker-compose.demo.yml**: S'encarrega de crear el nou contenidor de la Demo, aixi com d'aixecar d'altres contenidors necessaris, com el de PostgreSQL, i d'enllaçar-los.
- **Makefile**: Arxiu opcional facilitador, però molt útil, que permet, amb comandes senzilles, fer operacions essencials com posar en execució els contenidors, detenir-los, o d'altres.
- **.env**: Arxiu que guarda els noms en variables d'entorn que necessitarà PostgreSQL per crear i gestionar la base de dades de la Demo i les possibles IPs de les màquines on s'hi voldrà instal·lar la Demo.

Tots aquests arxius es troben dins la carpeta `docker` però allà tenen d'altres noms. Per crear una nova imatge de la Demo de Django-Aula necessitarem copiar els següents arxius, canviar-los el nom i deixar-los al directori arrel del projecte:

**A REVISAR - EN CONSTRUCCIÓ**

```bash
cp docker/Dockerfile.demo.automatica Dockerfile && \
cp docker/.dockerignore.demo .dockerignore && \
cp docker/docker-compose.demo.manual.yml docker-compose.demo.yml && \
cp docker/Makefile.demo.manual Makefile && \
cp docker/env.example .env
```

Comprovi que s'han copiat tots els arxius abans de proseguir.

<a name="id213"></a>
#### 2.1.3 Edició (opcional) del fitxer de variables d'entorn

L'arxiu `.env`, copiat a partir de l'arxiu d'exemple, conté les variables de connexió a la base de dades (PostgreSQL).

Per fer proves pots utilitzar les credencials existents per defecte ('secret'), però si la intenció és crear realment un nou contenidor Demo millorat, el millor és editar les variables de la base de dades i canviar els seus valors.

```bash
nano .env
```

<a name="id214"></a>
#### 2.1.4. Ajustar la ubicació d'alguns arxius

En el procès de creació del contenidor Django-Aula:demo existent i allotjat en Docker-Hub hem vist que era necessari copiar temoralment un seguit d'arxius que al repositori es troben a un directori a un altre directori diferent.

Concretament, el procès que fallava era l'últim, el de la càrrega de les dades que es feia amb l'ordre `make load_demo_data` que és el que s'encarrega de generar les dades i d'emplenar la base de dades en PostgreSQL amb les dades fictícies de la Demo. Aquesta còpia, que ara per ara cal fer és temporal, i només serveix per crear la imatge que farà servir el contenidor Web (Django-Aula), d'aquesta forma tot es trobarà on ara mateix la Demo programada per l'equip de desenvolupament espera trobar aquests arxius.

```bash
mkdir static
cp -r demo/static-web/demo static/
```
Després d'aquesta operaciò hauria d'haver el directori `./static/demo`a l'arrel de projecte amb, bàsicament, un seguit d'arxius d'imatges i un arxiu html.

<a name="id22"></a>
### 2.2 Pas 2: Construir la imatge i Iniciar l'Entorn

<a name="id221"></a>
#### 2.2.1 Construir la imatge per la Demo de django-aula

Per construir la imatge farem servir la comanda `make build`, definida a l'arxiu `Makerfile`

```bash
make build
```

<a name="id222"></a>
#### 2.2.2 Iniciar l'entorn i servir la Demo (runserver)

Per iniciar l'entorn i poder servir tant la Demo de Django-Aula com la base de dades de PostgreSQL, que ara està buïda de dades, es pot fer de dues maneres:

* Si es vol deixar el terminal sense accés a la línia de comandaments però que ens mostri la informaciò de l'inici del servidor i del que està passant:
   ```bash
   make start 
   ```
* Si es vol tenir un terminal amb accés a la línia de comandaments però que NO ens mostri la informació de l'inici del servidor i del que està passant:
   ```bash
   make serve 
   ```

<a name="id23"></a>
### 2.3 Pas 3: Carregar les Dades de Demostració

Per carregar les dades necessitem un terminal operatiu. Si hem fet servir `make serve`, ja el tindrem, per¨ò si hem fet servir `make start` haurem d'obrir un altre terminal amb SSH per poder procedir a la càrrega de les dades.

Amb un terminal operatiu podem comprovar si els contenidors s'han creat i es troben actius amb `docker ps`. Si tot és correcte es poden carregar les dades de demostració de la Demo de django-aula:

```bash
make load_demo_data
```
A títol informatiu, la comanda anterior executa `python manage.py loaddemodata` dins del contenidor 'web' i triga bastant temps en executar-se.

<a name="id24"></a>
### 2.4 Pas 4: Accés a la Demo de Django-Aula

Si tot ha anat bé, l'aplicació s'executarà dins del contenidor web, i el port a fer servir serà el port 8000 perquè l'arxiu `docker-compose.yaml` els ha mapejat i els ha fet coincidir:

* Si hi ha disponible un escriptori gràfic, es pot escriure al navegador, l'IP 127.0.0.1. Si és una màquina virtual amb xarxa NAT i hem fet un mapeat de ports, de tal manera que el port 127.0.0.1 de la màquina _host_ apunti a la IP de la màquina virtual _guest_ es podrà accedir a la Demo amb un navegador des de la màquina anfitrionia (host):

  *http://127.0.0.1:8000*

* Si s'està instal·lant la demo de Django-Aula a una màquina virtual amb xarxa bridge i es té configurada tal i com s'explica a l'arxiu [INSTAL·LACIÓ MANUAL DE LA DEMO](INSTALL_MANUAL_DEMO.md), tindrà una IP estàtica configurada (p. ex., 192.168.18.140). En aquest cas també d'hauria de poder accedir des qualsevol ordinador de la xarxa interna utilitzant:

  *http://192.168.18.140:8000*


<a name="id25"></a>
### 2.5 Pas 5: Extracció de les dades carregades en format sql i reubicar-les

Un cop s'hagi comprovat que els contenidors estan corrent, que tenim accés al web i que podem entrar amb qualsevol dels usuaris creats amb la contrasenya per defece proporcionada, és el moment d'extraure les dades de la base de dades del contenidor *demo_db* en format sql fora del contenidor de PostgreSQL. Això ho fem amb:

```bash
docker compose exec demo_db pg_dump -U <usuari> -d <db_name> > docker/dades_demo.sql
```
On \<usuari> i \<db_name> son els valors de les variables corresponents que hi ha definides a l'arxiu .env i ja no seran els que venen per defecte perquè els haurem canviat.

L'arxiu de dades *sql* ha de tenir per nom `dades_demo.sql` i s'ha d'ubicar dins la carpeta docker perquè el script d'automatització és allà on espera trobar-lo i, per tant, és el que caldrà actualitzar en el repositori oficial de Github.
