# Actualitza

Cada inici de curs s'ha de preparar el Djau amb les noves dades necessàries. Es pot fer una [instal·lació nova](../instalacion-2/instalacion.md) o mantenir l'actual i actualitzar-la.

Primer actualitzem el sistema:

```bash
sudo su
apt-get update
apt-get upgrade
```

A continuació el Djau, és convenient fer una còpia de la carpeta del Djau i de la base de dades:

```bash
sudo su
systemctl stop apache2
zip -r copiaDjau.zip /opt/djau
pg_dump -U djauser -f djau-20230410.pgsql basededadesDjau
```

Actualitzem codi, entorn virtual python i base de dades:

```bash
sudo su
systemctl stop apache2
cd /opt/djau
git pull
source venv/bin/activate
pip install --upgrade --no-cache-dir -r requirements.txt
python manage.py migrate
python manage.py collectstatic -c --no-input
deactivate
```

Finalment s'activa el servidor web i es comprova el funcionament:

```bash
sudo su
systemctl start apache2
```
