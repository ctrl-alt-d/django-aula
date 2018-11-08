from django.conf.urls import url
from aula.apps.extEsfera.views import sincronitzaEsfera,assignaGrups

urlpatterns = [
   url(r'^sincronitzaEsfera/$', sincronitzaEsfera,
       name="administracio__sincronitza__esfera"),
                       
   url(r'^assignaGrups/$', assignaGrups,
       name="administracio__configuracio__assigna_grups_esfera"),
                       
]

