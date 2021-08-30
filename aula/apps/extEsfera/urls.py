from django.conf.urls import url
from aula.apps.extEsfera.views import sincronitzaEsfera,assignaGrups,dadesAddicionals

urlpatterns = [
   url(r'^sincronitzaEsfera/$', sincronitzaEsfera,
       name="administracio__sincronitza__esfera"),
                       
   url(r'^assignaGrups/$', assignaGrups,
       name="administracio__configuracio__assigna_grups_esfera"),

    url(r'^dadesAddicionals/$', dadesAddicionals,
       name="administracio__sincronitza__dades_addicionals"),
                       
]

