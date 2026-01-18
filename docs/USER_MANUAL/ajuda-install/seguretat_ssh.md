# 🛡️ Configuració de Seguretat Essencial del Servidor (SSH)

Aquest document recull les pràctiques clau per augmentar la seguretat de l'accés remot (SSH) al vostre servidor, protegint-lo contra atacs de força bruta i accessos no desitjats.

---
# Índex

- [1. Ús d'Usuaris Estàndard amb `sudo`](#id1)
- [2. Deshabilitar l'Accés Directe com a `root` per SSH (Seguretat Mínima)](#id2)
   - [2.1 Modificar el Fitxer de Configuració](#id21)
   - [2.2 Aplicar els Canvis](#id22)
- [3. Ús de Claus SSH (Seguretat Òptima)](#id3)
   - [3.1 Generació i Còpia de la Clau](#id31)
   - [3.2 Advertència de Pèrdua de Clau (Problema crític)](#id32)
- [4. Instal·lació de Fail2Ban (Protecció contra Atacs de Força Bruta)](#id4)
   - [4.1 Comandes d'Administració pel filtre SSH](#id41)
   - [4.2 Protecció del Servidor Web (Apache)](#id42)

---

<a name="id1"></a>
## 1. Ús d'Usuaris Estàndard amb `sudo`

És una pràctica de seguretat fonamental **no utilitzar mai l'usuari `root` per a tasques diàries** ni per a la instal·lació d'aplicacions com Django-Aula.

* **Risc:** L'usuari `root` té permisos absoluts. Si es compromet, l'atacant obté el control total del servidor.
* **Recomanació:** Totes les tasques d'instal·lació i manteniment s'han de fer amb un usuari estàndard amb permisos `sudo` (com l'usuari **`djau`** creat al document **[usuari_sudo](usuari_sudo.md)**).

---

<a name="id2"></a>
## 2. Deshabilitar l'Accés Directe com a `root` per SSH (Seguretat Mínima)

Per evitar que un atacant pugui intentar iniciar sessió directament com a `root` mitjançant força bruta, deshabilitarem aquesta opció a la configuració d'SSH del servidor.

<a name="id21"></a>
### 2.1 Modificar el Fitxer de Configuració

1.  Editeu el fitxer de configuració del servei SSH:
    ```bash
    sudo nano /etc/ssh/sshd_config
    ```

2.  Busqueu el paràmetre `PermitRootLogin`. Si està comentat (prefixat amb `#`), elimineu el símbol i ajusteu el valor:
    ```ini
    # Assegureu-vos que tingui aquest valor:
    PermitRootLogin no
    ```

3.  Guardeu i tanqueu el fitxer.

<a name="id22"></a>
### 2.2 Aplicar els Canvis

1.  Reinicia el servei SSH:
    ```bash
    sudo systemctl restart sshd
    ```

A partir d'aquest moment, només podreu accedir mitjançant SSH utilitzant els usuaris que hàgiu creat (com ara `djau`). Sempre podeu fer servir el usuari `root` si escriviu `sudo su` i `exit` per tornar al usuari original.

---

<a name="id3"></a>
## 3. Ús de Claus SSH (Seguretat Òptima)

L'accés mitjançant contrasenya (encara que sigui amb un usuari amb `sudo`) no és el més segur. El mètode **més segur** és utilitzar un parell de **claus SSH** (una clau privada en el vostre ordinador i la clau pública al servidor).

Aquest mètode garanteix que només els ordinadors que posseeixin la clau privada (amb la seva contrasenya de seguretat per a més seguretat, o *passphrase*) puguin accedir al servidor.

<a name="id31"></a>
### 3.1 Generació i Còpia de la Clau

Tot i que l'explicació detallada de la generació de claus es pot trobar en molts recursos en línia, el procés bàsic és:

1.  **Generar la Clau (al client):** Des del vostre ordinador local, genereu una clau RSA de 4096 bits i assigneu-li un nom, com ara `djau_vps`:
    ```bash
    ssh-keygen -f ~/.ssh/djau_vps -t rsa -b 4096
    ```
    * **Molt important:** Introduïu una contrasenya (*passphrase*) per protegir la clau privada.

2.  **Copiar la Clau Pública (al servidor):** Copieu la clau pública al nou usuari del servidor. Substituïu `djau@host` per l'usuari i la IP/Domini del servidor:
    ```bash
    ssh-copy-id -i ~/.ssh/djau_vps djau@host
    ```

<a name="id32"></a>
### 3.2 Advertència de Pèrdua de Clau (Problema crític)

Si el servidor no disposa d'un **terminal de consola d'emergència** (com el que solen oferir els VPS), i **perdeu la clau privada**, no podreu entrar al servidor de cap manera.

* **Recomanació:** Feu sempre una **còpia de seguretat** de la clau privada generada en un lloc segur (fora de línia o xifrat), per si l'ordinador local es perd o es fa malbé.

---

<a name="id4"></a>
## 4. Instal·lació de Fail2Ban (Protecció contra Atacs de Força Bruta)

**Fail2Ban** és un servei essencial que monitoritza els registres del sistema i bloqueja temporalment les adreces IP que intenten accedir repetidament al servidor (p. ex., provant milers de contrasenyes en SSH).

L'script d'instal·lació automatitzada de Django-Aula ja s'encarrega d'instal·lar i configurar el *jail* (filtre) per a SSH, però és important saber-ne el funcionament.

<a name="id41"></a>
### 4.1 Comandes d'Administració pel filtre SSH

| Acció | Comanda |
| :--- | :--- |
| **Comprovar l'estat general:** | `sudo fail2ban-client status` |
| **Comprovar l'estat del filtre SSH i les IPs bloquejades:** | `sudo fail2ban-client status sshd` |
| **Desbloquejar una IP manualment:** | `sudo fail2ban-client set sshd unbanip 1.2.3.4` |
| **Veure el log de fail2ban:** | `sudo less /var/log/fail2ban.log` |
| **Obtenir un llistat amb el nombre de vegades que una IP ha estat bloquejada:** | `sudo zgrep -h "Ban " /var/log/fail2ban.log* | awk '{print $NF}' | sort | uniq -c` |

<a name="id42"></a>
### 4.2 Protecció del Servidor Web (Apache)

Per a la protecció del servidor web contra atacs de *web scraping* i escanejos de vulnerabilitats, es recomana configurar filtres per a Apache.

Es poden crear filtres específics que detectin patrons d'atac i bloquegin aquestes IP automàticament tot i que encara no es troben implementats en el procés automàtic d'instal·lació de l'aplicatiu.

➡️ Consulteu recursos avançats, si n'esteu interessats, com la pàgina [https://www.andresmorenostudio.com/blog/fail2ban-apache-server](https://www.andresmorenostudio.com/blog/fail2ban-apache-server) per crear filtres de Fail2Ban per a Virtual Hosts concrets o per a errors comuns d'Apache.
