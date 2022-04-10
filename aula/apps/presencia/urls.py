from django.urls import re_path
from aula.apps.presencia import views as presencia_views

urlpatterns = [
    re_path(r'^regeneraImpartir/$', presencia_views.regeneraImpartir,
        name="administracio__sincronitza__regenerar_horaris" ),
                       
    re_path(r'^mostraImpartir/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', presencia_views.mostraImpartir,
        name="aula__horari__horari" ),
                       
    re_path(r'^mostraImpartir/$', presencia_views.mostraImpartir, { 'year':None, 'month': None, 'day': None },
        name="aula__horari__horari" ),
                       
    re_path(r'^passaLlista/(?P<pk>\d+)/$', presencia_views.passaLlista,
        name="aula__horari__passa_llista" ),
                       
    re_path(r'^afegeixAlumnesLlista/(?P<pk>\d+)/$', presencia_views.afegeixAlumnesLlista,
        name="aula__horari__afegir_alumnes" ),
                       
    re_path(r'^copiarAlumnesLlista/(?P<pk>\d+)/$', presencia_views.copiarAlumnesLlista,
        name="aula__horari__copiar_alumnes" ),
                       
    re_path(r'^marcarComHoraSenseAlumnes/(?P<pk>\d+)/$', presencia_views.marcarComHoraSenseAlumnes,
        name="aula__horari__hora_sense_alumnes" ),
                       
    re_path(r'^treuAlumnesLlista/(?P<pk>\d+)/$', presencia_views.treuAlumnesLlista,
        name="aula__horari__treure_alumnes" ),
                       
    re_path(r'^afegeixGuardia/(?P<dia>\d+)/(?P<mes>\d+)/(?P<year>\d{4})/$', presencia_views.afegeixGuardia,
        name="aula__horari__afegir_guardia" ),
                       
    re_path(r'^esborraGuardia/(?P<pk>\d+)/$', presencia_views.esborraGuardia,
        name="aula__horari__esborrar_guardia" ),
                       
    re_path(r'^calculadoraUnitatsFormatives/$', presencia_views.calculadoraUnitatsFormatives,
        name="aula__materies__calculadora_uf" ),
                       
    re_path(r'^alertaAssistencia/$', presencia_views.alertaAssistencia,
        name="coordinacio_alumnes__assistencia_alertes__llistat" ),  
          
    #amorilla@xtec.cat             
    re_path(r'^Indicadors/$', presencia_views.indicadors,
        name="coordinacio_alumnes__indicadors__llistat" ),  

    #amorilla@xtec.cat             
    re_path(r'^indcsv/$', presencia_views.indcsv,
        name="coordinacio_alumnes__indicadors__baixacsv" ),  
                       
    re_path(r'^faltesAssistenciaEntreDates/$', presencia_views.faltesAssistenciaEntreDates,
        name="aula__materies__assistencia_llistat_entre_dates" ),  

    re_path(r'^passaLlistaGrupDataTriaGrupDia/$', presencia_views.passaLlistaGrupDataTriaGrupDia,
        name="coordinacio_alumnes__presencia__passa_llista_a_un_grup_tria" ),  
                       
    re_path(r'^passaLlistaGrupData/(?P<grup>\d+)/(?P<dia>\d+)/(?P<mes>\d+)/(?P<year>\d{4})/$', presencia_views.passaLlistaGrupData,
        name="coordinacio_alumnes__presencia__passa_llista_a_un_grup_resultats" ),

    re_path(r'^anularImpartir/(?P<pk>\d+)/$', presencia_views.anularImpartir,
       name="aula__horari__anularImpartir"),

    re_path(r'^desanularImpartir/(?P<pk>\d+)/$', presencia_views.desanularImpartir,
       name="aula__horari__desanularImpartir"),

    re_path(r'^winwheel/(?P<pk>\d+)/$', presencia_views.winwheel,
        name="aula__horari__winwheel" ),
                       

]


