#encoding: utf-8
# Cal descarregar el driver de gecko (mozilla) segons el teu sistema, per executar els tests basats en Selenium.
# (documentació) https://pypi.org/project/selenium/
# (Software) https://github.com/mozilla/geckodriver/releases

import subprocess
driver = subprocess.check_output("whereis -b geckodriver", shell=True)
camps = driver.decode('utf-8').split(' ')
if len(camps) <= 1:
  #instala driver
  resultat = subprocess.call("wget https://github.com/mozilla/geckodriver/releases/download/v0.23.0/geckodriver-v0.23.0-linux64.tar.gz --directory-prefix=/tmp/", shell=True)
  if resultat != 0:
    raise Exception("Error al descarregar de la web")
  print ("Executa això: sudo tar -xzvf /tmp/geckodriver-v0.23.0-linux64.tar.gz --directory=/tmp/ && cp /tmp/geckodriver /usr/local/bin/")
else:
  subprocess.call("python manage.py test aula.apps.presencia.tests --keepdb", shell=True)  










