#!/bin/bash
# functions.sh
# Conté funcions i variables d'estil comuns a tots els scripts per la insta·lació automàtica

# --------------------------------------------------
# VARIABLES DE COLOR I ESTIL ANSI
# --------------------------------------------------

RESET='\e[0m'
NEGRITA='\e[1m'

# Colors básics
AZUL='\e[34m'
VERDE='\e[32m'
ROJO='\e[31m'
CIANO='\e[36m'
AMARILLO='\e[33m'
MAGENTA='\e[35m'
GRIS='\033[0;90m'  # Gris clar (ideal per a logs)

# Estils compostos
C_EXITO="${NEGRITA}${VERDE}"       # Éxit i confirmacions (✅)
C_ERROR="${NEGRITA}${ROJO}"        # Errors o fallades (❌)
C_PRINCIPAL="${NEGRITA}${AZUL}"    # Fases principals (FASE 1, FASE 2)
C_CAPITULO="${NEGRITA}${CIANO}"    # Títuls de Capítul (1. DEFINICIÓ...)
C_SUBTITULO="${NEGRITA}${MAGENTA}" # Títuls de Subcapítul (1.1, 1.2)
C_INFO="${NEGRITA}${AMARILLO}"     # Informació important (INFO, ATENCIÓ)


# ===========================================================================
# Funció: finalitzar_amb_error
# Serveix per mostrar un text d'error concret greu i sortir de l'instal·lador
#
# Exemple: finalitzar_amb_error "No s'ha pogut obtenir la clau per a $OS_ID des de download.docker.com"
# ===========================================================================

finalitzar_amb_error() {
    echo -e "\n"
    echo -e "${C_ERROR}❌ ERROR: $1${RESET}"
    echo "La instal·lació s'ha aturat perquè un pas crític ha fallat."
    exit 1
}


# =========================================================================
# Funció: read_prompt
# Demana a l'usuari una resposta a una pregunta i comprova que l'escriu o
# que la deixa en blanc, si hi ha una resposta per defecte.
#
# Exemple: read_prompt "De quin color tens el cabell?" COLOR_CABELL "Blau"
# =========================================================================

read_prompt () {
    # $1: Missatge (prompt)
    # $2: Nom de la variable a assignar (sense $)
    # $3: [Opcional] Valor per defecte (si s'omet o si es buit, el camp és obligatori)

    local PROMPT_MSG="$1"
    local VAR_NAME="$2"
    local DEFAULT_VALUE="$3"
    local INPUT_VALUE=""

    while true; do
        # 1. Llegit l'entrada de l'usuari
        read -p "$PROMPT_MSG" INPUT_VALUE

        # 2. Eliminar espais en blanc, abans i després del valor entrat (trim)
        INPUT_VALUE=$(echo "$INPUT_VALUE" | xargs)

        if [ -z "$INPUT_VALUE" ]; then
            # A) Si no hi ha entrada de l'usuari:

            if [ -n "$DEFAULT_VALUE" ]; then
                # A.1) Si hi ha valor per defecte ($3 te contingut), fer-lo servir i sortir-ne.
                eval "$VAR_NAME='$DEFAULT_VALUE'"
                echo -e "${C_EXITO}☑️ Valor per defecte utilitzat: '$DEFAULT_VALUE'${RESET}"
				echo -e "\n"
                break
            else
                # A.2) Si NO hi ha valor per defecte, la resposta és obligatòria.
                echo -e "${C_ERROR}❌ ERROR: Aquesta pregunta no es pot deixar en blanc.${RESET}\n"
                # Torna a iterar (while true)
            fi
        else
            # B) Si hi ha resposta de l'usuari, fer-la servir i sortir-ne.
            eval "$VAR_NAME='$INPUT_VALUE'"
            echo -e "${C_EXITO}☑️ Resposta introduïda: '$INPUT_VALUE'${RESET}"
			echo -e "\n"
            break
        fi
    done
}



# ======================================================================
# Funció: read_email_confirm
# Demana una adreça de correu, valira el seu format amb una regex simple.
#
# Exemple: read_email_confirm "Missatge de la sol·licitud: " VAR_NAME "valor_per_defecte"
# El correu validat es desa a la variable de Bash amb nom $VAR_NAME.
# ======================================================================

read_email_confirm() {
    local PROMPT_MSG="$1"
    local OUTPUT_VAR_NAME="$2"
    local DEFAULT_VALUE="$3"
    local EMAIL_REGEX="^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    local INPUT_VALUE=""
    local C_ERROR=$(tput setaf 1) # Vermell
    local C_INFO=$(tput setaf 6)  # Cian
    local RESET=$(tput sgr0)      # Reset
    local EMAIL_VALID=0 # 0=No vàlid, 1=Vàlid

    while [ $EMAIL_VALID -eq 0 ]; do
        # Construir el missatge del prompt (incloent el valor per defecte, si hi existeix)
        local CURRENT_PROMPT="$PROMPT_MSG"
        if [ -n "$DEFAULT_VALUE" ]; then
            CURRENT_PROMPT="$PROMPT_MSG (per defecte: $DEFAULT_VALUE): "
        fi

        # Llegir la resposta de l'usuari
        read -r -p "$CURRENT_PROMPT" INPUT_VALUE

        # Si l'usuari prem Enter i hi ha valor per defecte, fer-lo servir.
        if [ -z "$INPUT_VALUE" ] && [ -n "$DEFAULT_VALUE" ]; then
            INPUT_VALUE="$DEFAULT_VALUE"
        fi

        # 1. Comprovar si no s'ha proporcionat un correu (no permès en aquest cas)
        if [ -z "$INPUT_VALUE" ]; then
            echo -e "${C_ERROR}❌ ERROR: Cal proporcionar un correu electrònio. La resposta no pot estar buida. Provi de nou.${RESET}"
            continue
        fi

        # 2. Comprovar el format amb la regex (es fa servir =~ en Bash)
        if [[ "$INPUT_VALUE" =~ $EMAIL_REGEX ]]; then
            EMAIL_VALID=1
        else
            echo -e "${C_ERROR}❌ ERROR: El format del correu ('$INPUT_VALUE') no sembla vàlld. Ha de ser: usuari@domini.ext Provi de nou.${RESET}"
        fi
    done

    # Assignar el valor validat a la variable de sortida
    eval "$OUTPUT_VAR_NAME=$(printf %q "$INPUT_VALUE")"
}



# ======================================================================
# Funció: read_password_confirm
# Demana una contrasenya i la seva repetició, validant que coincideixen i que no siguin respostes buides.
#
# Exemple: read_password_confirm "Missatge de la primera sol·licitud: " VAR_NAME
# La contrasenya validada es desa a la variable de Bash amb el nom $VAR_NAME.
# ======================================================================

read_password_confirm() {
    local PROMPT_MSG="$1"
    local OUTPUT_VAR_NAME="$2"
    local PASSWD=""
    local PASSWD2=""
    local C_ERROR=$(tput setaf 1) # Vermell
    local RESET=$(tput sgr0)      # Reset

    while true; do
        # Sol·licitud de la primera contrasenya
        read -sp "$PROMPT_MSG" PASSWD
        echo

        # Sol·licitud de la repetició de la contrasenya
        read -sp "Repeteixi la CONTRASENYA: " PASSWD2
        echo -e "\n"

        if [ -z "$PASSWD" ] || [ -z "$PASSWD2" ]; then
            echo -e "${C_ERROR}❌ ERROR: La contrasenya no pot deixar-se en blanc. Provi de nou.${RESET}\n"
        elif [ "$PASSWD" != "$PASSWD2" ]; then
            echo -e "${C_ERROR}❌ ERROR: Les contrasenyes no coincideixen. Provi de nou.${RESET}\n"
        else
            # Assignar el valor final de la contrasenya a la variable de sortida
            # 'eval' cal per assignar dinàmicament el valor a una variable el nom de la qual és una cadena.
            # Es fa servir 'printf %q' per a assegurar el valor i evitar injecció de shell amb 'eval'.
            eval "$OUTPUT_VAR_NAME=$(printf %q "$PASSWD")"
            break
        fi
    done
}


# ======================================================================
# Funció: check_install
# Comprova la instal·lció de paquets i informa si hi ha hagut cap error
# o si els paquests s'han instal·lat correctament.
#
# Exemple: check_install "Nucli Django i Python"
# ======================================================================

check_install() {
    # $1: Descripció dels paquest a instal·lar

    local EXIT_CODE=$?    # Desa el codi de sortida de de la comanda anterior
    local DESC_MSG="$1"   # Desa el primer argument (la descripció)

    if [ "$EXIT_CODE" -ne 0 ]; then
        echo -e "\n"
        echo -e "${C_ERROR}❌ ERROR CRÍTIC: Hi ha hagut una fallada a la instal·lació de: ${DESC_MSG}${RESET}"
        echo -e "${C_INFO}ℹ️ L'última ordre ha tornat el codi d'error $EXIT_CODE.${RESET}"
        echo -e "${C_INFO}ℹ️ No eé possible continuar. Revisi la connexió, el log i executi l'script de nou.${RESET}"
        echo -e "\n"
        exit 1
    else
	    echo -e "\n"
        echo -e "${C_EXITO}✅ Instal·lació: '${DESC_MSG}' completada amb èxit.${RESET}"
    fi
    echo -e "\n"
	sleep 2
}
