#!/bin/bash
# setup_cron.sh
# Configura les tasques programades (CRON) per a l'aplicació Django-Aula.
# HA D'EXECUTAR-SE amb privilegis de root (sudo bash setup_cron.sh)
# Assumeix que s'executa des del directori del projecte (/opt/djau)

clear

# ----------------------------------------------------------------------
# CÀRREGA DE VARIABLES I FUNCIONS COMUNS ALS SCRIPTS D'AUTOMATITZACIÓ
# ----------------------------------------------------------------------

echo -e "\n"
echo -e "Executant script setup_cron.sh."
echo -e "\n"

# 1. CARREGAR LLIBRERIA DE FUNCIONS
source "./functions.sh"

# 2. CARREGAR VARIABLES DE CONFIGURACIÓ
CONFIG_FILE="./config_vars.sh"

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo -e "${C_EXITO}☑️ Variables de configuracióó carregades.${RESET}"
else
    echo -e "${C_ERROR}❌ ERROR: Fitxer de configuració ($CONFIG_FILE) no trobat. Sortint.${RESET}"
    exit 1
fi

# Definicions de Variables Clau que no existeixen a config_vars.sh
LOG_DIR="$FULL_PATH/log" # Directori per guardar logs

echo -e "\n"
echo -e "${C_PRINCIPAL}==================================================="
echo -e "${C_PRINCIPAL}--- FASE 3: TASQUES PROGRAMADES ${RESET}${CIANO}(setup_cron.sh)${RESET}${C_PRINCIPAL} ---"
echo -e "${C_PRINCIPAL}===================================================${RESET}"

# Comprova si l'usuari actual és root (UID 0)
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${C_ERROR}❌ ADVERTÈNCIA: Aquest script ha d'executar-se amb 'sudo bash setup_cron.sh' per modificar les tasques programades en crontab.${RESET}"
    echo -e "${C_INFO}ℹ️ Si us plau, executi l'script amb permisos de superusuari (root).${RESET}"
    exit 1
fi

# ----------------------------------------------------------------------
# 1. CREACIÓ DE L'SCRIPT DE BACKUP
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}==========================================================================================================="
echo -e "${C_CAPITULO}--- 1. CREACIÓ I CONFIGURACIÓ DE L'SCRIPT QUE FARÀ LES CÒPIES DE SEGURETAT DE LA BASE DE DADES (BACKUP) ---"
echo -e "${C_CAPITULO}===========================================================================================================${RESET}"
echo -e "\n"

NOM_SCRIPT_BACKUP="backup-bd-djau.sh"
BACKUP_SCRIPT="$FULL_PATH/$NOM_SCRIPT_BACKUP"
BACKUP_DIR="$FULL_PATH/djauBK/"


echo -e "${C_SUBTITULO}--- 1.1 Creant el directori de backups ---${RESET}"
echo -e "${C_SUBTITULO}------------------------------------------${RESET}"

mkdir -p "$BACKUP_DIR"
chown "$APP_USER":"$APP_USER" "$BACKUP_DIR"
echo -e "${C_EXITO}✅ Directori per les còpies de seguretat (backup)${RESET} ${C_INFO}$BACKUP_DIR ${C_EXITO}creat.${RESET}"
echo -e "\n"
sleep 3

echo -e "${C_SUBTITULO}--- 1.2 Creant l'arxiu${RESET} ${CIANO}$BACKUP_SCRIPT${RESET} ${C_SUBTITULO}---${RESET}"
echo -e "${C_SUBTITULO}----------------------------------------------------------${RESET}"

cat << EOF > "$BACKUP_SCRIPT"
#!/bin/bash
# Script de backup de PostgreSQL (Necessita permisos NOPASSWD per pg_dump instal·lats amb l'script install_app.sh)

# Variables de entorn
export PGDATABASE="$DB_NAME"
export PGUSER="$DB_USER"

ara=\`/bin/date +\%Y\%m\%d\%H\%M\`
hora=\`/bin/date +\%H\`
dia=\`/bin/date +\%d\`
mes=\`/bin/date +\%Y\%m\`
directori="$BACKUP_DIR"
copia="\${directori}bdd-ara-\${ara}.sql"
extensio=".bz2"

# Assegurar que el directori existeix
mkdir -p "\$directori"

# Dur a terme el dump de la base de dades
# NOTA: pg_dump necessita que l'usuario $APP_USER tingui NOPASSWD per 'pg_dump' que ja es va configurar en l'script install_djau.sh
/usr/bin/pg_dump > "\$copia"

# Comprimir l'arxiu
/bin/bzip2 "\$copia"

# Crear els enllaços (còpies) rotatives
cat "\${copia}\${extensio}" > "\${directori}bdd-hora-\${hora}.sql\${extensio}" 
cat "\${copia}\${extensio}" > "\${directori}bdd-dia-\${dia}.sql\${extensio}" 
cat "\${copia}\${extensio}" > "\${directori}bdd-mes-\${mes}.sql\${extensio}" 

# Eliminar el backup temporal
rm "\$copia\${extensio}"
EOF

# Assignar propietari i permisos d'execució
chown "$APP_USER":"$APP_USER" "$BACKUP_SCRIPT"
chmod +x "$BACKUP_SCRIPT"
echo -e "${C_EXITO}✅ Script de backup creat${RESET} ${C_INFO}$BACKUP_SCRIPT${RESET} ${C_EXITO}i permisos assignats a${RESET} ${C_INFO}$APP_USER.${RESET}"
sleep 3

# ----------------------------------------------------------------------
# 2. GENERACIÓ DE TASQUES CRON
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}================================================="
echo -e "${C_CAPITULO}--- 2. GENERACIÓ DE TASQUES PROGRMADES (CRON) ---"
echo -e "${C_CAPITULO}=================================================${RESET}"
echo -e "\n"

echo -e "${C_SUBTITULO}--- 2.1 Directori de logs${RESET} ${CIANO}$LOG_DIR${RESET} ${C_SUBTITULO}creat ---${RESET}"
echo -e "${C_SUBTITULO}---------------------------------------------------${RESET}"

# Crear el directori de logs, si no existeix, i fer que tingui permisos a www-data i l'usuari instal·lador
mkdir -p "$LOG_DIR"
chown "$APP_USER":www-data "$LOG_DIR"
chmod 775 "$LOG_DIR"

echo -e "${C_EXITO}✅ Directori de logs${RESET} ${C_INFO}$LOG_DIR${RESET} ${C_EXITO}creat i permisos assignats a${RESET} ${C_INFO}$APP_USER${RESET} ${C_EXITO}y${RESET} ${C_INFO}www-data.${RESET}"
echo -e "\n"
sleep 3

# =====================================================================
# CREACIÓ D'ARXIUS TEMPORALS SEPARATS PER CRONTAB
# =====================================================================

CRONTAB_FILE_APP_USER="/tmp/crontab_${PROJECT_FOLDER}_$APP_USER.tmp"
CRONTAB_FILE_WWW_DATA="/tmp/crontab_${PROJECT_FOLDER}_www-data.tmp"

echo -e "${C_SUBTITULO}--- 2.2 Generant arxiu temporal per l'usuari '$APP_USER' ---${RESET}"
echo -e "${C_SUBTITULO}------------------------------------------------------------${RESET}"

cat <<- CRONEOF_APP > "$CRONTAB_FILE_APP_USER"
# =================================================================
# TASQUES PROGRAMADES PER A DJANGO-AULA ($PROJECT_FOLDER)
# USUARI: $APP_USER
#
# FORMAT CRON: minut (0-59) hora (0-23) dia_mes (1-31) mes (1-12) dia_setmana (0-7, 0=7=Dg)
# =================================================================

# Tasca 1: Còpia de Seguretat de Base de Dades (Execució cada 20 minuts)
# Utilitza l'script '$BACKUP_SCRIPT' generat al pas 1.
0,20,40 * * * * $BACKUP_SCRIPT >> $LOG_DIR/backup.log 2>&1

CRONEOF_APP

echo -e "${C_EXITO}☑️ Fitxer temporal per a còpia de seguretat${RESET} ${C_INFO}$CRONTAB_FILE_APP_USER${RESET} ${C_EXITO}generat.${RESET}"
echo -e "\n"

sleep 2

echo -e "${C_SUBTITULO}--- 2.3 Generant fitxer temporal per a l'usuari 'www-data' ---${RESET}"
echo -e "${C_SUBTITULO}-----------------------------------------------------------------${RESET}"

cat <<- CRONEOF_WWW > "$CRONTAB_FILE_WWW_DATA"
# =================================================================
# TASQUES PROGRAMADES PER A DJANGO-AULA ($PROJECT_FOLDER)
# USUARI: www-data
#
# FORMAT CRON: minut (0-59) hora (0-23) dia_mes (1-31) mes (1-12) dia_setmana (0-7, 0=7=Dg)
# =================================================================

# Tasca 2: Notificació a famílies cada dia de la setmana, excepte el Dissabte i el Diumenge.
# La notificació es produeix en el minut 42 de cada hora, començant a les 8:42h del matí i acabant a les 21:42h de la nit.
42 8,9,10,11,12,13,14,15,16,17,18,19,20,21 * * 1-5 bash -c "$FULL_PATH/scripts/notifica_families.sh >> $LOG_DIR/notifica_families_\`date +\%Y_\%m_\%d\`.log 2>&1"

# Tasca 3: Preescriptura d'incidències cada dia de la setmana, excepte el Dissabte i el Diumenge.
# La preescriptura es produeix sempre 41 minuts després de la mitjanit.
41 00 * * 1-5 bash -c "$FULL_PATH/scripts/preescriu_incidencies.sh >> $LOG_DIR/prescriu_incidencies_\`date +\%Y_\%m_\%d\`.log 2>&1"

# Tasca 4: Sincronització de presència cada 30 minuts, cada dia de la setmana, excepte el Dissabte i el Diumenge.
# La sincronització de presència es produeix sempre en el minut 20 i en el minut 50 de cada hora.
20,50 * * * 1-5 bash -c "$FULL_PATH/scripts/sortides_sincronitza_presencia.sh >> $LOG_DIR/sincro_presencia_\`date +\%Y_\%m_\%d\`.log 2>&1"

# Tasca 5: Avís a tutors de faltes (es produeix a les 2:30h de la matinada dels Dimarts, Dijous i Dissabte)
30 2 * * 2,4,6 bash -c "$FULL_PATH/scripts/avisa_tutor_faltes.sh >> $LOG_DIR/avisa_tutor_faltes_\`date +\%Y_\%m_\%d\`.log 2>&1"

CRONEOF_WWW

echo -e "${C_EXITO}☑️ Fitxer temporal per a scripts${RESET} ${C_INFO}$CRONTAB_FILE_WWW_DATA ${C_EXITO}generat.${RESET}"

sleep 3

# ----------------------------------------------------------------------
# 3. INSTAL·LACIÓ DE TASQUES CRON
# ----------------------------------------------------------------------

echo -e "\n\n"
echo -e "${C_CAPITULO}========================================================="
echo -e "${C_CAPITULO}--- 3. INSTAL·LACIÓ DE TASQUES CRON PER A CADA USUARI ---"
echo -e "${C_CAPITULO}=========================================================${RESET}"
echo -e "\n"

echo -e "${C_SUBTITULO}--- 3.1 Instal·lant crontab per a l'usuari${RESET} ${CIANO}'$APP_USER'${RESET}${C_SUBTITULO} (Còpia de seguretat) ---${RESET}"
echo -e "${C_SUBTITULO}--------------------------------------------------------------${RESET}"

# Instal·lació directa del fitxer temporal per a APP_USER
crontab -u "$APP_USER" "$CRONTAB_FILE_APP_USER"

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR: Fallada en instal·lar la tasca de còpia de seguretat per a '$APP_USER'.${RESET}"
else
    echo -e "${C_EXITO}✅ Tasca de còpia de seguretat instal·lada en crontab de${RESET} ${C_INFO}$APP_USER${RESET}"
fi
echo -e "\n"
sleep 3

echo -e "${C_SUBTITULO}--- 3.2 Instal·lant crontab per a l'usuari${RESET} ${CIANO}'www-data'${RESET}${C_SUBTITULO} (Scripts) ---${RESET}"
echo -e "${C_SUBTITULO}-------------------------------------------------------------------${RESET}"

# Instal·lació directa del fitxer temporal per a www-data
crontab -u www-data "$CRONTAB_FILE_WWW_DATA"

if [ $? -ne 0 ]; then
    echo -e "${C_ERROR}❌ ERROR: Fallada en instal·lar les tasques per a 'www-data'.${RESET}"
else
    echo -e "${C_EXITO}✅ Tasques d'scripts instal·lades en crontab de${RESET} ${C_INFO}www-data${RESET}"
fi
sleep 3

# Neteja dels dos fitxers temporals
rm "$CRONTAB_FILE_APP_USER" "$CRONTAB_FILE_WWW_DATA"

echo -e "\n\n"
echo -e "${C_PRINCIPAL}================================================================"
echo -e "${C_PRINCIPAL}--- FASE 3: CONFIGURACIÓ DE CRON FINALITZADA${RESET} ${CIANO}(setup_cron.sh)${RESET} ${C_PRINCIPAL}---"
echo -e "${C_PRINCIPAL}================================================================${RESET}"
echo -e "\n"
echo "   Per comprovar si les tasques han quedat instal·lades pot executar les següents ordres:"
echo -e "      $ ${C_SUBTITULO}sudo crontab -u $APP_USER -l${RESET}"
echo -e "      $ ${C_SUBTITULO}sudo crontab -u www-data -l${RESET}"
echo -e "\n"

sleep 5

echo -e "${C_EXITO}===============================================================${RESET}"
echo -e "${C_EXITO}--- 🎉 ENHORABONA: ¡INSTAL·LACIÓ DE DJANGO-AULA COMPLETADA! ---${RESET}"
echo -e "${C_EXITO}===============================================================${RESET}"
echo -e "\n"
echo "Si ha seguit les 3 fases indicades en l'ordre correcte i no hi ha hagut cap fallada en el procés..."
echo -e "${NEGRITA}L'aplicació DJANGO-AULA haurà quedat instal·lada amb èxit.${RESET}"
echo -e "\n"
echo "A partir d'ara DJANGO-AULA (DjAu) ja es troba preparat per a rebre les dades del seu centre educatiu (alumnat, professorat, horaris, etc)."
echo -e "\n"

sleep 3

echo -e "${C_CAPITULO}--- Recordatori d'accés a l'aplicatiu ---${RESET}"
echo -e "\n"

if [[ "$INSTALL_TYPE_LOWER" == "pub" ]]; then
    echo -e "${C_INFO}ℹ️ L'accés ha d'utilitzar la URL segura (HTTPS).${RESET}"

    if [[ "$CERT_TYPE_LOWER" == "auto" ]]; then
        echo -e "${C_INFO}    Com que s'ha instal·lat un certificat ${NEGRITA}Autofirmat TEMPORAL${RESET}, el navegador mostrarà una ADVERTÈNCIA DE SEGURETAT. Haurà de confirmar l'excepció per continuar i accedir a l'aplicatiu.${RESET}"
        echo -e "\n"
        echo -e "${C_SUBTITULO}    URL d'Accés per IP (Recomanat per a Tests/VM):${RESET}"
        echo -e "${NEGRITA}   ➡️ https://127.0.0.1${RESET}"
        echo -e "${NEGRITA}   ➡️ https://localhost${RESET}"
        echo -e "\n"
        echo -e "${C_SUBTITULO}    URL d'Accés per Domini (Utilitza el nom del certificat):${RESET}"
        echo -e "${NEGRITA}   ➡️ https://$DOMAIN_CLEAN${RESET}"
        echo -e "   (Aquesta URL només funcionarà si '$DOMAIN_CLEAN' està definit al fitxer /etc/hosts de la VM o resolt amb registre DNS d'un servidor de domini.)"
    else
        echo -e "${C_INFO}    S'ha instal·lat un certificat ${NEGRITA}Vàlid (Let's Encrypt).${RESET}${C_INFO} L'accés hauria de ser segur.${RESET}"
        echo -e "${NEGRITA}   ➡️ https://$DOMAIN_CLEAN${RESET}"
    fi

else # INTERNA
    echo -e "${C_INFO}S'ha instal·lat en mode ${NEGRITA}INTERN${RESET}${C_INFO} (sense SSL).${RESET}"
    echo -e "${C_SUBTITULO}URL d'Accés: ${RESET}"
    echo -e "${NEGRITA}   ➡️ http://127.0.0.1${RESET}"
    echo -e "${NEGRITA}   ➡️ http://localhost${RESET}"
    echo -e "${NEGRITA}   ➡️ http://$DOMAIN_CLEAN${RESET} Si està definit a /etc/hosts o amb registre DNS d'un servidor de domini."
fi
echo -e "\n"

echo -e "${C_CAPITULO}--- CÀRREGA DE DADES DEL CURS ESCOLAR ---${RESET}"
echo -e "\n"
echo -e "${NEGRITA}➡️ SEGÜENT PAS: Càrrega de dades i configuració del curs escolar.${RESET}"
echo -e "   Consulti les instruccions detallades per a tot el procés de càrrega de dades a l'apartat corresponent en GitHub"
echo -e "\n\n"

sleep 3

# ----------------------------------------------------------------------
# PAS FINAL: ADVERTÈNCIA DE SEGURETAT CRÍTICA
# ----------------------------------------------------------------------

echo -e "\n"
echo -e "${C_TITULO}=================================================${RESET}"
echo -e "${C_ERROR}🚨 ALERTA DE SEGURETAT CRÍTICA: MODO DEBUG ACTIU!${RESET}"
echo -e "${C_TITULO}=================================================${RESET}"
echo -e "L'aplicatiu DJNGO-AULA s'ha instal·lat amb el paràmetre ${C_ERROR}DEBUG = True${RESET}, visible a l'inici de l'arxiu /aula/settings_local.py."
echo -e "Aquest mode és útil abans de la càrrega de dades pel curs escolar ${C_INFO}(configuració inicial del curs)${RESET}, però també per ${C_INFO}depuració d'errors${RESET} quan l'aplicatiu està funcionant a mig curs."
echo ""
echo "En mode DEBUG:"
echo "* L'aplicatiu només permetrà l'accés a usuaris amb permisos d'administració (o molt elevats)."
echo "* Exposarà informació tècnica sensible si es produeixen errors."
echo ""
echo "🛑 ACCIÓ REQUERIDA PER POSAR EN PRODUCCIÓ:"
echo "------------------------------------------"
echo -e "${C_INFO}Un cop finalitzada la càrrega inicial de dades, configuració dels usuaris i de totes les particularitats del curs escolar:${RESET}"
echo -e "1. Editi l'arxiu ${C_EXITO}'$FULL_PATH/aula/settings_local.py'${RESET}"
echo -e "2. Canviï la línia:"
echo -e "      DEBUG = ${C_ERROR}True${RESET}"
echo -e "   Per:"
echo -e "      DEBUG = ${C_EXITO}False${RESET}"
echo -e "3. ${C_INFO}Reiniciï el servidor Apache (sudo systemctl restart apache2) o, per a més seguretat, tot el servidor.${RESET}"
echo -e "${C_TITULO}========================================================================================================${RESET}"
echo -e "\n"
