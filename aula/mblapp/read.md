# Exemples crides a la API

```bash
$ #demano un token
$
$ curl -X POST -H "Content-Type: application/json" -d '{"username":"M1","password":"djAu"}' http://localhost:8000/api-token-auth/
{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ik0xIiwidXNlcl9pZCI6NCwiZW1haWwiOiIiLCJleHAiOjE1MjU5NjA5MjR9.EKEhsW-uqdblRLEpAH0uxKMb-FUnCJB6a3_3xRd4Pno"}
$ #accedeixo a recurs amb el token
$
$ curl -H "Authorization: JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6Ik0xIiwidXNlcl9pZCI6NCwiZW1haWwiOiIiLCJleHAiOjE1MjU5NjA5MjR9.EKEhsW-uqdblRLEpAH0uxKMb-FUnCJB6a3_3xRd4Pno" http://127.0.0.1:8000/mblapp/hello_api_login/
{"status":"here we are"}
$ #provo sense el token
$
$ curl http://127.0.0.1:8000/mblapp/hello_api_login/
{"detail":"Authentication credentials were not provided."}
Tens, si vols, una url que no demana autenticació:
$ #sense auth
$
$ curl http://127.0.0.1:8000/mblapp/hello_api/
{"status":"here we are"}
```