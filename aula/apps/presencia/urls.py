from django.conf.urls import url
from aula.apps.presencia import views as presencia_views

urlpatterns = [
    url(r'^regeneraImpartir/$', presencia_views.regeneraImpartir,
        name="administracio__sincronitza__regenerar_horaris" ),
                       
    url(r'^mostraImpartir/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', presencia_views.mostraImpartir,
        name="aula__horari__horari" ),
                       
    url(r'^mostraImpartir/$', presencia_views.mostraImpartir, { 'year':None, 'month': None, 'day': None },
        name="aula__horari__horari" ),
                       
    url(r'^passaLlista/(?P<pk>\d+)/$', presencia_views.passaLlista,
        name="aula__horari__passa_llista" ),
                       
    url(r'^afegeixAlumnesLlista/(?P<pk>\d+)/$', presencia_views.afegeixAlumnesLlista,
        name="aula__horari__afegir_alumnes" ),
                       
    url(r'^copiarAlumnesLlista/(?P<pk>\d+)/$', presencia_views.copiarAlumnesLlista,
        name="aula__horari__copiar_alumnes" ),
                       
    url(r'^marcarComHoraSenseAlumnes/(?P<pk>\d+)/$', presencia_views.marcarComHoraSenseAlumnes,
        name="aula__horari__hora_sense_alumnes" ),
                       
    url(r'^treuAlumnesLlista/(?P<pk>\d+)/$', presencia_views.treuAlumnesLlista,
        name="aula__horari__treure_alumnes" ),
                       
    url(r'^afegeixGuardia/(?P<dia>\d+)/(?P<mes>\d+)/(?P<year>\d{4})/$', presencia_views.afegeixGuardia,
        name="aula__horari__afegir_guardia" ),
                       
    url(r'^esborraGuardia/(?P<pk>\d+)/$', presencia_views.esborraGuardia,
        name="aula__horari__esborrar_guardia" ),
                       
    url(r'^calculadoraUnitatsFormatives/$', presencia_views.calculadoraUnitatsFormatives,
        name="aula__materies__calculadora_uf" ),
                       
    url(r'^alertaAssistencia/$', presencia_views.alertaAssistencia,
        name="coordinacio_alumnes__assistencia_alertes__llistat" ),  
                       
    url(r'^faltesAssistenciaEntreDates/$', presencia_views.faltesAssistenciaEntreDates,
        name="aula__materies__assistencia_llistat_entre_dates" ),  

    url(r'^passaLlistaGrupDataTriaGrupDia/$', presencia_views.passaLlistaGrupDataTriaGrupDia,
        name="coordinacio_alumnes__presencia__passa_llista_a_un_grup_tria" ),  
                       
    url(r'^passaLlistaGrupData/(?P<grup>\d+)/(?P<dia>\d+)/(?P<mes>\d+)/(?P<year>\d{4})/$', presencia_views.passaLlistaGrupData,
        name="coordinacio_alumnes__presencia__passa_llista_a_un_grup_resultats" ),

    url(r'^anularImpartir/(?P<pk>\d+)/$', presencia_views.anularImpartir,
       name="aula__horari__anularImpartir"),

    url(r'^desanularImpartir/(?P<pk>\d+)/$', presencia_views.desanularImpartir,
       name="aula__horari__desanularImpartir"),

]


