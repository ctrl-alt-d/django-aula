#!/bin/bash
# test_email.sh
# Permet provar la configuració d'enviament de correu SMTP carregada a settings_local.py
# HA D'EXECUTAR-SE des del directori 'setup_djau' (on resideix) per carregar els fitxers de configuració.

clear

# ----------------------------------------------------------------------
# CÀRREGA DE VARIABLES I FUNCIONS COMUNS ALS SCRIPTS D'AUTOMATITZACIÓ
# ----------------------------------------------------------------------
echo -e "\n"
echo -e "Executant script test_email.sh."
echo -e "\n"

echo -e "${C_SUBTITULO}--- Carregant variables i funcions comunes per a la instal·lació ---${RESET}"
echo -e "${C_SUBTITULO}--------------------------------------------------------------------${RESET}"
echo -e "\n"

echo -e "Llegint functions.sh i config_vars.sh."
echo -e "\n"

# 1. CARREGAR LLIBRERIA DE FUNCIONS
source "./functions.sh"

# 2. CARREGAR VARIABLES DE CONFIGURACIÓ
CONFIG_FILE="./config_vars.sh"

if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
    echo -e "${C_EXITO}☑️ Variables de configuració carregades.${RESET}"
else
    echo -e "${C_ERROR}❌ ERROR: Fitxer de configuració ($CONFIG_FILE) no trobat. Sortint.${RESET}"
    echo -e "\n"
    exit 1
fi

# Assegurar-se que l'entorn virtual existeixi
VENV_PATH="$FULL_PATH/venv"

if [ ! -d "$VENV_PATH" ]; then
    echo -e "${C_ERROR}❌ ERROR: L'entorn virtual de Python no es troba a $VENV_PATH.${RESET}"
    echo -e "Assegureu-vos d'haver executat 'setup_djau.sh' amb anterioritat per crear l'entorn virtual i el fitxer settings_local.py."
    exit 1
fi

echo -e "\n"
echo -e "${C_CAPITULO}====================================================================="
echo -e "${C_CAPITULO}--- VERIFICACIÓ DE CORREU ELECTRÒNIC (SMTP) ---${RESET}"
echo -e "${C_CAPITULO}=====================================================================${RESET}"
echo -e "\n"

# 1. Sol·licitar la direcció de correu destinació
read_prompt "Introdueixi la direcció de correu electrònic DESTINACIÓ per a la prova: " DESTINO_EMAIL

echo -e "\n${C_INFO}ℹ️ Enviant correu de prova a ${NEGRITA}$DESTINO_EMAIL${RESET} utilitzant la configuració de settings_local.py...${RESET}"

# 2. Activar l'entorn virtual per a l'execució de Python
# L'script es mou a l'arrel del projecte ($FULL_PATH) per executar manage.py.

cd "$FULL_PATH"
source venv/bin/activate

# 3. Codi Python incrustat per a la prova

PYTHON_SCRIPT_EMAIL="temp_test_email.py"

cat << EOF_PYTHON > "$PYTHON_SCRIPT_EMAIL"
from django.core.mail import send_mail
from django.conf import settings
import sys

# L'adreça del remitent ja està carregada des de settings.
remitente = settings.DEFAULT_FROM_EMAIL
email_host = settings.EMAIL_HOST
email_port = settings.EMAIL_PORT
email_backend = settings.EMAIL_BACKEND
# Capturem la variable de shell DESTINO_EMAIL amb f-string (segur en Heredoc)
destinatario = ['${DESTINO_EMAIL}']

try:
    mensaje_texto = (
        'Aquest és un correu de prova enviat pel sistema DjAu (Django-Aula).\n\n'
        f'S\'ha enviat amb èxit utilitzant el backend: {email_backend}.\n\n'
        'La configuració SMTP utilitzada va ser:\n'
        f'    - Servidor: {email_host}\n'
        f'    - Port: {email_port}\n\n'
        'Si heu rebut aquest correu, la configuració SMTP és correcta.'
    )
    enviado = send_mail(
        'Prova de Correu DjAu - Instal·lació Automatitzada',
        mensaje_texto,
        remitente,
        destinatario,
        fail_silently=False, # Crucial per capturar excepcions
    )

    if enviado == 1:
        print('✅ ÈXIT: El correu s\'ha enviat correctament. Revisi la safata d\'entrada i la carpeta de SPAM.')
        sys.exit(0)
    else:
        # Això passa si el servidor accepta la connexió però rebutja el missatge (p.ex., filtre d'spam)
        print('❌ ERROR: L\'enviament va retornar 0. El servidor SMTP podria haver rebutjat la connexió silenciosament.')
        sys.exit(1)
except Exception as e:
    print('\n❌ ERROR CRÍTIC DURANT L\'ENVIAMENT:')
    print(f'Missatge: {e}')
    print('\n')
    print('--- PASSOS PER AL DIAGNÒSTIC ---')

    # *** AQUEST AVÍS ES MOSTRA A LA CONSOLA ***
    if 'Connection' in str(e) or 'Authentication' in str(e):
        print('1. Revisi la configuració d\'EMAIL_HOST, EMAIL_PORT i EMAIL_HOST_PASSWORD a settings_local.py.')
        print('2. Si l\'error és de connexió, comproveu les REGLES DEL TALLAFOCS (p. ex., UFW) del vostre servidor VPS.')
        print('    El tràfic SORTINT (Outbound) al port SMTP (p. ex., 587 o 465) ha d\'estar permès.')
        print('3. Si utilitzeu un proveïdor de correu extern (p. ex., Gmail), assegureu-vos d\'utilitzar una contrasenya d\'aplicació, no la vostra contrasenya principal.')

    print('\n')
    sys.exit(1)

EOF_PYTHON

# 4. Executar l'script temporal i capturar el codi de sortida
# Redirigim la sortida d'error (2>&1) perquè els missatges de Python es mostrin a l'usuari.
python manage.py shell < "$PYTHON_SCRIPT_EMAIL"
EXIT_CODE=$?

# 5. Neteja i Desactivació
rm "$PYTHON_SCRIPT_EMAIL"
deactivate

# 6. Mostrar el resultat de l'execució de la comanda Python
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${C_EXITO}✅ Prova de correu finalitzada amb èxit.${RESET}"
else
    echo -e "${C_ERROR}❌ Prova de correu fallida. Revisi els errors anteriors.${RESET}"
fi
