# Contingut del Directori Docker

Aquest directori conté tots els fitxers creats per gestionar el desplegament de la Demo de Django-Aula i per la creació d'imatges de l'aplicació Django-Aula mitjançant contenidors Docker.

El directori conté els fitxers de configuració pel desplegament ràpid de la Demo i els fitxers per construir-la, així com algun arxiu més que obre la porta per futurs desenvolupaments de l'aplicatiu sencer amb Docker.

---

## 1. Requisit previ. Instal·lació de Docker CE i docker-compose en el sistema operatiu

Segons es descriu a les instruccions principals del repositori, hi ha dues maneres d'instal·lar Docker en el sistema operatiu, la manual i l'automatitzada.

| Nom de l'Arxiu | Descripció | Ús Principal |
| :--- | :--- | :--- |
| `install_docker.sh` | **Script d'instal·lació automatitzada de Docker.** Descarrega i configura tot alló que cal per instal·lar l'entorn Docker i docker-compose en el sistema. | Instal·lar Docker en el sistema operatiu. |


## 2. Arxius de Configuració de Desplegament Ràpid

Aquests arxius s'utilitzen per a l'**Instal·lació de la Demo** amb Docker de forma automatitzada, tal com s'explica al document principal. Són la base per a un desplegament senzill i automatitzat típic amb Docker.

| Nom de l'Arxiu | Descripció | Ús Principal |
| :--- | :--- | :--- |
| `install_quick_demo_docker.sh` | **Script d'instal·lació automatitzada.** Descarrega, col·loca els arxius de configuració a l'arrel del projecte, els reanomena i desplega els contenidors automàticament. | Desplegament actual de la Demo. |
| `docker-compose.demo.automatica.yml` | Fitxer de configuració de serveis (Web + DB) utilitzat per la Demo. | Serà l'arxiu `docker-compose.yml` que desplegarà la Demo. |
| `Makefile.demo.automatica` | Defineix les ordres de gestió simplificades (`serve`, `stop`, `logs` i `down`) per a la Demo. | Serà l'arxiu `Makefile` que facilitarà el desplegament de la Demo. |
| `env.demo.automatica` | Arxiu de variables d'entorn per la base de dades de PostgreSQL que farà servir la Demo. | Serà l'arxiu `.env` que llegirà l'arxiu `docker-compose.yml`. |
| `dades_demmo.sql` | És el fitxer SQL (`.sql`) amb les dades de demostració precarregades. | El contenidor de PostgreSQL llegeix aquest fitxer en iniciar-se i omple la base de dades de forma ràpida i automàtica. |

---

## 3. Fitxers de Construcció i Entorns de Desenvolupament

Es troben ubicats al directori **build-dev** i són els que es fan servir per **crear noves imatges**, tant per la Demo com per qualsevol altre objectiu.

| Nom de l'Arxiu | Descripció | Finalitat |
| :--- | :--- | :--- |
| `Dockerfile.demo.automatica` | Defineix com es va construir la imatge per a la Demo actualment desplegable de forma automatitzada . | Utilitzat per crear la imatge pujada al repositori d'imatges *Docker Hub*. |
| `docker-compose.demo.manual.yml` | És el fitxer de partida a partir del qual es va construir el *docker-compose.demo.automatica.yml*. | Ús per a desenvolupadors locals que volen accedir a *shells*, *migrations*, etc. |
| `docker-compose.dev.yml` | Configuració completa dels serveis per a **l'entorn de Desenvolupament** (DEV). (ara en desenvolupament) | Facilitar crear un entorn de desenvolupament de l'aplicació bassat en Docker i pensat per a desenvolupadors locals que volen accedir a *shells*, *migrations*, etc. |
| `Makefile.demo.manual` | És el fitxer de partida a partir del qual es va construir el *Makefile.demo.automatica*. Interacciona amb el fitxer *docker-compose.demo.yml*.| És l'arxiu que facilitarà la creació i desplegament de les noves Demos que es vulguin crear. |
| `Makefile.demo.complet` | Conté conjuntament les instruccions per treballar tant amb la versió manual com la versió *DEV*. | Serveix com a referència i com a base per a entorns de Producció/Desenvolupament. |
| `env.example` | Arxiu de variables d'entorn *sense personalitzar* per la base de dades de PostgreSQL que farà servir la Demo. | Base per crear el fitxer `.env` per crear una imatge de Django-Aula amb Docker. |
| `.dockerignore.demo` | Especifica els fitxers que s'han d'excloure del context de construcció de la imatge de la Demo. | Optimització i seguretat de la imatge Docker final. |
