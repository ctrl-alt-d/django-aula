# ⚙️ Configuració Avançada de DjAu

Aquest document detalla les opcions de configuració avançada del Django-Aula (DjAu) que defineixen el comportament de l'aplicació en qüestions de política interna (seguretat, disciplina, gestió de dades i mòduls).

---

## 1. Configuració per Fitxer (settings_local.py)

Aquestes variables es gestionen mitjançant l'arxiu de configuració local `settings_local.py`. En el procés d'instal·lació automàtic, s'afegeixen automàticament, si l'instal·lador ho desitja, al final del fitxer, però **comentades** (amb el símbol `#`), per defecte. Si no s'ha efectuat la instal·lació automatitzada sempre pot triar les variables que necessita i afegir-les manualment.

Recordi:  
> **Ruta del Fitxer:** `aula/settings_local.py` (s'importa des de `setup_djau/advanced_settings.py`)

### Instruccions d'Ús

1.  **Editeu** l'arxiu `aula/settings_local.py` amb permís d'administrador.
2.  Localitzeu el bloc de configuració avançada al final del fitxer (si les heu afegides en el procés d'instal·lació automatitzat).
3.  Per activar o modificar una funcionalitat, **descomenteu** la línia (`# VARIABLE = Valor` a `VARIABLE = Valor`) i ajusteu el valor segons les necessitats.
4.  **Apliqueu els canvis:** Cal **reiniciar el servidor Apache/WSGI** perquè la nova configuració tingui efecte.

### Catàleg de Variables Avançades (advanced_settings.py)

#### 1. Seguretat i Accés

| Variable | Descripció | Valor Per Defecte |
| :--- | :--- | :--- |
| `LIMITLOGIN` | Límit d'intents de connexió fallits abans que el compte quedi bloquejat. | `5` |
| `CUSTOM_TIMEOUT` | Temps màxim d'inactivitat (en segons) abans de tancar la sessió. | `900` (15 min) |
| `CUSTOM_TIMEOUT_GROUP` | Permet definir un temps d'espera diferent segons el grup d'usuaris (p. ex., consergeria o professors). | `Comentat` |

#### 2. Gestió d'Incidències i Faltes

| Variable | Descripció | Valor Per Defecte |
| :--- | :--- | :--- |
| `CUSTOM_TIPUS_INCIDENCIES` | Si **True**, activa la possibilitat de classificar les incidències per tipus. | `False` |
| `CUSTOM_RETARD_PROVOCA_INCIDENCIA` | Si **True**, cada retard registrat genera automàticament una incidència. | `False` |
| `CUSTOM_RETARD_TIPUS_INCIDENCIA` | Defineix el tipus d'incidència (e.g., *Incidència*, *informativa*) generat automàticament per un retard. | `Comentat` |
| `CUSTOM_RETARD_FRASE` | Frase utilitzada a la incidència generada automàticament per un retard. | `Comentat` |
| `CUSTOM_PERIODE_CREAR_O_MODIFICAR_INCIDENCIA` | Nombre de dies que es permet crear o modificar una incidència antiga. | `90` |
| `CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO` | Si **True**, l'acumulació d'incidències pot obligar a l'expulsió de l'alumne. | `True` |
| `CUSTOM_PERIODE_MODIFICACIO_ASSISTENCIA` | Nombre de dies que es permet modificar l'assistència (per correcció de professors). | `90` |
| `CUSTOM_DIES_PRESCRIU_INCIDENCIA` | Dies que una incidència ha de transcórrer per prescriure. | `30` |
| `CUSTOM_DIES_PRESCRIU_EXPULSIO` | Dies que una expulsió ha de transcórrer per prescriure. | `90` |
| `CUSTOM_NOMES_TUTOR_POT_JUSTIFICAR` | Si **True**, només el tutor pot justificar absències dels seus alumnes. | `True` |
| `CUSTOM_PERMET_COPIAR_DES_DUNA_ALTRE_HORA` | Si **True**, permet copiar el llistat d'assistència des d'una altra hora. | `False` |
| `CUSTOM_RETARD_PRIMERA_HORA_GESTIONAT_PEL_TUTOR` | Si **True**, gestiona el retard de primera hora pel tutor (en lloc de consergeria/administració). | `False` |
| `CUSTOM_FALTES_ABSENCIA_PER_CARTA` | Faltes d'absència no justificades (en dies) per tal de generar la carta base. | `15` |
| `CUSTOM_FALTES_ABSENCIA_PER_TIPUS_CARTA` | Permet definir el límit de faltes per a cada **tipus** de carta. | `Comentat` |
| `CUSTOM_FALTES_ABSENCIA_PER_NIVELL_NUM_CARTA` | Permet definir el límit de faltes segons el **nivell** i el número de carta. Invalida l'opció anterior si s'activa. | `Comentat` |

#### 3. Mòduls i Funcionalitat

| Variable | Descripció | Valor Per Defecte |
| :--- | :--- | :--- |
| `CUSTOM_MODUL_SORTIDES_ACTIU` | Activa el mòdul de gestió de sortides i activitats. | `True` |
| `CUSTOM_SORTIDES_OCULTES_A_FAMILIES` | Si **True**, s'oculten les sortides a les famílies (si la gestió o pagament es fa amb una plataforma externa). | `False` |
| `CUSTOM_QUOTES_ACTIVES` | Si **True**, activa si es permet fer servir les quotes. | `False` |
| `CUSTOM_TIPUS_QUOTA_MATRICULA` | Nom del tipus de quota per als pagaments de matrícula. | `Comentat` |
| `CUSTOM_QUOTA_UNICA_MATRICULA` | Si **True**, permet utilitzar una única definició de quota per a tot l'alumnat de matrícula. | `Comentat` |
| `CUSTOM_FAMILIA_POT_MODIFICAR_PARAMETRES` | Si **True**, permet que la família pugui modificar els seus paràmetres a l'aplicació. | `False` |
| `CUSTOM_FAMILIA_POT_COMUNICATS` | Si **True**, permet a la família enviar comunicats. | `False` |
| `CUSTOM_MODUL_PRESENCIA_SETMANAL_ACTIU` | Si **True**, activa el mòdul de presència setmanal (graella amb faltes). | `False` |
| `CUSTOM_NO_CONTROL_ES_PRESENCIA` | Si **False**, desactiva la comprovació de "és presència" en el control. | `False` |
| `CUSTOM_TUTORS_INFORME` | Si **True**, permet als tutors tenir accés als informes de seguiment de faltes i incidències. | `False` |
| `CUSTOM_RULETA_ACTIVADA` | Activa el filtre per mostrar la ruleta d'alumnes a la pantalla de passar llista. | `True` |
| `CUSTOM_MOSTRAR_MAJORS_EDAT` | Si **True**, permet mostrar si l'alumne és major d'edat. | `Comentat` |
| `CUSTOM_MARCA_MAJORS_EDAT` | Marca utilitzada per indicar la majoria d'edat. | `Comentat` |
| `CUSTOM_PORTAL_FAMILIES_TUTORIAL` | Indica la descripció i l'adreça del tutorial per a les famílies. | `Comentat` |

#### 4. Pagaments i Comerç Electrònic

| Variable | Descripció | Valor Per Defecte |
| :--- | :--- | :--- |
| `CUSTOM_SORTIDES_PAGAMENT_ONLINE` | Si **True**, permet realitzar pagaments online (requereix configuració Redsys/entitat). | `False` |
| `CUSTOM_REDSYS_ENTORN_REAL` | Entorn Redsys: **True** per a real, **False** per a proves. | `False` |
| `CUSTOM_PREU_MINIM_SORTIDES_PAGAMENT_ONLINE` | Preu mínim (en €) per una sortida per activar el pagament online. | `1` |
| `CUSTOM_SORTIDES_PAGAMENT_CAIXER` | Si **True**, activa si es permet fer pagament per caixer. | `True` |
| `CUSTOM_FORMULARI_SORTIDES_REDUIT` | Si **True**, utilitza un formulari de dades reduït per a pagaments. | `True` |
| `CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT` | Text d'instruccions de pagament per defecte. | `Comentat` |
| `CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ENTITAT_BANCARIA` | Text d'instruccions per a pagament en entitat bancària. | `Comentat` |
| `CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_EFECTIU` | Text d'instruccions per a pagament en efectiu. | `Comentat` |
| `CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ONLINE` | Text d'instruccions per a pagament online. | `Comentat` |

#### 5. Diversos i Localització

| Variable | Descripció | Valor Per Defecte |
| :--- | :--- | :--- |
| `CUSTOM_NIVELLS` | Permet definir l'estructura de nivells del centre (e.g., ESO, BTX, CICLES). | `Comentat` |
| `CUSTOM_ORDER_PRESENCIA` | Permet reordenar la llista d'assistència (per cognom, nom, grup, etc.). | `Comentat` |
| `CUSTOM_LC_TIME` | Formats de temps i data a nivell de sistema operatiu. | `Comentat` |
| `CUSTOM_DATE_FORMAT` | Format de data a mostrar a l'aplicació (e.g., `%-d %B de %Y`). | `Comentat` |
| `CUSTOM_MAX_EMAIL_RECIPIENTS` | Quantitat màxima de destinataris per cada email, depèn del servidor de correu. | `100` |
| `CUSTOM_DADES_ADDICIONALS_ALUMNE` | Permet afegir altres dades dels alumnes (e.g., Drets imatge, Dades mèdiques) des de Sincronitza. | `Comentat` |
| **Fitxers de Rutes (Legal)** | Rutes a fitxers de text per a condicions legals (GPD, Cookies, Venda, Fiscals) que es mostren en diferents parts de l'aplicació. | `Comentat` |

#### 6. Configuració Tècnica Avançada

| Variable | Descripció | Valor Per Defecte |
| :--- | :--- | :--- |
| `CUSTOM_GRUPS_PODEN_VEURE_FOTOS` | Llista de grups d'usuaris que tenen permís per veure les fotos dels alumnes. | `Comentat` |
| `CUSTOM_TIPUS_MIME_FOTOS` | Tipus MIME permesos per a les fotos dels alumnes. | `Comentat` |
| `CUSTOM_INDICADORS` | Configuració complexa per al càlcul d'indicadors d'absentisme (percentatge d'absències sobre hores lectives per període/nivell). | `Comentat` |

---

## 2. 🗄️ Configuració per Base de Dades (Admin)

És important recordar que DjAu utilitza la Base de Dades per emmagatzemar la configuració de mòduls d'integració externs, pagaments TPV i contrasenyes de sincronització.

**Aquests paràmetres NO s'han d'afegir a `settings_local.py`**.

### Com es Configura?

La seva configuració es gestiona a través de la **interfície d'administració de DjAu** (ruta `/admin/`). Cal buscar el mòdul d'extensió corresponent (p. ex., `Extkronowin`, `Extsaga`).

### Paràmetres Típics de BBDD

| Paràmetre | Mòdul | Exemple de Configuració |
| :--- | :--- | :--- |
| `ParametreKronowin.passwd` | `Extkronowin` | Contrasenya per defecte dels nous usuaris importats. |
| `ParametreSaga.grups estatics` | `Extsaga` | Llista de grups que no han de ser modificats durant la sincronització SAGA. |
| `ParametreKronowin.assignatures amb professor` | `Extkronowin` | Codi d'assignatures optatives que s'han de diferenciar pel professorat. |
| `Sortides TPVs` | `Sortides` | Configuració dels codis de comerç i *keys* per als TPV de pagament online. |

***

