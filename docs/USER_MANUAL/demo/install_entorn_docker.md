# Guia d'Instal·lació de Docker i Docker Compose

Aquesta guia detalla el procés d'instal·lació de l'entorn **Docker CE** i **Docker Compose** en servidors amb sistemes operatius basats en Debian, com Ubuntu o d'altres.

Cal tenir en commpte que **És un pas obligatori per dur a terme qualsevol operació amb Docker**. Concretament s'instal·larà:
* **Docker CE**
* **Docker Compose**

---

# Índex

  - [1. Requisits de Servidor](#id1)
  - [2. **Procés automatitzat d'Instal·lació de l'entorn Docker (Recomanat)**](#id2)
  - [3. Procés manual d'instal·lació de l'entorn Docker (pas a pas)](#id3)
    - [3.1. Preparar el Sistema Operatiu](#id31)
    - [3.2. Afegir el Repositori Oficial de Docker](#id32)
    - [3.3. Instal·lar els Paquets de Docker](#id33)
    - [3.4. Comprovació final i autoinicialització](#id34)
	
---

<a name="id1"></a>
## 1. Requisits de Servidor

* **Sistema Operatiu:** Ubuntu Server 22.04 LTS o Debian 13.
* **Accés:** Es requereix un usuari amb Accés a `sudo`.  
   **[Documentació per crear un nou usuari amb permisos de `sudo`](../ajuda-install/usuari_sudo.md)** 

Es recomanen 10GB d'espai de disc mínim per a Debian 13 o 15GB per Ubuntu per instal·lar la Demo mitjançant Docker.
 
<a name="id2"></a>
## 2. Procés automatitzat d'Instal·lació de l'entorn Docker (Recomanat)

Per instal·lar l'entorn de Docker no cal crear cap directori expressament. Podem fer-ho a l'arrel del directori del nostre usuari perquè només caldrà descarregar-se un script que s'encarregarà de tot el procés d'instal·lació i preparació del sistema.

La instrucció a executar per descarregar i executar el script d'instal·lació automatitzada és:
 
```bash
wget -q -O install_docker.sh https://raw.githubusercontent.com/ctrl-alt-d/django-aula/refs/heads/master/docker/install_docker.sh && chmod +x install_docker.sh && sudo ./install_docker.sh
```

<a name="id3"></a>
## 3. Procés manual d'instal·lació de l'entorn Docker (Pas a pas)

Les instruccions del procés manual tenen l'objectiu de documentar tot el que cal fer per instal·lar l'entorn de Docker i facilitar l'ajustament del script d'automatització de la instal·lació, donat el cas.

Es basen en la [documentació oficial de Docker](https://docs.docker.com/engine/install/) per Debian (11, 12 i 13) i per Ubuntu (22.04 LTS, 24.04 LTS i 25.10).

**Executeu les ordres següents amb el vostre usuari** (p. ex., `djau`), **utilitzant `sudo` per obtenir els privilegis necessaris**.

<a name="id31"></a>
### 3.1. Preparar el Sistema Operatiu

Abans d'instal·lar Docker cal assegurar que no hi ha paquets de Docker no oficials instal·lats en el sistema:
```bash
sudo apt remove $(dpkg --get-selections docker.io docker-compose docker-doc podman-docker containerd runc | cut -f1)
```

Actualitzar la llista de paquets i instal·lem les dependéncies requerides per afegir repositoris amb HTTPS:
```bash
sudo apt update
sudo apt install ca-certificates curl
```

<a name="id32"></a>
### 3.2. Afegir el Repositori Oficial de Docker

Afegir la clau GPG oficial de Docker (necessària per verificar l'autenticitat dels paquets) i configurar el repositori.

```bash
# 1. Crear el directori per a la clau GPG:
sudo install -m 0755 -d /etc/apt/keyrings

# 2. Descarregar i afegir la clau GPG pel cas de Debian:
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc

# 3. Establir els permisos de la clau:
sudo chmod a+r /etc/apt/keyrings/docker.asc

# 4. Afegir el repositori al sistema pel cas de Debian:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/debian
Suites: $(. /etc/os-release && echo "$VERSION_CODENAME")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```

<a name="id33"></a>
### 3.3. Instal·lar els Paquets de Docker

Un cop afegit el repositori, cal actualitzar la llista i instal·lar el motor Docker i els seus components. S'ha aprofita per instal·lar ara també la comanda `make`.

```bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin make
```

<a name="id34"></a>
### 3.4. Comprovació final i autoinicialització

Es comprova l'estat del servei i s'assegura que s'inicia automàticament.

```bash
# Comprovar l'estat del servei (hauria de ser 'active'):
systemctl status docker

# Assegurar-se que el servei s'inicia amb el sistema:
sudo systemctl enable docker
```

<a name="id35"></a>
### 3.5 Afegir Usuari al Grup docker

Per poder executar ordres de Docker sense necessitat d'utilitzar sudo constantment, s'afegeix l'usuari al grup docker. (Cal substituir `djau` pel nom d'usuari que està instal·lant l'entorn):

```bash
sudo usermod -aG docker djau
```

**ATENCIÓ**: Perqué els permisos tinguin efecte, **cal tancar i tornar a obrir la sessió (desconnectar i tornar a connectar-se per SSH) o reiniciar la màquina.**
