# Instal·lació de la Demo de Django-Aula amb Docker

Aquest document explica com posar en funcionament, d'una manera fàcil i automatitzada, una Demo de Django-Aula, tant per un usuari normal com per un desenvolupador de codi que vulgui contribuir amb el projecte.

És necessar i imprescindible instal·lar l'entorn de Docker i docker-compose si no s'ha fet abans:

  👉 **[Guia per la instal·lació de Docker i docker-compose](install_entorn_docker.md)**  (Es pot obviar si ja s'ha fet)

El procés d'instal·lació construeix la imatge de la Demo a tal fi de tenir sempre la última versió del programari disponible.

La Demo pot ser instal·lada tant a una màquina aïllada de cap xarxa, com a una màquina en xarxa local com a un servidor públic que tingui un domini o subdomini associat.

**Només cal descarregar i executar un arxiu (script) d'instal·lació per posar-la en marxa**.

---

# Ìndex

- [1. Descàrrega i execució del script per posar en marxa la Demo](#id1)
- [2. Funcionament del script automatitzat per la instal·lació de la Demo](#id2)
   - [2.1 Què fa l'automatització?](#id21)
   - [2.2 Arxius descarregats amb la instal·lats i la seva funció](#id22)
   - [2.3 Versió per a desenvolupadors (DEV)](#id23)
- [3. Informació sobre l'arxiu `Makefile` i les ordres disponibles](#id3)
- [4. Accés a la Demo un cop instal·lada i en correcte funcionament](#id4)
   - [4.1 Sistemes operatius que disposin d'un entorn gràfic local](#id41)
   - [4.2 Màquina virtualitzada amb xarxa NAT configurada](#id42)
   - [4.3 Màquina virtualitzada amb xarxa bridge configurada o servidor públic (VPS)](#id43)

---

<a name="id1"></a>
## 1. Descàrrega i execució del script per posar en marxa la Demo

El script d'automatització està preparat per desplegar una Demo tant per un usuari normal com per un desenvolupador que vulgui fer canvis en el codi i observar-les a la Demo.

Es recomana crear un directori, dins el directori de l'usuari instal·lador, on es descarregarà el script i on es guardaran els arxius necessaris per desplegar la Demo de Django-Aula. Per exemple `demo-djau.docker`:

```bash
mkdir demo-djau-docker
cd demo-djau-docker
```

Un cop creat el directori on s'instal·larà la Demo només caldrà descarregar el script automatitzat d'instal·lació. Amb la comanda següent no només es descarrega l'arxiu sinó que començarà a executar-se automàticament:

**Instal·lació normal de la Demo:**

```bash
wget -q -O install_demo_docker.sh https://raw.githubusercontent.com/ctrl-alt-d/django-aula/refs/heads/master/docker/install_demo_docker.sh && chmod +x install_demo_docker.sh && bash ./install_demo_docker.sh
```

**Instal·lació de la Demo per a desenvolupadors:**

```bash
wget -q -O install_demo_docker.sh https://raw.githubusercontent.com/ctrl-alt-d/django-aula/refs/heads/master/docker/install_demo_docker.sh && chmod +x install_demo_docker.sh && bash ./install_demo_docker.sh -d
```

<a name="id2"></a>
## 2. Funcionament del script automatitzat per la instal·lació de la Demo

<a name="id21"></a>
### 2.1 Què fa l'automatització?

El script automatitzat du a terme vàries tasques, que són:

1 - Clonar el repositori de l'aplicatiu al directori on s'ha descarregat el script instal·lador.

2 - Copiar i situar correctament els arxius necessaris per poder fer el desplegament dels contenidors de Docker.  

3 - Instal·lar la comanda `make` si no es troba instatal·lada en el sistema. Si fos el cas, demanarà la contrasenya per activar el permís de `sudo`.  

4 - Facilitar l'edició de l'arxiu *.env* per configurar el tipus de màquina on es vol instal·lar la Demo mitjançant la llista *ALLOWED_HOSTS*:  
  - **Màquina aïllada o virtualitzada amb xarxa NAT**: No caldrà afegir res a la llisa. Per defecte la Demo se serveix en *localhost:8000* (127.0.0.1:8000)  
  - **Màquina en xarxa local o virtualitzada amb xarxa bridge:** Caldrà afegir l'IP de la màquina a la xarxa local.
  - **Servidor públic (VPS)**: Caldrà afegir l'IP pública del servidor i, si se'n diposa, el domini i/o subdominis que estiguin apuntant a aquesta IP pública.  

5 - Amb els arxius preparats, posar en marxa els dos contenidors necessaris pel funcionament de la Demo, un per la pròpia Demo, anomenat demo_web, i un altre per la base de dades PostgreSQL, anomenat demo_db.  

6 - Comprovar que el contenidor PostgreSQL estigui llest i el motor de PostgresSQL preparat per rebre les dades de demostració que es generaran.

7 - Generar les dades de demostració per visualitzar la mostra d'un horari escolar fictici.

8 - Engegar el servidor de proves de python per accedir a l'aplicatiu en format Demo (Aquest servidor no s'ha de fer servir per desplegar l'aplicació real).

9 - Mostrar l'estat dels contenidors desplegats per comprovar que estan funcionant correctament.
  
<a name="id22"></a>
### 2.2 Arxius necessaris pel desplegament de la Demo i la seva funció

Els arxius que el desplegament de la Demo necessita són:

1 - `Dockerfile`
2 - `docker-compose.yml` o `docker-compose.dev.yml`
3 - `.env`
4 - `.dockerignore`
5 - `Makefile`

Aquesta instal·lació us proporciona els següents fitxers, ubicats al vostre directori de treball:

| Fitxer | Funció | Annotacions |
| :--- | :--- | :--- |
| **`Dockerfile`** | Defineix com es construirà la imatge del servei **web** (Django-Aula) |  |
| **`docker-compose.yml`** | Defineix els serveis **web** (Django-Aula) i **db** (PostgreSQL). | Utilitza la imatge oficial de PostgreSQL i defineix com es desplegarà la imatge de la Demo. |
| **`docker-compose.dev.yml`** | Versió per a desenvolupadors que defineix els serveis **web** (Django-Aula) i **db** (PostgreSQL). | Similar a l'anterior però munta el repositori clonat dins el contenidor web per poder modificar el codi i veure els resultats sobre la Demo. |
| **`.env`** | Conté les credencials de la base de dades i la llista *ALLOWED_HOSTS*. | **No cal modificar la secció de la base de dades**. En canvi pot ser necessari afegir IP i/o dominis a la llista *ALLOWED_HOSTS*. |
| **`.dckerignore`** | Defineix els arxius del repositori que no cal inserir dins el contenidor de la Demo. |  |
| **`Makefile`** | Simplifica la gestió dels contenidors amb ordres curtes. | Inclou comandes essencials, tant per la versió normal de la Demo com per la versió per desenvolupadors. |


<a name="id23"></a>
### 2.3 Versió per a desenvolupadors (DEV)

El script automatitzat facilita també la instal·lació de la Demo pensant en els desenvolupadors de codi. S'instal·la amb el tag -d o --dev al darrera del nom del script i té dues diferències fonamentals respecte a la versió normal:

- 1 - Munta tot el repositori dins el contenidor web per poder treballar amb el codi i que els canvis es poden reflectir a la Demo.
- 2 - Dona a escollir entre generar o no les dades fictícies per omplir la base de dades.

<a name="id3"></a>
## 3. informació sobre l'arxiu `Makefile` i les ordres disponibles

El fitxer `Makefile` simplifica la interacció amb els contenidors de Docker.

Les comandes disponibles per la Demo són:

| Comanda | Funció | Ordre Subjacent |
| :--- | :--- | :--- |
| **`make build`** | Construeix la imatge del servei Web (Demo DjAu). | `docker compose -f docker-compose.yml build --no-cache web` |
| **`make serve`** | Posa en marxa els serveis (Web i DB) en segon pla (detached). | `docker compose -f docker-compose.yml up -d` |
| **`make stop`** | Atura els serveis sense eliminar els contenidors ni les dades. | `docker compose -f docker-compose.yml stop` |
| **`make down`** | Atura els serveis, elimina els contenidors i **elimina permanentment la base de dades** | `docker compose -f docker-compose.yml down -v` |
| **`make logs`** | Mostra els logs de tots dos serveis en temps real. | `docker compose -f docker-compose.yml logs -f` |

Les comandes disponibles per la versió per a desenvolupadors (DEV) són:

| Comanda | Funció | Ordre Subjacent |
| :--- | :--- | :--- |
| **`make dev-build`** | Construeix la imatge del servei Web (Demo DjAu). | `docker compose -f docker-compose.dev.yml build --no-cache web` |
| **`make dev-serve`** | Posa en marxa els serveis (Web i DB) en segon pla (detached). | `docker compose -f docker-compose.dev.yml up -d` |
| **`make dev-stop`** | Atura els serveis sense eliminar els contenidors ni les dades. | `docker compose -f docker-compose.dev.yml stop` |
| **`make dev-down`** | Atura els serveis, elimina els contenidors i **elimina permanentment la base de dades** | `docker compose -f docker-compose.dev.yml down -v` |
| **`make dev-logs`** | Mostra els logs de tots dos serveis en temps real. | `docker compose -f docker-compose.dev.yml logs -f` |
| **`make dev-load_demo_data`** | Carrega fixtures i genera les dades fictícies per la Demo. | `python manage.py loaddata aula/apps/*/fixtures/dades.json i python manage.py loaddemodata` |
| **`make dev-makemigrations`** | Comprova canvis als models i creant migracions. | `docker exec -it dev_web python manage.py makemigrations` |
| **`make dev-shell`** | Entrant a la consola de Django. | `docker exec -it dev_web python manage.py shell` |
| **`make dev-bash`** | Entra al terminal del contenidor web. | `docker exec -it dev_web bash` |

**Detall de les ordres del `Makefile`**

Per a referència, les ordres exactes del Makefile són:

```makefile
build:
        $(INFO) "Construint imatge de la Demo..."
        docker compose -f docker-compose.yml build

serve:
        $(INFO) "Aixecant serveis de la Demo..."
        docker compose -f docker-compose.yml up -d
        $(EXITO) "Demo en marxa al port 8000"

stop:
        $(INFO) "Aturant serveis de la Demo..."
        docker compose -f docker-compose.yml stop

down:
        $(INFO) "Eliminant contenidors i xarxes de la Demo..."
        docker compose -f docker-compose.yml down

logs:
        docker compose -f docker-compose.yml logs -f web

# --- COMANDES DE DESENVOLUPAMENT (DEV) ---

dev-build:
        $(INFO) "Construint imatge de Desenvolupament..."
        docker compose -f docker-compose.dev.yml build

dev-serve:
        $(INFO) "Aixecant serveis de Desenvolupament (amb volums en viu)..."
        docker compose -f docker-compose.dev.yml up -d
        $(EXITO) "Entorn de Dev en marxa al port 8000"

dev-stop:
        $(INFO) "Aturant serveis de Dev..."
        docker compose -f docker-compose.dev.yml stop

dev-down:
        $(INFO) "Eliminant contenidors i xarxes de Dev..."
        docker compose -f docker-compose.dev.yml down

dev-logs:
        docker compose -f docker-compose.dev.yml logs -f web

# --- GESTIÓ DE DADES I DJANGO (DEV) ---

dev-load_demo_data:
        $(INFO) "Carrega fixtures i dades de demo..."
        @printf $(GRIS)
        @docker exec -it dev_web bash -c "python manage.py loaddata aula/apps/*/fixtures/dades.json"
        @docker exec -it dev_web python manage.py loaddemodata
        @printf $(NC)
        $(EXITO) "Dades de la Demo carregades amb èxit."

dev-makemigrations:
        $(INFO) "Comprovant canvis als models i creant migracions..."
        docker exec -it dev_web python manage.py makemigrations

dev-shell:
        $(INFO) "Entrant a la consola de Django..."
        docker exec -it dev_web python manage.py shell

dev-bash:
        $(INFO) "Entrant al terminal del contenidor web..."
        docker exec -it dev_web bash
```

<a name="id4"></a>
## 4. Accés a la Demo un cop instal·lada i en correcte funcionament

Un cop executat l'arxiu d'instal·lació automatitzada i amb els arxius necessaris descarregats, construida la imatge amb `make build ` i executada la comanda `make serve`, l'aplicació estarà accessible en el port **8000** fent servir el servidor web per a proves de Django.

Per accedir-hi dependrà del tipus de màquina on hagim desplegat la Demo.

<a name="id41"></a>
### 4.1 Sistemes operatius que disposin d'un entorn gràfic local

Si el sistema operatiu on s'executa Docker té entorn gràfic, podeu accedir directament amb el seu propi navegador escrivint l'url:

```
http://localhost:8000 o també http://127.0.0.1:8000
```

<a name="id42"></a>
### 4.2 Màquina virtualitzada amb xarxa NAT configurada

Si hem desplegat la Demo dins una màquina virtual (VM) amb **xarxa NAT** cal fer un mapeig de ports. Suposant que el mapeig ha consistit en assignar el port `127.0.0.1` de la màquina anfitriona (*host*) per a que apunti a la IP de la màquina virtualitzada (*guest*) es podrà accedir a la Demo amb un navegador d'internet des de la màquina anfitriona *host*:

```
http://127.0.0.1:8000
```     

<a name="id43"></a>
### 4.3 Màquina virtualitzada amb xarxa bridge configurada o servidor públic (VPS)

Amb una màquina virtualitzada amb Xarxa Bridge, tinguin o no IP Estàtica, haurem hagut d'afegir l'IP de la màquina virtual a l'arxiu `.env`, preferíblement fent servir el script automatitzat, però sempre ho podem fer manualment. 

L'arxiu *.env* facilita afegir la IP perquè el que realment fa és afegir l'IP de la màquina a l'arxiu `demo.py` que es troba dins el contenidor *demo_web*. Afegir la IP manualment a la llista `ALLOWED_HOSTS` és molt més complicat dins un contenidor i sobretot **temporal**, perquè si detenim el contenidor i el tornem a aixecar, el canvi efectuat es perdria.

Suposant que la IP de la màquina virtualitzada fos la 192.168.18.168

Des d'un navegador de qualsevol màquina de la xarxal local interna s'hauria de poder accedir a la Demo escrivint l'url:

```
http://192.168.18.168:8000
```

Si fos un VPS amb un domini o subdomini com *demo.djau.elteudomini.cat*, escriuríem, des del qualsevol dispositiu connectat a internet, com per exemple un mòbil, el següent:

```
http://demo.djau.elteudomini.cat:8000
```   


> **IMPORTANT:** Aquesta Demo Docker corre amb un servidor web de proves de Django, pensat pel desenvolupament de l'aplicatiu, i és molt limitat. No està preparat ni per acceptar connexions segures de tipus https ni per fer front a atacs de hackers. La seva perdurabilitat en el temps no es pot assegurar.
