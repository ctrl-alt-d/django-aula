from django.urls import re_path
from aula.apps.extEsfera.views import sincronitzaEsfera,assignaGrups,dadesAddicionals

urlpatterns = [
   re_path(r'^sincronitzaEsfera/$', sincronitzaEsfera,
       name="administracio__sincronitza__esfera"),
                       
   re_path(r'^assignaGrups/$', assignaGrups,
       name="administracio__configuracio__assigna_grups_esfera"),

    re_path(r'^dadesAddicionals/$', dadesAddicionals,
       name="administracio__sincronitza__dades_addicionals"),
                       
]

