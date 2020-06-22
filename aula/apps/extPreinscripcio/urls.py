from django.conf.urls import url
from aula.apps.extPreinscripcio.views import importaFitxer

urlpatterns = [
   url(r'^importa/$', importaFitxer,
       name="administracio__sincronitza__preinscripcio"),

]
