# Contingut del Directori Docker

Aquest directori els fitxers necessaris per gestionar el desplegament d'una Demo de Django-Aula, tant per la versió normal com per la versió per desenvolupament, mitjançant contenidors Docker.

Per informació més detallada, consulti la documentació detallada per la [Instal·lació de la demo de forma automatitzada amb Docker](../docs/USER_MANUAL/demo/install_demo_docker.md)
---

## 1. Requisit previ. Instal·lació de Docker CE i docker-compose en el sistema operatiu

Segons es descriu a les instruccions principals del repositori, hi ha dues maneres d'instal·lar Docker en el sistema operatiu, la manual i l'automatitzada.

| Nom de l'Arxiu | Descripció |
| :--- | :--- |
| `install_docker.sh` | **Script d'instal·lació automatitzada de Docker.** Descarrega i configura tot allò que cal per instal·lar l'entorn Docker i docker-compose en el sistema. |


## 2. Arxius necessaris pel desplegament de la Demo

Aquests arxius s'utilitzen per a l'**Instal·lació de la Demo** amb Docker de forma automatitzada, tal com s'explica al document principal. Són la base per a un desplegament senzill i automatitzat típic amb Docker.

| Nom de l'Arxiu | Descripció |
| :--- | :--- |
| `install_demo_docker.sh` | **Script d'instal·lació automatitzada.** Descarrega, col·loca els arxius de configuració a l'arrel del projecte, els reanomena i desplega els contenidors automàticament. |
| `docker-compose.yml` | Fitxer de configuració de serveis (Web + DB) utilitzat per la Demo. |
| `docker-compose.dev.yml` | Versió per a desenvolupadors de codi del fitxer de configuració de serveis (Web + DB) que crea la Demo. |
| `Dockerfile` | Defineix com es construirà la imatge de la Demo |
| `Makefile` | Facilita el desplegament de la Demo mitjançant ordres de gestió simplificades, com ara `serve`, `stop`, `logs`, `down`, etc. |
| `.env` | Arxiu de variables d'entorn per la base de dades de PostgreSQL que farà servir la Demo. |
| `.dockerignore` | Declaració d'arxius que no son necessaris incloure dins el contenidor docker de la Demo |
