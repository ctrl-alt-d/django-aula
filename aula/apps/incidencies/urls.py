from django.conf.urls import url
from aula.apps.incidencies import views as incidencies_views

urlpatterns = [
                       
    url(r'^posaIncidenciaAula/(?P<pk>\d+)/$', incidencies_views.posaIncidenciaAula,
        name="aula__horari__posa_incidencia"),
                       
    url(r'^posaIncidencia/$', incidencies_views.posaIncidencia,
        name="aula__incidencies__posa_incidencia"),

    url(r'^posaIncidenciaprimerahora/$', incidencies_views.posaIncidenciaPrimeraHora,
        name="gestio__incidencia__onbehalf"),
                       
    url(r'^posaExpulsio/$', incidencies_views.posaExpulsio,
        name="aula__incidencies__posa_expulsio"),
                       
    url(r'^posaExpulsioW2/(?P<pk>\d+)/$', incidencies_views.posaExpulsioW2,
        name="aula__incidencies__posa_expulsio_w2"),
                       
    url(r'^posaExpulsioPerAcumulacio/(?P<pk>\d+)/$', incidencies_views.posaExpulsioPerAcumulacio,
        name="aula__incidencies__posa_expulsio_per_acumulacio"),
                       
    url(r'^sancio/(?P<pk>\d+)/$', incidencies_views.sancio,
        name="coordinacio_alumnes__sancions__sancionar"),
                       
    url(r'^editaExpulsio/(?P<pk>\d+)/$', incidencies_views.editaExpulsio,
        name="aula__incidencies__edita_expulsio"),
                       
    url(r'^eliminaIncidenciaAula/(?P<pk>\d+)/$', incidencies_views.eliminaIncidenciaAula,
        name="aula__horari__elimina_incidencia"),
                       
    url(r'^eliminaIncidencia/(?P<pk>\d+)/$', incidencies_views.eliminaIncidencia,
        name="aula__incidencies__elimina_incidencia"),
                       
    url(r'^llistaIncidenciesProfessional/$', incidencies_views.llistaIncidenciesProfessional,
        name="aula__incidencies__les_meves_incidencies"),
                       
    url(r'^alertesAcumulacioExpulsions/$', incidencies_views.alertesAcumulacioExpulsions,
        name="coordinacio_alumnes__ranking__list"),
    
    url(r'^sancio/(?P<pk>\d+)/$', incidencies_views.sancio,
        name="coordinacio_alumnes__sancions__sancionar"),
    
    url(r'^sancions/$', incidencies_views.sancions,
        name="coordinacio_alumnes__sancions__sancions"),

    url(r'^sancions/(?P<s>\w+)/$', incidencies_views.sancions,
        name="coordinacio_alumnes__sancions__sancions"),

    url(r'^sancionsExcel/$', incidencies_views.sancionsExcel,
        name="coordinacio_alumnes__sancions__sancions_excel"),

    url(r'^editaSancio/(?P<pk>\d+)/$', incidencies_views.editaSancio,
        name="coordinacio_alumnes__sancions__edicio"),

    url(r'^esborrarSancio/(?P<pk>\d+)/$', incidencies_views.esborrarSancio,
        name="coordinacio_alumnes__sancions__esborrar"),

    url(r'^controlTramitacioExpulsions/$', incidencies_views.controlTramitacioExpulsions,
        name="professorat__expulsions__control_tramitacio"),
                                              
    url(r'^cartaSancio/(?P<pk>\d+)/$', incidencies_views.cartaSancio,
        name="coordinacio_alumnes__sancions__carta"),
                       
    url(r'^blanc/$', incidencies_views.blanc,
        name="aula__incidencies__blanc"),
   
                       
    
]

