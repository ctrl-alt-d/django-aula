from django.conf.urls import url
from aula.apps.avaluacioQualitativa import views as avaluacioQualitativa_views

urlpatterns = [
   url(r'^items/$', avaluacioQualitativa_views.items,
    name="coordinacio_pedagogica__qualitativa__items"),
                       
   url(r'^avaluacions/$', avaluacioQualitativa_views.avaluacionsQualitatives,
    name="coordinacio_pedagogica__qualitativa__avaluacions"),
                       
   url(r'^lesMevesAvaluacionsQualitatives/$', avaluacioQualitativa_views.lesMevesAvaluacionsQualitatives,
    name="aula__qualitativa__les_meves_avaulacions_qualitatives"),
                       
   url(r'^entraQualitativa/(?P<qualitativa_pk>\d+)/(?P<assignatura_pk>\d+)/(?P<grup_pk>\d+)/$', avaluacioQualitativa_views.entraQualitativa,
    name="aula__qualitativa__entra_qualitativa"),
                       
   url(r'^resultats/$', avaluacioQualitativa_views.resultats,
    name="coordinacio_pedagogica__qualitativa__resultats_qualitatives"),
                       
   url(r'^report/(?P<pk>\d+)$', avaluacioQualitativa_views.report,
    name="coordinacio_pedagogica__qualitativa__report"),
 
   url(r'^blanc/$', avaluacioQualitativa_views.blanc,
    name="coordinacio_pedagogica__qualitativa__blanc"),
                       
]

