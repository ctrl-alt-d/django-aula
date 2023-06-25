from django.urls import re_path
from aula.apps.importaActuacions import views as importaActuacions_views

urlpatterns = [
    re_path(r'^connexioDB/$', importaActuacions_views.connexioDBold ,
       name="importaActuacions__connexio__DB"),
    re_path(r'^sincronitzaProfessionals/$', importaActuacions_views.sincronitzaProfessionals ,
       name="importaActuacions__sincronitzaProfessionals"),
    re_path(r'^importantActuacions/$', importaActuacions_views.importantActuacions ,
       name="importaActuacions__importa__actuacions"),
    re_path(r'^resultatImportacio/$', importaActuacions_views.importacio ,
       name="importaActuacions__resultat__importacio"),
]