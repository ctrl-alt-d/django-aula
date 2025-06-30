# Exemples crides a la API
>Aquesta és la documentació de la part servidora de l'APP.
### Intro
L'App part backend funciona amb rest i jwt. Hi ha un nous requeriments:

* djangorestframework
* djangorestframework-simplejwt
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
#Ex. resposta: {
  "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU",
  "refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"
}

#Fase 3: Prova accedir a recurs amb el token
export JWTOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiY29sZF9zdHVmZiI6IuKYgyIsImV4cCI6MTIzNDU2LCJqdGkiOiJmZDJmOWQ1ZTFhN2M0MmU4OTQ5MzVlMzYyYmNhOGJjYSJ9.NHlztMGER7UADHZJlxNG0WSi22a2KaYSfd1S-AuT7lU
curl -H "Authorization: Bearer ${JWTOKEN}" http://127.0.0.1:8000/api/token/hello_api_login/
#Resposta: {"status":"here we are just login"}

##Fase 4: Demanar les dades de l'alumne d'un mes concret
export JWTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIyNjcyNjksImVtYWlsIjoiIn0.FwF9NHS6De9FYllUTnDWHDXfApit3po1fnVB1pjUq2Q
export LASTSYNCDATE="2018-06-01 12:00:13"
curl -H "Authorization: Bearer ${JWTOKEN}"  http://127.0.0.1:8000/api/token/notificacions/mes/10/
#Resposta: [{"id":155,"darrera_sincronitzacio":null},
#{"dia":"13/10/2022","materia":"SMX12(2)","hora":"14:50 a 15:50","professor":"Àngel Bosch Hernàndez","text":"Falta d'assistència","tipus":"Falta"},
#{"dia":"10/10/2022","materia":"SMX12(2)","hora":"19:00 a 19:55","professor":"Daniel Prados","text":"Falta d'assistència","tipus":"Falta"},
#{"dia":"10/10/2022","materia":"SMX12(2)","hora":"18:00 a 19:00","professor":"Daniel Prados","text":"Falta d'assistència","tipus":"Falta"},
#{"dia":"11/10/2022","hora":"19:00 a 19:55","professor":"Juaky Rubio","text":"Parla, molesta i no deixa treballar als companys.","tipus":"Falta"}
#]

#Fase 5: Demanar si hi ha novetats
export JWTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIyNjc2NTksImVtYWlsIjoiIn0.T3sPlZMhXSzhiGeId4nlqAQMmfxO1tqSLFctqcWDkGo
export LASTSYNCDATE="2022-11-18 12:00:13"
curl -H "Authorization: Bearer ${JWTOKEN}" -d "{\"last_sync_date\":\"${LASTSYNCDATE}\"  }" http://127.0.0.1:8000/api/token/notificacions/news/
#Resposta: {"resultat":"Sí"}


#Fase 6: Demanar dades de l'alumne
export JWTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIzNTQ0OTUsImVtYWlsIjoiIn0.2pgU5g0FkPdaqIXY46U6FVh_6r4JMgYrYNwGgFrGZHc
curl -H "Authorization: Bearer ${JWTOKEN}" http://127.0.0.1:8000/api/token/alumnes/dades/
#Resposta: 
{"grup":"SMX2A","datanaixement":"13/5/2004","telefon":"","responsables":
[{"nom":"Ganchozo Risco, Miriam Graciela","mail":"keylu5810@hotmail.com","tfn":""},
{"nom":"","mail":"","tfn":""}],"adreça":"CR Pere III 62  ESC. C 1er 1era , Figueres"}


#Demanar sortides d'un alumne
curl -H "Authorization: Bearer ${JWTOKEN}" http://127.0.0.1:8000/api/token/sortides/
#Resposta: 
[{"id":62,"titol":"BATALLA DE L'EBRE","data":"2024-11-12 06:00:00","pagament":true,"realitzat":true},
{"id":111,"titol":"Ciència Sorprenent","data":"2024-11-11 11:00:00","pagament":false,"realitzat":false},
{"id":136,"titol":"COM COMENÇA TOT  4ESO C i PS","data":"2024-11-06 13:40:00","pagament":false,"realitzat":false},
{"id":89,"titol":"MATFESTA-PARADES","data":"2024-10-25 08:20:00","pagament":false,"realitzat":false},
{"id":51,"titol":"English let's go","data":"2024-10-03 08:10:00","pagament":false,"realitzat":false},
{"id":58,"titol":"VIATGE DE FINAL D'ETAPA","data":"2024-09-25 00:00:00","pagament":true,"realitzat":true},
{"id":20,"titol":"ESO4 Convivència La Vajol","data":"2024-09-18 08:30:00","pagament":false,"realitzat":false}]

#Demanar detall d'una sortida concreta d'un alumne
curl -H "Authorization: Bearer ${JWTOKEN}" http://127.0.0.1:8000/api/token/sortides/455/
# On 455 és l'identificador de la sortida
#Resposta: 
[{"titol":"BATALLA DE L'EBRE","desde":"12/11/2024 06:00","finsa":"13/11/2024 21:00",
"programa":"Sortida per treballar la Guerra Civil Espanyola, en concret en espais on e",
preu":"53.00", "dataLimitPagament":"2024-10-31 23:59:00","realitzat":true,"idPagament":2144}]

#Enllaç d'entrada a la Webview per a realitzar pagament d'una sortida
curl -H "Authorization: Bearer ${JWTOKEN}" https://127.0.0.1:8000/sortides/pagoOnlineApi/4297/
# On 4297 és l'identificador del pagament
#Retorna la pàgina html amb les dades del pagament per anar al TPV



$# ------------------- Altres proves ------------------------------
#Prova accedir sense el token
$
$ curl http://127.0.0.1:8000/api/token/notificacions/news/
{"detail":"Authentication credentials were not provided."}



# token refresh
curl -X POST -H "Content-Type: application/json" -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"}' http://localhost:8000/api-token-refresh/
#Resposta:
{"access":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIzNTYyOTcsImVtYWlsIjoiIiwib3JpZ19pYXQiOjE2NzIzNTU5Njd9.DdyS8X4XMJ7O8cpCYMRjhtGbbL6QJu72vesWr36