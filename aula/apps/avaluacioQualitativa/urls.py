from django.conf.urls.defaults import patterns,url

urlpatterns = patterns('aula.apps.avaluacioQualitativa.views',
   url(r'^items/$', 'items',
    name="coordinacio_pedagogica__qualitativa__items"),
                       
   url(r'^avaluacions/$', 'avaluacionsQualitatives',
    name="coordinacio_pedagogica__qualitativa__avaluacions"),
                       
   url(r'^lesMevesAvaluacionsQualitatives/$', 'lesMevesAvaluacionsQualitatives',
    name="aula__qualitativa__les_meves_avaulacions_qualitatives"),
                       
   url(r'^entraQualitativa/(?P<qualitativa_pk>\d+)/(?P<assignatura_pk>\d+)/(?P<grup_pk>\d+)/$', 'entraQualitativa',
    name="aula__qualitativa__entra_qualitativa"),
                       
   url(r'^resultats/$', 'resultats',
    name="coordinacio_pedagogica__qualitativa__resultats_qualitatives"),
                       
   url(r'^report/(?P<pk>\d+)$', 'report',
    name="coordinacio_pedagogica__qualitativa__report"),
 
   url(r'^blanc/$', 'blanc',
    name="coordinacio_pedagogica__qualitativa__blanc"),
                       
)

