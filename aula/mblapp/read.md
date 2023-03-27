# Exemples crides a la API

```bash
#Fase 0: Li passem el token inicial. TODO: usuari -> username, demanar data naixement
export INITIALTOKEN="d790dca6-dcd0-4f73-8f78-07d6e2713aa8"
curl -X POST -H "Content-Type: application/json" -d "{\"clau\":\"${INITIALTOKEN}\" }" http://localhost:8000/mblapp/capture_token_api/
#Ex resposta: {"password":"BvZeRaQGQrL4","usuari":"5C9n"}
#Fase 1: Posar l'usuari a estat actiu ( a mà ho farà el professor per UI ):
$ python manage.py shell
>>> from django.contrib.auth.models import User
>>> u=User.objects.get(username ="5C9n")
>>> u.is_active = True
>>> u.save()
#Fase 2: Prova de demanar un token per accedir-hi
$
$ curl -X POST -H "Content-Type: application/json" -d '{"username":"5C9n","password":"BvZeRaQGQrL4"}' http://localhost:8000/api-token-auth/{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ik0xIiwidXNlcl9pZCI6NCwiZW1haWwiOiIiLCJleHAiOjE1MjU5NjA5MjR9.EKEhsW-uqdblRLEpAH0uxKMb-FUnCJB6a3_3xRd4Pno"}
#Fase 3: Prova accedir a recurs amb el token
$
$ curl -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ik0xIiwidXNlcl9pZCI6NCwiZW1haWwiOiIiLCJleHAiOjE1MjU5NjA5MjR9.EKEhsW-uqdblRLEpAH0uxKMb-FUnCJB6a3_3xRd4Pno" http://127.0.0.1:8000/mblapp/hello_api_login/
{"status":"here we are"}
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