# Scripts per instal·lar automàticament l'apilicatiu Django-Aula

En aquest document hi ha el llistat d'arxius d'aquest directori amb la única excepció de l'script instal·lador, que es troba a l'arrel del projecte.

**Scripts per la instal·lació automàtica de l'aplicatiu Django-Aula**

- **`install_djau.sh`**: Es troba a l'arrel del projecte, no en aquest directori, i és l'script llançador de la instal·lació automàtica de l'aplicatiu Django-Aula.  
- **`setup_djau.sh`**: Es executat automàticament per l'arxiu *install_djau.sh* i s'encarrega de configurar l'arxiu *settings_local.py*, bàsic per la personalització de l'aplicatiu per un cetre educatiu concret.  
- **`setup_apache.sh`**: Instal·la i configura, principalment, el servidor web Apache que serà l'encarregat de servir l'aplicatiu al navegador client.  
- **`setup_cron.sh`**: Crea el script que farà les còpies automàtiques de seguretat de la base de dades i confitura l'execució d'altres scripts que s'han d'executar cada cert temps pel correcte funcionament de l'aplicatiu.

- **`functions.sh`**: Llibreria de funcions i variables que fan servir els scripts anteriors.

Un cop executada la instal·lació apareixerà un altre arxiu en aquest directori, anomenat **`config_vars.sh`**, que conté el contingut de variables que els scripts van generant segons es van executant de forma succesiva i que fan servir els scripts posteriors pel seu correcte funcionament. **Un cop feta la instal·lació aquest arxiu es pot esborrar**, si es desitja, però també és un recordari de quins paràmetres es van fer servir. No té cap més valor.

**`Advanced_settings.py`**: És l'arxiu que conté les parametritzacions complementàries per l'arxiu `settings_local.py`. En el procés d'instal·lació automàtic, arribat el moment, es pregunta a l'usuari instal·lador si desitja afegir-les com paràmetres comentats (amb simbol #) a *settings_local.py*. De fet és l'antic arxiu *`parametritzacions.txt`*.

**`test_email.sh`**: Quan s'està executant *setup_djau.sh*, arribat el moment es demana si es vol fer una prova d'enviament de correu per comprovar que les credencials proporcionades per configurar el compte de correu son vàlides i l'aplicatiu podrà enviar-los. Aquest script s'encarrega d'enviar un correu de prova. Es pot executar sempre que es desitji i és per aquest raó que es troba com un arxiu independent.
