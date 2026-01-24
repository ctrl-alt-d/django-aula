#!/bin/bash
# setup_apache.sh
# Automatitza la configuració d'Apache2, móduls, virtual hosts i certificats.
# CAL EXECUTAR-LO amb privilegis de root (p. ej., sudo bash setup_apache.sh)

clear

# ----------------------------------------------------------------------
# CÀRREGA DE VARIABLES I FUNCIONS COMUNES ALS SCRIPTS D'AUTOMATITZACIÓ
# ----------------------------------------------------------------------
echo -e "\n"
echo -e "Executant script setup_apache.sh."
echo -e "\n"

echo -e "${C_SUBTITULO}--- Carregant variables i funcions comunes per a la instal·lació ---${RESET}"
echo -e "${C_SUBTITULO}--------------------------------------------------------------------${RESET}"
echo -e "\n"

echo -e "Llegint functions.sh i config_vars.sh."
echo -e "\n"

# 1. Càrrega de la llibreria de funcions
source "./functions.sh"

# 2. Càrrega de variables de configuració
CONFIG_FILE="./config_vars.sh"

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo -e "${C_EXITO}☑️ Variables de configuració carregades.${RESET}"
else
    echo -e "${C_ERROR}❌ ERROR: Arxiu de variables de configuració ($CONFIG_FILE) no trobat. Sortint.${RESET}"
    exit 1
fi


echo -e "\n\n"
echo -e "${C_PRINCIPAL}================================================================"
echo -e "${C_PRINCIPAL}--- FASE 2: SERVIDOR WEB I CERTIFICATS SSL${RESET} ${CIANO}(setup_apache.sh)${RESET} ${C_PRINCIPAL}---"
echo -e "${C_PRINCIPAL}================================================================${RESET}"


if [ "$(id -u)" -ne 0 ]; then
    echo -e "\n"
    echo -e "${C_ERROR}❌ ADVERTÈNCIA: Aquest script ha d'executar-se amb ${RESET} ${C_INFO}'sudo bash setup_apache.sh'${RESET} ${C_ERROR}a tal fi de poder modificar les tasques programdes en *crontab*.${RESET}"
    sleep 3
fi


# ----------------------------------------------------------------------
# 1. INSTAL·LACIÓ I CONFIGURACIÓ DE SEGURETAT
# ----------------------------------------------------------------------

echo -e "\n"
echo -e "${C_CAPITULO}==============================================================="
echo -e "${C_CAPITULO}--- 1. INSTAL·LACIÓ DE SERVIDOR I CONFIGURACIÓ DE SEGURETAT ---"
echo -e "${C_CAPITULO}===============================================================${RESET}"
echo -e "\n"

# 1.1 Instal·lació de Servidor Apache, WSGI, UFW i Certbot

echo -e "${C_SUBTITULO}--- 1.1 Instal·lació de Servidor Apache, WSGI, UFW y Certbot ---${RESET}"
echo -e "${C_SUBTITULO}----------------------------------------------------------------${RESET}"

echo -e "${C_INFO}ℹ️ Actualitzant la llista de paquets (apt-get update)...${RESET}"
apt-get update > /dev/null

echo
echo -e "${C_INFO}ℹ️ Instala·lant dependències: Apache, WSGI, UFW, Certbot...${RESET}"
echo -e "\n"

APT_DESC="Servidor Apache i mod-wsgi"
echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
apt-get install -y apache2 libapache2-mod-wsgi-py3
check_install "$APT_DESC"

APT_DESC="Tallafocs UFW"
echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
apt-get install -y ufw
check_install "$APT_DESC"

APT_DESC="Certbot i la seva integració amb el servidor Apache"
echo -e "${C_INFO}ℹ️ $APT_DESC${RESET}"
apt-get install -y certbot python3-certbot-apache
check_install "$APT_DESC"

echo -e "\n"
echo -e "${C_EXITO}✅ El servidor Apache i els seus complements s'han instal·lat correctament.${RESET}"
echo -e "\n"
sleep 3


# 1.2 Configuració del Firewall UFW

echo -e "${C_SUBTITULO}--- 1.2 Configurant Firewall (UFW) ---${RESET}"
echo -e "${C_SUBTITULO}--------------------------------------${RESET}"

# --- 1. Permetre OpenSSH (per garantir l'accés per SSH) ---
echo -e "Permetent tràfic OpenSSH..."
ufw allow OpenSSH > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${C_EXITO}✅ Permetre OpenSSH. ${RESET}"
else
    echo -e "${C_ERROR}❌ ERROR: No s'ha pogut afegir la regla OpenSSH. Revisi la configuració d'UFW.${RESET}"
    exit 1
fi

# --- 2. Permetre trànsit web (Apache Full: 80 i 443) ---
echo -e "Permetent trànsit web (Apache Full)..."
ufw allow "Apache Full" > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${C_EXITO}✅ Permetre trànsit web (Apache Full: ports 80 i 443).${RESET}"
else
    echo -e "${C_ERROR}❌ ERROR: No s'ha pogut afegir la regla 'Apache Full'. Revisi la configuració d'UFW.${RESET}"
    exit 1
fi

echo -e "\n"

# Habilitar el firewall
ufw --force enable

ufw status

if sudo ufw status | grep -q 'Status: active'; then
    # El codi de sortida és 0 només si 'Status: active' es troba
    echo -e "\n"
    echo -e "${C_EXITO}✅ Firewall UFW habilitat CORRECTAMENT.${RESET}"
    echo -e "${C_EXITO}   Permetent tràfic SSH i Apache Full (80/443).${RESET}"
else
    # Si la comprovació falla, significa que ufw no està actiu o no està instal·lat
    echo -e "\n"
    echo -e "${C_ERROR}❌ ERROR: No s'ha pogut verificar l'estat 'active' del tallafocs UFW.${RESET}"
    echo -e "${C_INFO}ℹ️ Si us plau, revisi si el paquet UFW s'ha instal·lat correctament o si l'ordre 'ufw enable' ha fallat.${RESET}"
    exit 1
fi

sleep 3


# ----------------------------------------------------------------------
# 2. HABILITACIÓ DE MÒDULS I GENERACIÓ DE CERTIFICAT (INTERACTIU)
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}====================================================================="
echo -e "${C_CAPITULO}--- 2. CONFIGURACIÓ DE MÒDULS I GENERACIÓ DE CERTIFICAT (SSL/TLS) ---"
echo -e "${C_CAPITULO}=====================================================================${RESET}"
echo -e "\n"

echo -e "${C_SUBTITULO}--- 2.1 Habilitació de mòduls d'Apache ---${RESET}"
echo -e "${C_SUBTITULO}------------------------------------------${RESET}"

a2enmod wsgi ssl headers rewrite > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR: Fallada en ahbilitar mòduls d'Apache (wsgi, ssl, headers, rewrite).${RESET}"
	echo -e "\n"
    exit 1
fi
echo -e "${C_EXITO}✅ Mòduls habilitats: wsgi, ssl, headers, rewrite.${RESET}"
echo -e "\n"
sleep 3

# ----------------------------------------------------------------------
# 2.2 NETEJA DE VARIABLES I DEFINICIÓ DE PARÀMETRES DE CERTIFICAT
# ----------------------------------------------------------------------

echo -e "${C_SUBTITULO}--- 2.2 Sol·licitud i validació de paràmetres ---${RESET}"
echo -e "${C_SUBTITULO}-------------------------------------------------${RESET}"

VENV_PATH="$FULL_PATH/venv"
WSGI_PATH="$FULL_PATH/aula/wsgi.py"

# 1. Eliminar accents i caracters especials.
# 2. Reemplaçar espais per guions baixos.
# 3. Eliminar qualsevol caràcter que no sigui alfanumèric o guió baix, per seguretat.
LOCALITAT_CLEAN=$(echo "$LOCALITAT" | iconv -t ascii//TRANSLIT | tr ' ' '_')
LOCALITAT_CLEAN=$(echo "$LOCALITAT_CLEAN" | sed 's/[^a-zA-Z0-9_]//g')

read_prompt "Introdueixi el correu de l'administrador (per defecte: juan@xtec.cat): " SERVER_ADMIN "juan@xtec.cat"

echo -e "${C_EXITO}✅ Parámetres de seguretat definits.${RESET}"
echo -e "\n"
sleep 3

# ------------------------------------------------------------------------------
# 2.3 ASSEGURANT LA CONFIGURACIÓ DE L'ARXIU APACHE2.CONF PER PREVENCIÓ D'ERRADES
# ------------------------------------------------------------------------------

echo -e "${C_SUBTITULO}--- 2.3 Assegurant la correcta configuració de l'arxiu apache2.conf per tal de prevenir errades amb Certbot (ServerName global) ---${RESET}"
echo -e "${C_SUBTITULO}-----------------------------------------------------------------------------------------------------------------------------------${RESET}"

# S'afegeix la directiva ServerName a l'arxiu de configuració principal d'Apache.
APACHE_CONF="/etc/apache2/apache2.conf"

# 1. NETEJA PREVENTIVA
# Elimina qualsevol línia incompleta 'ServerName ' que haguès pogut fallar abans,
# eliminant l'errada de sintaxis del "ServerName" sense arguments.
sudo sed -i '/^ServerName *$/d' "$APACHE_CONF"

# 2. VERIFICACIÓ I ADICIÓ IDEMPOTENT
# Verifica si la directiva ServerName ja existeix amb l'argument correcte.
if ! grep -q "^ServerName $DOMAIN_CLEAN" "$APACHE_CONF"; then

    # S'hi afegeix només si NO existeix.
    echo "ServerName $DOMAIN_CLEAN" | sudo tee -a "$APACHE_CONF" > /dev/null

    echo -e "${C_EXITO}✅ Directiva 'ServerName $DOMAIN_CLEAN' afegida a $APACHE_CONF.${RESET}"
else
    echo -e "${C_INFO}ℹ️ La directiva 'ServerName $DOMAIN_CLEAN' ya existeix en $APACHE_CONF. No s'ha dut a terme cap canvi.${RESET}"
fi
echo -e "\n"
sleep 3


# ----------------------------------------------------------------------
# 2.4 ELECCIÓ I GENERACIÓ DE CERTIFICATS
# ----------------------------------------------------------------------

echo -e "${C_SUBTITULO}--- 2.4 Generació i elecció de certificats SSL/TLS ---${RESET}"
echo -e "${C_SUBTITULO}------------------------------------------------------${RESET}"

# Variables de ruta de certificats
CERT_KEY="/etc/ssl/private/$PROJECT_FOLDER-selfsigned.key"
CERT_CRT="/etc/ssl/certs/$PROJECT_FOLDER-selfsigned.crt"

if [[ "$INSTALL_TYPE_LOWER" == "pub" ]]; then

    echo -e "${C_INFO}-> Generant certificat Self-Signed TEMPORAL per a $DOMAIN_CLEAN${RESET}"
	openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
		-keyout "$CERT_KEY" \
		-out "$CERT_CRT" \
		-subj "/C=ES/ST=Catalonia/L=$LOCALITAT_CLEAN/O=$PROJECT_FOLDER/CN=$DOMAIN_CLEAN" > /dev/null 2>&1

	# Verificar la generació (comprovació CRÍTICA)
	if [ $? -ne 0 ] || [ ! -s "$CERT_CRT" ]; then
           echo -e "${C_ERROR}❌ ERROR CRÍTIC: Fallada en generar el certificat SSL temporal...${RESET}"
           echo -e "\n"
           exit 1
        fi
    echo -e "${C_EXITO}✅ Certificat Self-Signed TEMPORAL generat i llest com a marcador de posició.${RESET}"
    sleep 3

    # ----------------------------------------------------------------------
    # Misssatge informatiu sobre l'elecció del certificat
    # ----------------------------------------------------------------------

    echo -e "\n"
    echo -e "${C_INFO}--- Tipus de Certificats SSL/TLS ---${RESET}"
    echo -e "L'aplicació necessita un certificat per habilitar la connexió segura (HTTPS/SSL) del navegador; en cas contrari, mostrarà un error de confiança."
    echo -e "\n"
    echo -e "${C_SUBTITULO}1. Certificat Auto-signat (Self-Signed):${RESET}"
    echo -e "    - Són generats localment i són ideals per a ${NEGRITA}entorns de desenvolupament (test) o xarxes internes a les quals no s'accedirà des de l'exterior.${RESET}"
    echo -e "    - ${C_ERROR}Advertència:${RESET} Els navegadors web mostraran una ${NEGRITA}alerta de seguretat${RESET} en no ser emesos per una Autoritat de Certificació (CA) reconeguda.${RESET}"
    echo -e "\n"
    echo -e "${C_SUBTITULO}2. Certificat Vàlid (Let's Encrypt):${RESET}"
    echo -e "    - Són certificats ${NEGRITA}reconeguts, vàlids i gratuïts${RESET}, adequats per a ${NEGRITA}entorns de producció.${RESET}"
    echo -e "    - ${C_EXITO}Requisit:${RESET} Només es poden obtenir si el servidor té un ${NEGRITA}nom de domini o subdomini real${RESET} que apunta a la seva IP pública.${RESET}"
    echo -e "\n"

    echo -e "${C_INFO}⚠️ PRE-REQUISIT: Per a Let's Encrypt, el domini '$DOMAIN_CLEAN' (i www.) ha d'apuntar a la IP pública del servidor.${RESET}"
    read_prompt "¿Vol instal·lar un certificat Let's Encrypt (LE) o un certificat Auto-signat (per defecte AUTO)? (le/AUTO): " CERT_TYPE "AUTO"
    CERT_TYPE_LOWER=$(echo "$CERT_TYPE" | tr '[:upper:]' '[:lower:]')

    if [[ "$CERT_TYPE_LOWER" == "le" ]] || [[ "$CERT_TYPE_LOWER" == "letsencrypt" ]]; then

        # LÒGICA CERTBOT (Let's Encrypt)
        echo -e "${C_INFO}ℹ️ Ha seleccionat Let's Encrypt. L'execució interactiva es realitzarà després de crear el fitxer de configuració VHost del servidor web.${RESET}"
        echo -e "${C_INFO}    El certificat auto-signat TEMPORAL serà reemplaçat pel de Let's Encrypt.${RESET}"
    else
        # LÒGICA CERTIFICAT AUTO-SIGNAT (Self-Signed)
        echo -e "${C_INFO}-> Convertint el certificat Self-Signed creat temporalment en permanent per a $DOMAIN_CLEAN${RESET}"
        echo -e "${C_INFO}⚠️ Advertència: Els navegadors web mostraran un missatge de no confiança...${RESET}"
        sleep 3
    fi
else
    # Entorn INTERN: NO es genera cap certificat.
    echo -e "${C_INFO}ℹ️ Entorn INTERN seleccionat. S'omet la generació de certificats SSL.${RESET}"
    CERT_TYPE_LOWER="int"
    sleep 3
fi


# ----------------------------------------------------------------------
# 3. CREACIÓ D'ARXIUS VIRTUAL HOST
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}========================================================"
echo -e "${C_CAPITULO}--- 3. CREACIÓ D'ARXIUS DE CONFIGURACIÓ VIRTUAL HOST ---"
echo -e "${C_CAPITULO}========================================================${RESET}"
echo -e "\n"

VHOST_DIR="/etc/apache2/sites-available"			# Nom del directori on es trobaran els VHost
HTTP_REDIRECT_CONF="$VHOST_DIR/$PROJECT_FOLDER.conf"		# Nom del VHost http extern que redirigirà a https
SSL_CONF="$VHOST_DIR/$PROJECT_FOLDER-ssl.conf"			# Nom del VHost https extern
HTTP_INTERNAL_CONF="$VHOST_DIR/$PROJECT_FOLDER-int.conf"	# Nom del VHost http intern

if [[ "$INSTALL_TYPE_LOWER" == "pub" ]]; then

    echo -e "${C_INFO}-> Configurando Vhosts para entorno PÚBLICO (HTTP a HTTPS)${RESET}"
    echo -e "\n"

    # 3.1 Creant arxiu per accés per HTTP (Redirecció)
    echo -e "${C_SUBTITULO}--- 3.1 Creant arxiu per accés per HTTP extern (Redirecció) ---${RESET}"
    echo -e "${C_SUBTITULO}---------------------------------------------------------------${RESET}"

    cat << EOF | sudo tee "$HTTP_REDIRECT_CONF" > /dev/null
<VirtualHost *:80>
	ServerAdmin $SERVER_ADMIN
	ServerName $DOMAIN_CLEAN
	ServerAlias www.$DOMAIN_CLEAN 127.0.0.1 localhost
	RedirectMatch permanent ^(.*)$ https://$DOMAIN_CLEAN$1
</VirtualHost>
EOF

    echo -e "${C_EXITO}✅ Arxiu HTTP ($HTTP_REDIRECT_CONF) per accés extern creat (Redirecció).${RESET}"
    echo -e "\n"
    sleep 1

   # 3.2 Creant arxiu per accés segur HTTPS (SSL)
   echo -e "${C_SUBTITULO}--- 3.2 Creant arxiu per accés segur HTTPS (SSL) ---${RESET}"
   echo -e "${C_SUBTITULO}----------------------------------------------------${RESET}"

   cat << EOF | sudo tee "$SSL_CONF" > /dev/null
<VirtualHost *:443>
	ServerAdmin $SERVER_ADMIN
	ServerName $DOMAIN_CLEAN
	ServerAlias www.$DOMAIN_CLEAN 127.0.0.1 localhost

	# Configuració WSGI
	WSGIDaemonProcess $PROJECT_FOLDER python-home=$VENV_PATH python-path=$FULL_PATH \\
		locale="ca_ES.utf8"
	WSGIProcessGroup $PROJECT_FOLDER
	WSGIApplicationGroup %{GLOBAL}
	WSGIScriptAlias / $WSGI_PATH 

	# Àlies per a contingut estatic (collectstatic)
	Alias /site-css/admin $FULL_PATH/aula/static/admin/
	Alias /site-css $FULL_PATH/aula/static/

	# Accés a directoris
	<Directory $FULL_PATH/aula>
		<Files wsgi.py>
			Require all granted
		</Files>
	</Directory>
	<Directory $FULL_PATH/aula/static/>
		Require all granted
	</Directory>
	<Directory $FULL_PATH/aula/static/admin/>
		Require all granted
	</Directory>

	ErrorLog /var/log/apache2/$PROJECT_FOLDER-ssl-error.log
	CustomLog /var/log/apache2/$PROJECT_FOLDER-ssl-access.log combined

	# Configuració SSL (Self-Signed per defecte. Certbot ho reemplaçarà si es selecciona Let's Encrypt (LE)
	SSLEngine on
	SSLCertificateFile $CERT_CRT
	SSLCertificateKeyFile $CERT_KEY
	LogLevel warn

	# Altres configuracions...
	BrowserMatch ".*MSIE.*" \
		nokeepalive ssl-unclean-shutdown \
		downgrade-1.0 force-response-1.0

</VirtualHost>
EOF

    echo -e "${C_EXITO}✅ Arxiu SSL ($SSL_CONF) creat.${RESET}"
    sleep 3

else # INSTAL·LACIÓ INTERNA (int)

    echo -e "${C_INFO}-> Configurant Vhost per a entorn INTERN (només HTTP)${RESET}"
    cat << EOF | sudo tee "$HTTP_INTERNAL_CONF" > /dev/null
<VirtualHost *:80>
	ServerAdmin $SERVER_ADMIN
	ServerName $DOMAIN_CLEAN
	ServerAlias www.$DOMAIN_CLEAN 127.0.0.1 localhost

	# Configuració WSGI
	WSGIDaemonProcess $PROJECT_FOLDER python-home=$VENV_PATH python-path=$FULL_PATH \\
		locale="ca_ES.utf8"
	WSGIProcessGroup $PROJECT_FOLDER
	WSGIApplicationGroup %{GLOBAL}
	WSGIScriptAlias / $WSGI_PATH

	# Àlies per a contingut estàtic (collectstatic)
	Alias /site-css/admin $FULL_PATH/aula/static/admin/
	Alias /site-css $FULL_PATH/aula/static/

	# Accés a directoris
	<Directory $FULL_PATH/aula>
		<Files wsgi.py>
			Require all granted
		</Files>
	</Directory>
	<Directory $FULL_PATH/aula/static/>
		Require all granted
	</Directory>
	<Directory $FULL_PATH/aula/static/admin/>
		Require all granted
	</Directory>

	ErrorLog /var/log/apache2/$PROJECT_FOLDER-http-error.log
	CustomLog /var/log/apache2/$PROJECT_FOLDER-http-access.log combined
	LogLevel warn

	# Altres configuracions...
	BrowserMatch ".*MSIE.*" \
		nokeepalive \
		downgrade-1.0 force-response-1.0

</VirtualHost>
EOF

    echo -e "${C_EXITO}✅ Arxiu HTTP INTERN ($HTTP_INTERNAL_CONF) creat (WSGI port 80).${RESET}"

fi

echo -e "\n\n"
echo -e "${C_CAPITULO}==============================================="
echo -e "${C_CAPITULO}--- 4. AJUST DE PERMISOS DE www-data (WSGI) ---"
echo -e "${C_CAPITULO}===============================================${RESET}"
echo -e "\n"

# 1. Permisos del DIRECTORI DE DADES PRIVADES (Cal Lectura/Escriptura)
#    S'assigna el grup 'www-data' amb permisos de lectura/escriptura (770) al grup.
chown -R "$APP_USER":www-data "$PATH_DADES_PRIVADES"
chmod 770 "$PATH_DADES_PRIVADES"
echo -e "${C_EXITO}✅ Permisos per a dades privades assignats a '$APP_USER':www-data (chmod 770).${RESET}"

# 2. Assignar el grup www-data al projecte
chown -R "$APP_USER":www-data "$FULL_PATH"
echo -e "${C_EXITO}✅️ Grup 'www-data' assignat al directori del projecte.${RESET}"
echo -e "\n\n"

echo -e "${C_EXITO}✅ Ajustament de permisos completats.${RESET}"
sleep 5


# ----------------------------------------------------------------------
# 5. HABILITACIÓ DE VIRTUAL HOSTS I CERTBOT
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}===================================================="
echo -e "${C_CAPITULO}--- 5. HABILITACIÓ DE LLOCS, CERTBOT I RECÀRREGA ---"
echo -e "${C_CAPITULO}====================================================${RESET}"
echo -e "\n"

# 5.1 Deshabilitant Virtual Hosts per defecte d'Apache
echo -e "${C_SUBTITULO}--- 5.1 Deshabilitant Virtual Hosts per defecte ---${RESET}"
echo -e "${C_SUBTITULO}---------------------------------------------------${RESET}"

# Deshabilitar el Vhost per defecte
a2dissite 000-default.conf > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${C_EXITO}✅ Vhost per defecte deshabilitat.${RESET}"
else
    # ATENCIÓ: Si 'a2dissite' ja estava deshabilitat, pot retornar 0.
    # No obstant això, si falla per altres motius (permisos, etc.), cal avisar.
    # En aquest cas, un error lleu és acceptable si ja estava fet.
    # Comprovem si el fitxer ja no existeix al directori 'sites-enabled'
    if [ ! -L "/etc/apache2/sites-enabled/000-default.conf" ]; then
        echo -e "${C_EXITO}✅ Vhost per defecte ja estava deshabilitat (o no existia).${RESET}"
    else
        echo -e "${C_ERROR}❌ ERROR: No s'ha pogut deshabilitar el Vhost per defecte (000-default.conf).${RESET}"
        echo -e "${C_INFO}ℹ️ Si us plau, revisi els permisos o si el fitxer existeix.${RESET}"
        exit 1
    fi
fi
echo -e "\n"
sleep 1

# 5.2 Habilitant els nous  Virtual Hosts
echo -e "${C_SUBTITULO}--- 5.2 Habilitant els nous Virtual Hosts ---${RESET}"
echo -e "${C_SUBTITULO}---------------------------------------------${RESET}"

if [[ "$INSTALL_TYPE_LOWER" == "pub" ]]; then
    # Habilitar VHosts HTTP i SSL
    a2ensite "$PROJECT_FOLDER.conf" > /dev/null
    echo -e "${C_EXITO}✅ Vhost HTTP (80) habilitat i llest per fer redireccionar.${RESET}"

    a2ensite "$PROJECT_FOLDER-ssl.conf" > /dev/null
    echo -e "${C_EXITO}✅ Vhost HTTPS (443) habilitat. Servidor web preparat.${RESET}"

    echo -e "\n"
    echo -e "${C_EXITO}✅ Vhosts ($PROJECT_FOLDER y $PROJECT_FOLDER-ssl) habilitats.${RESET}"

else
    # Habilitar només el VHost HTTP intern
    a2ensite "$PROJECT_FOLDER-int.conf" > /dev/null
    echo -e "${C_EXITO}✅ Vhost HTTP INTERN ($PROJECT_FOLDER-int.conf) habilitat en el port 80.${RESET}"
fi

echo -e "\n"
sleep 1


# 5.3 INSTAL·LACIÓ OPCIONAL: VIRTUAL-HOST PER CATCH-ALL
echo -e "${C_SUBTITULO}--- 5.3 Configuració de Seguretat Addicional (Catch-all) ---${RESET}"
echo -e "${C_SUBTITULO}------------------------------------------------------------${RESET}"

echo
echo -e "${C_INFO}ℹ️ Si un servidor està exposat a internet sempre rebrà intents d'accedir al servidor que acaben arribant a Django-aula. L'aplicatiu els rebutja si no es troben dins [ALLOWED_HOSTS], però es genera un correu de notificació a l'administrador per cada intent de connexió rebutjat.${RESET}"
echo
read_prompt "¿Desitja instal·lar el Virtual Host 'Catch-all' (zzz-catchall.conf) que bloquejarà aquestes peticions no reconegudes per a que no arribin a Django-Aula? (Recomanat en Producció) [s/N]: " CATCHALL_CHOICE "n"

CATCHALL_CHOICE_LOWER=$(echo "$CATCHALL_CHOICE" | tr '[:upper:]' '[:lower:]')

if [[ "$CATCHALL_CHOICE_LOWER" == "s" || "$CATCHALL_CHOICE_LOWER" == "si" ]]; then
    # Habilita el mòdul rewrite si l'usuari vol el catch-all, per si de cas
    a2enmod rewrite > /dev/null 2>&1

    echo -e "\n"
    echo "⚙️ Instal·lant Virtual Host 'Catch-all' (zzz-catchall.conf) per bloquejar tràfnsit no desitjat (flood control)."

    # 1. Crear el directori per al DocumentRoot buit (requisit de l'Apache)
    sudo mkdir -p /var/www/catchall

    # 2. Crear el fitxer de configuració zzz-catchall.conf
    # NOTA: Utilitzem ServerName _ i ServerAlias * per atrapar tot el trànsit no reclamat
    sudo tee /etc/apache2/sites-available/zzz-catchall.conf > /dev/null <<EOT
# --- CATCH-ALL PER TRÀNSIT NO RECONEGUT (zzz-catchall.conf) ---
# Aquest host es carrega a la fi (zzz) per capturar el tràfic que cap altre VirtualHost ha reclamat.
# Això evita que els bots consumeixin recursos de l'aplicació Django i enviïn correus d'error.

## 1. TRAFIC HTTP (80)
<VirtualHost *:80>
    ServerName _
    ServerAlias *
    DocumentRoot /var/www/catchall

    # Bloquejar peticions no reconegudes amb un error 400 (Bad Request)
    ErrorDocument 400 "Host no reconegut"
    RewriteEngine On
    RewriteRule ^ - [R=400,L]
</VirtualHost>

## 2. TRAFIC HTTPS (443)
<VirtualHost *:443>
    ServerName _
    ServerAlias *
    DocumentRoot /var/www/catchall

    SSLEngine on
    # Configuració SSL dummy (Apache necessita un certificat per iniciar 443)
    SSLCertificateFile /etc/ssl/certs/ssl-cert-snakeoil.pem
    SSLCertificateKeyFile /etc/ssl/private/ssl-cert-snakeoil.key

    # TANCAMENT IMMEDIAT (403 Forbidden)
    RewriteEngine On
    # Regla: Per qualsevol petició, retorna 403 (tancar connexió).
    RewriteRule ^ - [R=403,L]
    ErrorDocument 403 /catchall-403

    <Directory /var/www/catchall>
        Require all denied
    </Directory>
</VirtualHost>
EOT

    # 3. Habilitar el nou Virtual Host
    sudo a2ensite zzz-catchall.conf > /dev/null 2>&1

    if [ $? -eq 0 ]; then
        echo -e "${C_EXITO}✅ Fitxer zzz-catchall.conf instal·lat i habilitat.${RESET}"
        echo "⚠️ Aquest Virtual Host només actua sobre peticions que NO coincideixen amb $PROJECT_FOLDER.conf."
    else
        echo -e "${C_ERROR}❌ ERROR: No s'ha pogut habilitar el Vhost zzz-catchall.conf.${RESET}"
        echo -e "${C_INFO}ℹ️ Si us plau, revisi la sintaxi del fitxer de configuració acabat de crear o els permisos.${RESET}"
        exit 1
    fi
    sleep 2
else
    echo "⏭️ Instal·lació de Catch-all no sol·licitada. Saltant."
fi

echo -e "\n"
sleep 1


# 5.4 Comprovació de la sintaxi dels Virtual Hosts per al servidor Apache
echo -e "${C_SUBTITULO}--- 5.4 Comprovació de la sintaxi dels Virtual Hosts per al servidor Apache ---${RESET}"
echo -e "${C_SUBTITULO}-------------------------------------------------------------------------------${RESET}"

echo -e "${C_INFO}ℹ️ Verificant la sintaxi dels arxius de configuració d'Apache (apache2ctl configtest)${RESET}"
echo -e "\n"

apache2ctl configtest

if [ $? -ne 0 ]; then
	echo -e "${C_ERROR}❌ ERROR CRÍTIC: Fallada en la prova de configuració d'Apache. Revisi els arxius de configuració creats. La instal·lació s'atura.${RESET}"
    exit 1
fi

echo -e "\n"

# 5.5 Informació del certificat autosignat o instal·lació del certificat amb Let's Encrypt

# Si el certificat triat és autosignat
if [[ "$CERT_TYPE_LOWER" == "auto" ]]; then

    echo -e "${C_SUBTITULO}--- 5.5 Certificat SSL Auto-signat generat i instal·lat ---${RESET}"
    echo -e "${C_SUBTITULO}-----------------------------------------------------------${RESET}"
    echo
    echo -e "${C_EXITO}✅ Certificat SSL Auto-signat generat i instal·lat al Vhost temporal.${RESET}"
    echo -e "${C_INFO}ℹ️ La connexió HTTPS funcionarà, però el navegador mostrarà una advertència de seguretat.${RESET}"


# Si el certificat triat és amb la CA Let's Encrypt.
elif [[ "$CERT_TYPE_LOWER" == "le" ]]; then

    echo -e "${C_SUBTITULO}--- 5.5 Executant Certbot per generar i instal·lar els certificats de Let's Encrypt ---${RESET}"
    echo -e "${C_SUBTITULO}---------------------------------------------------------------------------------------${RESET}"

    echo -e "${C_INFO}ℹ️ Certbot executarà una eina de comprovació interactiva i li farà preguntes sobre la configuració.${RESET}"
    echo -e "\n"

    echo -e "${C_INFO}Hi ha paràmetres importants a definir com ara:${RESET}"
    echo -e "${NEGRITA}    - Introduir un correu vàlid.${RESET}"
    echo -e "${NEGRITA}    - Seleccionar 'Enter' per habilitar HTTPS en ambdós dominis (amb i sense www).${RESET}"
    echo -e "${NEGRITA}    - Seleccionar '2' quan li pregunti si vol no redirigir (opció 1) o redirigir (opció 2) el trànsit generat quan s'ha accedit per HTTP (no segur).${RESET}"
    echo -e "\n"

# Executar Certbot de forma interactiva
    certbot --apache --redirect

    echo -e "\n"
    if [ $? -ne 0 ]; then
        echo -e "${C_ERROR}❌ ERROR: Fallada en l'obtenció del certificat Let's Encrypt. La instal·lació continuarà amb el certificat Self-Signed temporal.${RESET}"
    else
        echo -e "${C_EXITO}✅ Certificats Let's Encrypt obtinguts i instal·lats amb èxit. Apache2 modificat.${RESET}"
        echo -e "${C_INFO}ℹ️ La renovació automàtica està configurada per Certbot (certbot.timer).${RESET}"

        # ----------------------------------------------
        # VERIFICACIÓ I PROVA DE RENOVACIÓ DE CERTBOT
        # ----------------------------------------------

        echo -e "\n"
        echo -e "${C_SUBTITULO}--- Verificació de la renovació de certificats ---${RESET}"
        echo -e "${C_SUBTITULO}--------------------------------------------------${RESET}"

        read_prompt "¿Vol verificar l'estat del servei de renovació automàtica (certbot.timer)? per defecte NO. (sí/NO): " CHECK_TIMER "no"

        RESPONSE_LOWER=$(echo "$CHECK_TIMER" | tr '[:upper:]' '[:lower:]')

        if [[ "$RESPONSE_LOWER" == "sí" ]] || [[ "$RESPONSE_LOWER" == "si" ]]; then

            if [ "$IS_SYSTEMD" -eq 1 ]; then
                # Mètode systemd
                systemctl status certbot.timer
            else
                # Mètode SysVinit, amb cron
                echo "ℹ️ Comprovant la configuració de renovació (Cron Job)..."
                if [ -f /etc/cron.d/certbot ]; then
                    echo "✅ Fitxer /etc/cron.d/certbot trobat. La renovació està programada per Cron."
                else
                    echo "❌ No s'ha trobat la programació automàtica de renovació. S'ha de verificar manualment."
                    echo -e "${C_ERROR}❌ Es recomana verificar que certbot està actiu fent la simulació de renovació de certificats.${RESET}"
                fi
            fi
        fi
        echo -e "\n"

        read_prompt "¿Vol executar una simulació de renovació de certificats (dry-run)? Això no modificarà el sistema, només és una simulació. Per defecte NO (sí/NO): " DRY_RUN_TEST "no"

        RESPONSE_LOWER=$(echo "$DRY_RUN_TEST" | tr '[:upper:]' '[:lower:]')

        if [[ "$RESPONSE_LOWER" == "sí" ]] || [[ "$RESPONSE_LOWER" == "si" ]]; then
            echo -e "${C_INFO}-> Executant: sudo certbot renew --dry-run${RESET}"
            echo -e "\n"
            certbot renew --dry-run

            echo -e "\n"
            if [ $? -eq 0 ]; then
                echo -e "${C_EXITO}✅ Simulació de renovació completada amb èxit. El procés de renovació automàtic de certificats abans que caduquin funcionarà.${RESET}"
            else
                echo -e "${C_ERROR}❌ ADVERTÈNCIA: La simulació de renovació va fallar. Revisi els logs de Certbot per determinar la causa.${RESET}"
            fi
         fi
    fi
fi

echo -e "\n"

# 5.6 Recarregant la configuració del servidor Apache per aplicar els canvis

echo -e "${C_SUBTITULO}--- 5.6 Recarregant la configuració del servidor Apache per aplicar els canvis ---${RESET}"
echo -e "${C_SUBTITULO}----------------------------------------------------------------------------------${RESET}"

SERVICE_NAME="apache2"

if [ "$IS_SYSTEMD" -eq 1 ]; then
    #Mètode systemd
	systemctl reload "$SERVICE_NAME"
else
	#Mètode SysVinit/Procés
	service "$SERVICE_NAME" reload
fi

echo

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR: Fallada al recarregar Apache2. Revisa els logs i la sintaxi dels Vhosts.${RESET}"
	echo -e "\n"
    exit 1
else
	# Mostrar l'estat del servei per confirmació
	echo -e "Estat del servei Apache2:\n"

        if [ "$IS_SYSTEMD" -eq 1 ]; then
            #Mètode systemd
            systemctl status "$SERVICE_NAME" | grep Loaded
            systemctl status "$SERVICE_NAME" | grep Active
	    echo -e "\n"
	    echo -e "${C_EXITO}✅ Recàrrega d'Apache2 completada sense errades.${RESET}"
        else
            #Mètode SysVinit/Procés
	    service "$SERVICE_NAME" status
	    echo
            if ps aux | grep -v grep | grep -q "$SERVICE_NAME"; then
            	echo -e "${C_EXITO}✅ El servei $SERVICE_NAME està Actiu (Running).${RESET}"
            else
                echo -e "${C_ERROR}❌ El servei $SERVICE_NAME no està Actiu (Aturat). Caldrà comprovar manualment on és el problema.${RESET}"
            fi
        fi
fi
sleep 2

echo -e "\n"
echo -e "${C_INFO}--- Afegint variables a l'arxiu${RESET} ${CIANO}config_vars.sh${RESET} ${C_INFO}automàticament ---${RESET}\n"
echo "export CERT_TYPE_LOWER='$CERT_TYPE_LOWER'" >> "$SETUP_DIR/config_vars.sh"               # Pel missatge final informatiu (setup_cron.sh)

sleep 2

echo -e "\n\n"
echo -e "${C_PRINCIPAL}====================================================================="
echo -e "${C_PRINCIPAL}--- FASE 2. CONFIGURACIÓ D'APACHE FINALITZADA${RESET} ${CIANO}(setup_apache.sh)${RESET} ${C_PRINCIPAL}---"
echo -e "${C_PRINCIPAL}=====================================================================${RESET}"

echo -e "\n\n"
echo -e "${C_CAPITULO}========================================"
echo -e "${C_CAPITULO}--- INFORMACIÓ D'ACCÉS A L'APLICATIU ---"
echo -e "${C_CAPITULO}========================================${RESET}"
echo -e "\n"

if [[ "$INSTALL_TYPE_LOWER" == "pub" ]]; then
    echo -e "${C_INFO}ℹ️ L'accés ha d'utilitzar la URL segura (HTTPS).${RESET}"

    if [[ "$CERT_TYPE_LOWER" == "auto" ]]; then
        echo -e "${C_INFO}    Com que s'ha instal·lat un certificat definitiu ${NEGRITA}Autosignat${RESET}, el navegador mostrarà una ADVERTÈNCIA DE SEGURETAT. Haurà de confirmar l'excepció per continuar i accedir a l'aplicatiu.${RESET}"
        echo -e "\n"
        echo -e "${C_SUBTITULO}    URL d'Accés per IP (Recomanat per a Tests/VM):${RESET}"
        echo -e "${NEGRITA}   ➡️ https://127.0.0.1${RESET}"
        echo -e "${NEGRITA}   ➡️ https://localhost${RESET}"
        echo -e "\n"
        echo -e "${C_SUBTITULO}  URL d'Accés per Domini (Utilitza el nom del certificat):${RESET}"
        echo -e "${NEGRITA}   ➡️ https://$DOMAIN_CLEAN${RESET}"
        echo -e "     Aquesta URL només funcionarà si '$DOMAIN_CLEAN' està definit al fitxer /etc/hosts de la VM o resolt amb registre DNS d'un servidor de domini."
    else
        echo -e "${C_INFO}    S'ha instal·lat un certificat ${NEGRITA}Vàlid (Let's Encrypt).${RESET}${C_INFO} L'accés hauria de ser segur.${RESET}"
        echo -e "${NEGRITA}   ➡️ https://$DOMAIN_CLEAN${RESET}"
    fi

else
    echo -e "${C_INFO}S'ha instal·lat en mode ${NEGRITA}INTERN${RESET}${C_INFO} (sense SSL).${RESET}"
    echo -e "${C_SUBTITULO}URL d'Accés: ${RESET}"
    echo -e "${NEGRITA}   ➡️ http://127.0.0.1${RESET}"
    echo -e "${NEGRITA}   ➡️ http://localhost${RESET}"
    echo -e "${NEGRITA}   ➡️ http://$DOMAIN_CLEAN${RESET} Si està definit a /etc/hosts o amb registre DNS d'un servidor de domini."
fi
echo -e "\n"

echo -e "${C_INFO}--- SEGÜENT FASE: FASE 3 - TASQUES PROGRAMADAS ---${RESET}"
echo -e "\n"

echo -e "Per continuar amb l'automatització de les tasques programades (CRON) en el servidor, ${NEGRITA}executi les següents ordres (Copiar/Enganxar)${RESET}:"
echo -e "\n"

echo "   1. Asseguri's que es troba al directori on hi ha els scripts d'instal·lació del projecte:"
echo -e "      \$ ${C_SUBTITULO} cd \"$SETUP_DIR\"${RESET}"
echo -e "\n"

echo "   2. Executi l'script que configurarà les tasques programades (CRON) en el servidor (HA DE SER amb sudo):"
echo -e "      \$ ${C_SUBTITULO} sudo bash setup_cron.sh${RESET}"
echo -e "\n"
