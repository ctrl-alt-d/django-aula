# Guia d'Instal·lació de Docker i Docker Compose

Aquesta guia detalla el procés d'instal·lació de l'entorn **Docker CE** i **Docker Compose** en servidors amb sistemes operatius basats en Debian, com Ubuntu o d'altres.

Cal tenir en commpte que **És un pas obligatori per dur a terme qualsevol operació amb Docker**. Concretarem s'instal·lara:
* **Docker CE**
* **Docker Compose**

---

# Índex

  - [1. Requisits de Servidor](#id1)
  - [2. **Procés automatitzat d'Instal·lació de l'entorn Docker (Recomanat)**](#id2)
  - [3. Procés d'instal·lació (Métode manual)](#id3)
    - [3.1. Preparació del Sistema Operatiu](#id31)
    - [3.2. Afegir el Repositori Oficial de Docker](#id32)
    - [3.3. Instal·lació dels Paquets de Docker](#id33)
    - [3.4. Comprovació final i autoinicialització](#id34)
	
---

<a name="id1"></a>
## 1. Requisits de Servidor

* **Sistema Operatiu:** Ubuntu Server 22.04 LTS o Debian 13.
* **Accés:** Es requereix un usuari amb Accés a `sudo`.  
   **[Documentació per crear un nou usuari amb permisos de `sudo`](../ajuda-install/usuari_sudo.md)** 

<a name="id2"></a>
## 2. Procés automatitzat d'Instal·lació de l'entorn Docker (Recomanat)

Per instal·lar l'entorn de Docker no cal crear cap directori expressament. Podem fer-ho a l'arrel del directori del nostre usuari perquè només caldrà descarregar-se un script que executarà tot el procés d'instal·lació i preparació del sistema.

La instrucció a executar per descarregar i executar el script d'instal·lació automatitzada és:
 
```bash
wget -q -O install_docker.sh https://raw.githubusercontent.com/ctrl-alt-d/django-aula/refs/heads/master/docker/install_docker.sh && chmod +x install_docker.sh && sudo ./install_docker.sh
```

<a name="id3"></a>
## 3. Procés d'instal·lació (Métode manual)

Les instruccions del procés manual tenen l'objectiu de documentar tot el que cal fer per instal·lar l'entorn de Docker i facilitar l'ajustament del script d'automatització de la instal·lació donat el cas.

Aquestes instruccions d'instal·lació que a continuació es descriuen han estat basades en el [blog de voidnull](https://voidnull.es/instalacion-de-docker-en-debian-13/).

**Executeu les ordres següents amb el vostre usuari** (p. ex., `djau`), **utilitzant `sudo` per obtenir els privilegis necessaris**.

<a name="id31"></a>
### 3.1. Preparació del Sistema Operatiu

Actualitzem la llista de paquets i instal·lem les dependéncies requerides per afegir repositoris amb HTTPS:
```bash
sudo apt update
sudo apt install apt-transport-https ca-certificates curl gnupg lsb-release
```

<a name="id32"></a>
### 3.2. Afegir el Repositori Oficial de Docker

Afegim la clau GPG oficial de Docker (necessària per verificar l'autenticitat dels paquets) i configurem el repositori.

```bash
# 1. Crear el directori per a la clau GPG:
sudo install -m 0755 -d /etc/apt/keyrings

# 2. Descarregar i afegir la clau GPG:
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 3. Establir els permisos de la clau:
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# 4. Afegir el repositori al sistema:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

<a name="id33"></a>
### 3.3. Instal·lació dels Paquets de Docker

Un cop afegit el repositori, actualitzem la llista i instal·lem el motor Docker i els seus components.

```bash
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

<a name="id34"></a>
### 3.4. Comprovació final i autoinicialització

Comprovem l'estat del servei i ens assegurem que s'inicia automàticament.

```bash
# Comprovar l'estat del servei (hauria de ser 'active'):
systemctl status docker

# Assegurar-se que el servei s'inicia amb el sistema:
sudo systemctl enable docker
```

<a name="id35"></a>
### 3.5 Afegir Usuari al Grup docker

Per poder executar ordres de Docker sense necessitat d'utilitzar sudo constantment, afegim l'usuari al grup docker. (Substituíu `djau` pel nom d'usuari que tingueu creat):

```bash
sudo usermod -aG docker djau
```

**ATENCIÓ**: Perqué els permisos tinguin efecte, **cal tancar i tornar a obrir la sessió (desconnectar i tornar a connectar-se per SSH) o reiniciar la màquina.**
