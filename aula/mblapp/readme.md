# Exemples crides a la API
>Aquesta és la documentació de la part servidora de l'APP.
### Intro
L'App part backend funciona amb rest i jwt. Hi ha un nous requeriments:

* djangorestframework
* djangorestframework-jwt
* qrcode

### Workflow Alta Família

* Tutor genera i imprimeix codi QR ( des del menú "Tutoria/Mòbil App")
* Família escaneja codi QR. En aquest moment se li crea un usuari vinculat a l'alumne. L'usuari encara no està actiu. Família signa paper i el retorna al tutor.
* Amb el paper signat tutor activa l'usuari.

Nota: El tutor pot imprimir tants i tants QR's com vulgui.

### Workflow Notificacions

* El procés **notifica** de **relacioFamilies**  actualitza el camp **novetats_detectades_moment** del model **QRPortal** quan detecta que hi ha novetats a informar a la família.* L'aplicació fa pooling demanant si hi ha novetats (fem pooling per evitar usar serveis de tercers de push)
* La part servidora anota la data en que li ha enviat a la família les dades.

Nota: Sempre s'envien totes les dades, no és incremental.
### Estat actual:

Falta per programar:

* Envia a l'app assistència, incidències i expulsions. Cal ampliar-ho a la resta ( sancions, qualitativa, sortides,.... )


### Provatures part servidora des de la línia de comandes
```bash
#Fase 0: Li passem el token inicial. TODO: usuari -> username, demanar data naixement
export INITIALTOKEN="b55f31b8-57e2-4f4f-ac66-e133ec20ff3e"   #copiar-lo del .odt on hi ha el QR
export BORNDATE="2004-05-13"
curl -X POST -H "Content-Type: application/json" -d "{\"key\":\"${INITIALTOKEN}\", \"born_date\":\"${BORNDATE}\"  }" http://localhost:8000/api/token/capture_token_api/
#Ex resposta: {"username":"APIm3wi","password":"0BGhwmUWtU9P"}

#Fase 1: Posar l'usuari a estat actiu ( a mà ho fa el professor per UI ):
$ python manage.py shell
from django.contrib.auth.models import User
u=User.objects.get(username ="APIqAxX")
u.is_active = True
u.save()
exit()

#Fase 2: Prova de demanar un token per accedir-hi
$
curl -X POST -H "Content-Type: application/json" -d '{"username":"APIm3wi","password":"0BGhwmUWtU9P"}' http://localhost:8000/api-token-auth/
#Ex. resposta: {"token":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIyNjY4ODIsImVtYWlsIjoiIn0.VIAod8nnznP0WOjAWIS6dh2sO-XqXGeYwCfsLCNmXyw"}

#Fase 3: Prova accedir a recurs amb el token
export JWTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIyNjY4ODIsImVtYWlsIjoiIn0.VIAod8nnznP0WOjAWIS6dh2sO-XqXGeYwCfsLCNmXyw
curl -H "Authorization: JWT ${JWTOKEN}" http://127.0.0.1:8000/api/token/hello_api_login/
#Resposta: {"status":"here we are just login"}

##Fase 4: Demanar les dades de l'alumne d'un mes concret
export JWTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIyNjcyNjksImVtYWlsIjoiIn0.FwF9NHS6De9FYllUTnDWHDXfApit3po1fnVB1pjUq2Q
export LASTSYNCDATE="2018-06-01 12:00:13"
curl -H "Authorization: JWT ${JWTOKEN}" -d "{\"last_sync_date\":\"${LASTSYNCDATE}\"  }" http://127.0.0.1:8000/api/token/notificacions/mes/10/
#Resposta: [{"id":155,"darrera_sincronitzacio":null},
#{"dia":"13/10/2022","materia":"SMX12(2)","hora":"14:50 a 15:50","professor":"Àngel Bosch Hernàndez","text":"Falta d'assistència","tipus":"Falta"},
#{"dia":"10/10/2022","materia":"SMX12(2)","hora":"19:00 a 19:55","professor":"Daniel Prados","text":"Falta d'assistència","tipus":"Falta"},
#{"dia":"10/10/2022","materia":"SMX12(2)","hora":"18:00 a 19:00","professor":"Daniel Prados","text":"Falta d'assistència","tipus":"Falta"},
#{"dia":"11/10/2022","hora":"19:00 a 19:55","professor":"Juaky Rubio","text":"Parla, molesta i no deixa treballar als companys.","tipus":"Falta"}
#]

#Fase 5: Demanar si hi ha novetats
export JWTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIyNjc2NTksImVtYWlsIjoiIn0.T3sPlZMhXSzhiGeId4nlqAQMmfxO1tqSLFctqcWDkGo
export LASTSYNCDATE="2022-11-18 12:00:13"
curl -H "Authorization: JWT ${JWTOKEN}" -d "{\"last_sync_date\":\"${LASTSYNCDATE}\"  }" http://127.0.0.1:8000/api/token/notificacions/news/
#Resposta: {"resultat":"Sí"}

$# ------------------- Altres proves ------------------------------
#Prova accedir sense el token
$
$ curl http://127.0.0.1:8000/api/token/notificacions/news/
{"detail":"Authentication credentials were not provided."}
