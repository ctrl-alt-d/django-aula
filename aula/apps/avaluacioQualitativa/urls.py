from django.urls import re_path
from aula.apps.avaluacioQualitativa import views as avaluacioQualitativa_views

urlpatterns = [
   re_path(r'^items/$', avaluacioQualitativa_views.items,
    name="coordinacio_pedagogica__qualitativa__items"),
                       
   re_path(r'^avaluacions/$', avaluacioQualitativa_views.avaluacionsQualitatives,
    name="coordinacio_pedagogica__qualitativa__avaluacions"),
                       
   re_path(r'^lesMevesAvaluacionsQualitatives/$', avaluacioQualitativa_views.lesMevesAvaluacionsQualitatives,
    name="aula__qualitativa__les_meves_avaulacions_qualitatives"),
                       
   re_path(r'^entraQualitativa/(?P<qualitativa_pk>\d+)/(?P<assignatura_pk>\d+)/(?P<grup_pk>\d+)/$', avaluacioQualitativa_views.entraQualitativa,
    name="aula__qualitativa__entra_qualitativa"),
                       
   re_path(r'^resultats/$', avaluacioQualitativa_views.resultats,
    name="coordinacio_pedagogica__qualitativa__resultats_qualitatives"),
                       
   re_path(r'^report/(?P<pk>\d+)$', avaluacioQualitativa_views.report,
    name="coordinacio_pedagogica__qualitativa__report"),
 
   re_path(r'^blanc/$', avaluacioQualitativa_views.blanc,
    name="coordinacio_pedagogica__qualitativa__blanc"),
                       
]

