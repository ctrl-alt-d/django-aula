# Exemples crides a la API
>Aquesta és la documentació de la part servidora de l'APP.
### Intro

L'App part backend funciona amb rest i jwt. Hi ha un nous requeriments:

* djangorestframework
* djangorestframework-jwt
* qrcode

### Workflow Alta Família

* Tutor genera i imprimeix codi QR ( des del menú portal en aquest moment )
* Família escaneja codi QR. En aquest moment se li crea un usuari vinculat a l'alumne. L'usuari encara no està actiu. Família signa paper i el retorna al tutor.
* Amb el paper signat tutor activa l'usuari.

Nota: El tutor pot imprimir tants i tants QR's com vulgui.

### Workflow Notificacions

* El procés **notifica** de **relacioFamilies**  actualitza el camp **novetats_detectades_moment** del model **QRPortal** quan detecta que hi ha novetats a informar a la família.
* L'aplicació fa pooling demanant si hi ha novetats (fem pooling per evitar usar serveis de tercers de push)
* La part servidora anota la data en que li ha enviat a la família les dades.

Nota: Sempre s'envien totes les dades, no és incremental.
### Estat actual:

Només falten dues coses per programar:

* notifica (a relació famílies): cal ampliar la llista als que tenen tokens.
* vista de mblapp: cal enviar les dades bones i no dades de fake.


### Provatures part servidora des de la línia de comandes

```bash
#Fase 0: Li passem el token inicial. TODO: usuari -> username, demanar data naixement
export INITIALTOKEN="08d9c337-7b15-47d5-a4c7-56f0ec2b28bd"   #copiar-lo del .odt on hi ha el QR
export BORNDATE="1992-04-04"
curl -X POST -H "Content-Type: application/json" -d "{\"key\":\"${INITIALTOKEN}\", \"born_date\":\"${BORNDATE}\"  }" http://localhost:8000/mblapp/capture_token_api/
#Ex resposta: {"username":"APIittW","password":"fRyOrWNKHegg"}

#Fase 1: Posar l'usuari a estat actiu ( a mà ho farà el professor per UI ):
$ python manage.py shell
from django.contrib.auth.models import User
u=User.objects.get(username ="APIqAxX")
u.is_active = True
u.save()
exit()

#Fase 2: Prova de demanar un token per accedir-hi
$
curl -X POST -H "Content-Type: application/json" -d '{"username":"APIpOH1","password":"sxvQx?drpOHY"}' http://localhost:8000/api-token-auth/
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ik0xIiwidXNlcl9pZCI6NCwiZW1haWwiOiIiLCJleHAiOjE1MjU5NjA5MjR9.EKEhsW-uqdblRLEpAH0uxKMb-FUnCJB6a3_3xRd4Pno"}
#Fase 3: Prova accedir a recurs amb el token
export JWTOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IkFQSXBPSDEiLCJ1c2VyX2lkIjoyMjYsImVtYWlsIjoiIiwiZXhwIjoxNTMzMDQ2MzgxfQ._OCRlFiMP7ajk5_OxI_zOqZRbCdH8r2dtADmg-FOP28
curl -H "Authorization: JWT ${JWTOKEN}" http://127.0.0.1:8000/mblapp/hello_api_login/

{"status":"here we are"}

#Fase 4: Demanar les dades de l'alumne
export JWTOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IkFQSWl0dFciLCJ1c2VyX2lkIjoyMzUsImVtYWlsIjoiIiwiZXhwIjoxNTMyOTQ4MDg5fQ.uPixe14hJFLYdALHx2lbkRj6Gl9N4GWe-SUDom1Nh0g
export LASTSYNCDATE="2018-06-01 12:00:13"
curl -H "Authorization: JWT ${JWTOKEN}" -d "{\"last_sync_date\":\"${LASTSYNCDATE}\"  }" http://127.0.0.1:8000/mblapp/syncro_data_api/

{"darrera_sincronitzacio":"2018-07-30T15:49:36.819432",
"Assistència":[{"franja":"12:00-13:05","materia":"MA","dia":"2018-06-01","tipus":"Retard"},{"franja":"10:00-11:05","materia":"FI","dia":"2018-06-02","tipus":"Justificada"}],
"Expulsions":[],
"Incidències":[{"franja":"12:00-13:05","dia":"2018-06-01","tipus":"Incidència","motiu":"Molesta els companys"},{"franja":"12:00-13:05","dia":"2018-06-02","tipus":"Observació","motiu":"Bona feina"}],
"Activitats":[],
"Sancions":[],
"id":108}

$# ------------------- Altres proves ------------------------------
#Prova accedir sense el token
$
$ curl http://127.0.0.1:8000/mblapp/hello_api_login/
{"detail":"Authentication credentials were not provided."}
Tens, si vols, una url que no demana autenticació:
$ #sense auth
$
$ curl http://127.0.0.1:8000/mblapp/hello_api/
{"status":"here we are"}
```