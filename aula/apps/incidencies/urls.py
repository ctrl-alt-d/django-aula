from django.urls import re_path
from aula.apps.incidencies import views as incidencies_views

urlpatterns = [
                       
    re_path(r'^posaIncidenciaAula/(?P<pk>\d+)/$', incidencies_views.posaIncidenciaAula,
        name="aula__horari__posa_incidencia"),
                       
    re_path(r'^posaIncidencia/$', incidencies_views.posaIncidencia,
        name="aula__incidencies__posa_incidencia"),

    re_path(r'^posaIncidenciaprimerahora/$', incidencies_views.posaIncidenciaPrimeraHora,
        name="consergeria__incidencia__onbehalf"),
                       
    re_path(r'^posaExpulsio/$', incidencies_views.posaExpulsio,
        name="aula__incidencies__posa_expulsio"),
                       
    re_path(r'^posaExpulsioW2/(?P<pk>\d+)/$', incidencies_views.posaExpulsioW2,
        name="aula__incidencies__posa_expulsio_w2"),
                       
    re_path(r'^posaExpulsioPerAcumulacio/(?P<pk>\d+)/$', incidencies_views.posaExpulsioPerAcumulacio,
        name="aula__incidencies__posa_expulsio_per_acumulacio"),
                       
    re_path(r'^sancio/(?P<pk>\d+)/$', incidencies_views.sancio,
        name="coordinacio_alumnes__sancions__sancionar"),
                       
    re_path(r'^editaExpulsio/(?P<pk>\d+)/$', incidencies_views.editaExpulsio,
        name="aula__incidencies__edita_expulsio"),
                       
    re_path(r'^eliminaIncidenciaAula/(?P<pk>\d+)/$', incidencies_views.eliminaIncidenciaAula,
        name="aula__horari__elimina_incidencia"),
                       
    re_path(r'^eliminaIncidencia/(?P<pk>\d+)/$', incidencies_views.eliminaIncidencia,
        name="aula__incidencies__elimina_incidencia"),
                       
    re_path(r'^llistaIncidenciesProfessional/$', incidencies_views.llistaIncidenciesProfessional,
        name="aula__incidencies__les_meves_incidencies"),
                       
    re_path(r'^alertesAcumulacioExpulsions/$', incidencies_views.alertesAcumulacioExpulsions,
        name="coordinacio_alumnes__ranking__list"),
    
    re_path(r'^sancio/(?P<pk>\d+)/$', incidencies_views.sancio,
        name="coordinacio_alumnes__sancions__sancionar"),
    
    re_path(r'^sancions/$', incidencies_views.sancions,
        name="coordinacio_alumnes__sancions__sancions"),

    re_path(r'^sancions/(?P<s>\w+)/$', incidencies_views.sancions,
        name="coordinacio_alumnes__sancions__sancions"),

    re_path(r'^sancionsExcel/$', incidencies_views.sancionsExcel,
        name="coordinacio_alumnes__sancions__sancions_excel"),

    re_path(r'^editaSancio/(?P<pk>\d+)/$', incidencies_views.editaSancio,
        name="coordinacio_alumnes__sancions__edicio"),

    re_path(r'^esborrarSancio/(?P<pk>\d+)/$', incidencies_views.esborrarSancio,
        name="coordinacio_alumnes__sancions__esborrar"),

    re_path(r'^controlTramitacioExpulsions/$', incidencies_views.controlTramitacioExpulsions,
        name="professorat__expulsions__control_tramitacio"),
                                              
    re_path(r'^cartaSancio/(?P<pk>\d+)/$', incidencies_views.cartaSancio,
        name="coordinacio_alumnes__sancions__carta"),
                       
    re_path(r'^blanc/$', incidencies_views.blanc,
        name="aula__incidencies__blanc"),
   
                       
    
]

