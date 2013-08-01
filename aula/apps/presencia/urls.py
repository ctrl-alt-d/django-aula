from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('aula.apps.presencia.views',
    url(r'^regeneraImpartir/$', 'regeneraImpartir', 
        name="administracio__sincronitza__regenerar_horaris" ),
                       
    url(r'^mostraImpartir/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'mostraImpartir', 
        name="aula__horari__horari" ),
                       
    url(r'^mostraImpartir/$', 'mostraImpartir', { 'year':None, 'month': None, 'day': None }, 
        name="aula__horari__horari" ),
                       
    url(r'^passaLlista/(?P<pk>\d+)/$', 'passaLlista', 
        name="aula__horari__passa_llista" ),
                       
    url(r'^afegeixAlumnesLlista/(?P<pk>\d+)/$', 'afegeixAlumnesLlista', 
        name="aula__horari__afegir_alumnes" ),
                       
    url(r'^marcarComHoraSenseAlumnes/(?P<pk>\d+)/$', 'marcarComHoraSenseAlumnes', 
        name="aula__horari__hora_sense_alumnes" ),
                       
    url(r'^treuAlumnesLlista/(?P<pk>\d+)/$', 'treuAlumnesLlista', 
        name="aula__horari__treure_alumnes" ),
                       
    url(r'^afegeixGuardia/(?P<dia>\d+)/(?P<mes>\d+)/(?P<year>\d{4})/$', 'afegeixGuardia', 
        name="aula__horari__afegir_guardia" ),
                       
    url(r'^esborraGuardia/(?P<pk>\d+)/$', 'esborraGuardia', 
        name="aula__horari__esborrar_guardia" ),
                       
    url(r'^calculadoraUnitatsFormatives/$', 'calculadoraUnitatsFormatives', 
        name="aula__materies__calculadora_uf" ),
                       
    url(r'^alertaAssistencia/$', 'alertaAssistencia', 
        name="coordinacio_alumnes__assistencia_alertes__llistat" ),  
                       
    url(r'^faltesAssistenciaEntreDates/$', 'faltesAssistenciaEntreDates', 
        name="aula__materies__assistencia_llistat_entre_dates" ),  

    url(r'^passaLlistaGrupDataTriaGrupDia/$', 'passaLlistaGrupDataTriaGrupDia', 
        name="coordinacio_alumnes__presencia__passa_llista_a_un_grup_tria" ),  
                       
    url(r'^passaLlistaGrupData/(?P<grup>\d+)/(?P<dia>\d+)/(?P<mes>\d+)/(?P<year>\d{4})/$', 'passaLlistaGrupData', 
        name="coordinacio_alumnes__presencia__passa_llista_a_un_grup_resultats" ),

    
)

