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


#Fase 7: Demanar activitats i pagaments corresponents a l'alumne
export JWTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIzNTQ0OTUsImVtYWlsIjoiIn0.2pgU5g0FkPdaqIXY46U6FVh_6r4JMgYrYNwGgFrGZHc
curl -H "Authorization: Bearer ${JWTOKEN}" http://127.0.0.1:8000/api/token/alumnes/activitats/
#Resposta: 
[{"id":214,"darrera_sincronitzacio":null},
{"tipus":"A","titol":"2n ESO A Xerrada Mossos \"Comença el Joc\"","data-inici":"01.02.2024 11:25:00","data-fi":"01.02.2024 12:20:00","descripcio":"Enguany els Mossos d'Esquadra...","condicions-generals":"","tipus-pagament":"NO","preu":"0","termini":"","forma-pagament":"","comentari":"","pagat":""},
{"tipus":"P","titol":"2n ESO Tecnologia: Kit material elèctric","data-inici":"20.12.2023 23:59:00","data-fi":"17.12.2023 23:59:00","descripcio":"Durant el segon trimestre, des ...","condicions-generals":"Data límit per realitzar ...","tipus-pagament":"ON","preu":"6.40","termini":"20.12.2023 23:59:00","forma-pagament":"El pagament s'ha de realitzar ...,"comentari":"","pagat":"SI"}
]


#Fase 8: Realitzar un pagament a través del mòbil
export JWTOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIzNTQ0OTUsImVtYWlsIjoiIn0.2pgU5g0FkPdaqIXY46U6FVh_6r4JMgYrYNwGgFrGZHc
export CODI_PAGAMENT="4294"
export DATA_HORA_PAGAMENT="2024-03-18 12:00:13"
export ORDRE_PAGAMENT="11240004294"
curl -H "Authorization: Bearer ${JWTOKEN}" -d "{\"codi_pagament\":\"${CODI_PAGAMENT}\",\"data_hora_pagament\":\"${DATA_HORA_PAGAMENT}\", \"ordre_pagament\":\"${ORDRE_PAGAMENT}\"  }" http://127.0.0.1:8000/api/token/alumnes/pagat/

#Resposta: 
{"pagament_guardat":"True"}


$# ------------------- Altres proves ------------------------------
#Prova accedir sense el token
$
$ curl http://127.0.0.1:8000/api/token/notificacions/news/
{"detail":"Authentication credentials were not provided."}



# token refresh
curl -X POST -H "Content-Type: application/json" -d '{"refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX3BrIjoxLCJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImNvbGRfc3R1ZmYiOiLimIMiLCJleHAiOjIzNDU2NywianRpIjoiZGUxMmY0ZTY3MDY4NDI3ODg5ZjE1YWMyNzcwZGEwNTEifQ.aEoAYkSJjoWH1boshQAaTkf8G3yn0kapko6HFRt7Rh4"}' http://localhost:8000/api-token-refresh/
#Resposta:
{"access":"eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxMjEzLCJ1c2VybmFtZSI6IkFQSW0zd2kiLCJleHAiOjE2NzIzNTYyOTcsImVtYWlsIjoiIiwib3JpZ19pYXQiOjE2NzIzNTU5Njd9.DdyS8X4XMJ7O8cpCYMRjhtGbbL6QJu72vesWr36