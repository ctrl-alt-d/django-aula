# django-aula: Gestió Escolar - Software de Gestión de Centros Educatius

Gestió de presència, incidències i més per a Instituts, Escoles i Acadèmies.

<p align="center">
    <img src="http://i.imgur.com/YlCRTap.png" alt="Django-Aula responsive" width="70%">
</p>

[![Tecnologia](https://img.shields.io/badge/Tecnologia-Django%205.1-092E20.svg?style=for-the-badge&logo=django)](https://www.djangoproject.com/)
[![Database](https://img.shields.io/badge/Database-PostgreSQL-336791.svg?style=for-the-badge&logo=postgresql)](https://www.postgresql.org/)

[![Servei](https://img.shields.io/badge/Served%20with-Docker%20Compose-2496ED.svg?style=for-the-badge&logo=docker)](https://docs.docker.com/compose/)

[![Llicència](https://img.shields.io/badge/Llicència-MIT-2E8B57.svg?style=for-the-badge)](LICENSE)

**[Llicència i Crèdits](LICENSE)** | **EL PROGRAMA NO TÉ CAP GARANTIA, UTILITZEU-LO SOTA LA VOSTRA RESPONSABILITAT.**

---

# 📋 Índex de Continguts

- [1. Introducció](#introduccio)
- [2. Requisits del sistema operatiu per instal·lar Django-Aula](#requisits)
- [3. Desplegament d'una Demostració de Django-Aula amb Docker 🐳 ](#demodocker)
- [4. Instal·lació i càrrega de dades de Django-Aula per ús real a un Centre Educatiu](#produccio)
- [5. Equip Desenvolupador i Suport Tècnic](#dev-suport-tecnic)
   
---

<a name="introduccio"></a>
## Introducció

### Característiques Principals i Valor Afegit

Django-Aula és un sistema integral dissenyat per alleugerir la càrrega de treball del personal docent d'un centre educatiu, millorant la gestió acadèmica i de convivència, al mateix temps que possibilita mantenir informades les famílies.

El programa cobreix tots els aspectes clau de la gestió diària del centre educatiu: **Presència**, **Incidències**, **Actuacions**, **Sortides** i **Portal de Famílies**. Per a més detalls:

➡️ **[Sobre les CARACTERÍSTIQUES generals](docs/USER_MANUAL/caracteristicas.md)**

➡️ **[Sobre les FUNCIONALITATS concretes, amb captures de pantalla](docs/USER_MANUAL/funcionalidades.md)**

Es pot consultar un índex complet amb tota la informació sobre Django-Aula:

➡️ **[Índex complet sobre Django-Aula](docs/README.md)**


<a name="requisits"></a>
## Requisits del sistema operatiu per instal·lar Django-Aula

Django-Aula s'instal·la en un servidor amb sistema operatiu Linux i està adaptat per Debian 13, Ubuntu Server 24.04 LTS o superior, o derivats de la mateixa base. El hardware mínim és d'1 cpu (core), 1Gb de RAM i 10 o 15GB de disc dur per Debian Server o Ubuntu Server, respectívament.

Per qualsevol tipus d'instal·lació, ja sigui per un ús real o per l'entorn de demostració, és altament recomanable haver creat un usuari amb permisos de *SUDO*. [El procés està documentat.](docs/USER_MANUAL/ajuda-install/usuari_sudo.md)

---

<a name="demodocker"></a>
## Desplegament d'una Demostració de Django-Aula amb Docker 🐳 

L'entorn de demostració, conegut com Demo, és una versió funcional del sistema i que es pot posar en funcionament en pocs minuts. Disposa de dades fictícies (usuaris, professors, alumnat i un horari mínim) que faciliten observar l'aspecte visual i interaccionar, des de diferents rols, amb les funcionalitats de l'aplicatiu real Django-Aula.

El desplegament de la Demo es pot fer de dorma automatitzada, tot i que també es pot fer de forma manual, i s'aconsegueix amb l'execució de dues comandes i consta de dues passes consecutives:


### 1a - Instal·lació automàtica de Docker i Docker Compose

Des del directori de l'usuari instal·lador:

```bash
wget -q -O install_docker.sh https://raw.githubusercontent.com/ctrl-alt-d/django-aula/refs/heads/master/docker/install_docker.sh && \
chmod +x install_docker.sh && \
sudo ./install_docker.sh
```

### 2a - Instal·lació automàtica de la Demo de Django-Aula

Es recomana crear un subdirectori dins el directori de l'usuari instal·lador per instal·lar la Demo, en aquest exemple `demo-djau-docker`:

```bash
mkdir demo-djau-docker && cd demo-djau-docker && \
wget -q -O install_demo_docker.sh https://raw.githubusercontent.com/ctrl-alt-d/django-aula/refs/heads/master/docker/install_demo_docker.sh && \
chmod +x install_demo_docker.sh && \
bash ./install_demo_docker.sh
```

Tot i que el procés anterior és autònom i interactivament configurable, es recomana llegir la informació, molt més detallada del procés, segons el tipus de màquina (no virtualitzada, virtualitzada o servidor d'accés públic) on s'instal·larà la Demo. També hi haurà qui estarà interessat en dur a terme la instal·lació manual, tant de l'entorn de Docker com de la Demo. Per tots aquests casos es recomana consultar els següents detallats documents:


➡️ **[Instal·lació automatitzada de l'entorn de Docker i Docker Compose](docs/USER_MANUAL/demo/install_entorn_docker.md)**.

➡️ **[Instal·lació automatitzada de la Demo amb Docker](docs/USER_MANUAL/demo/install_demo_docker.md)**.

➡️ **[Instal·lació manual de la Demo (sense Docker)](docs/USER_MANUAL/demo/install_demo_manual.md)**.


<a name="produccio"></a>
## 🚀 Instal·lació i càrrega de dades de Django-Aula per ús real a un Centre Educatiu (Entorn de Producció)

### 1a part. Procés d'instal·lació.

Si vol instal·lar Django-Aula per fer-lo servir a un centre educatiu cal un servidor de producció, ja sigui un servidor públic (VPS) o un servidor local (xarxa local), que pot ser una màquina real o una màquina virtual (VM). Per tots aquests casos hi ha dues opcions:

* **Mètode Prioritari i recomanat: Desplegament completament automatitzat** amb scripts.  
➡️ **[GUIA COMPLETA D'INSTAL·LACIÓ AUTOMATITZADA](docs/install_djau_automatic_scripts.md)**

* Mètode Clàssic: Desplegament manual pas a pas.  
➡️ **[Instruccions de Desplegament Manual](docs/install_djau_manual.md)**

### 2a part. Procés de càrrega de dades

Després de la instal·lació el sistema estarà preparat per rebre les dades reals del centre educatiu pel curs escolar (alumnat, docents, aules, horaris, etc).

➡️ **[Instruccions per la càrrega de dades del centre educatiu](docs/README.md)**.

---

<a name="dev-suport-tecnic"></a>
## 📚 Equip Desenvolupador i Suport Tècnic

* **Vols col·laborar-hi com a #DEV?**  
Aquestes són les [Issues prioritàries](https://github.com/ctrl-alt-d/django-aula/issues?q=is%3Aissue%20state%3Aopen%20label%3APrioritari)
* **Preguntes d'ús freqüent**.  
[FAQs](https://github.com/ctrl-alt-d/django-aula/issues?utf8=%E2%9C%93&q=is%3Aissue+label%3AFAQ+)
* **Has trobat errors? Necessites ajuda?** Utilitza el Formulari per demanar ajuda o comunicar errors (*Issues*)  
[Issues/Formularis d'ajuda](https://github.com/ctrl-alt-d/django-aula/issues/new/choose)

---

