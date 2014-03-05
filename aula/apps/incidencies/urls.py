from django.conf.urls.defaults import patterns,url

urlpatterns = patterns('aula.apps.incidencies.views',
                       
    url(r'^posaIncidenciaAula/(?P<pk>\d+)/$', 'posaIncidenciaAula',
        name="aula__horari__posa_incidencia"),
                       
    url(r'^posaIncidencia/$', 'posaIncidencia',
        name="aula__incidencies__posa_incidencia"),
                       
    url(r'^posaExpulsio/$', 'posaExpulsio',
        name="aula__incidencies__posa_expulsio"),
                       
    url(r'^posaExpulsioW2/(?P<pk>\d+)/$', 'posaExpulsioW2',
        name="aula__incidencies__posa_expulsio_w2"),
                       
    url(r'^posaExpulsioPerAcumulacio/(?P<pk>\d+)/$', 'posaExpulsioPerAcumulacio',
        name="aula__incidencies__posa_expulsio_per_acumulacio"),
                       
    url(r'^expulsioDelCentre/(?P<pk>\d+)/$', 'expulsioDelCentre',
        name="coordinacio_alumnes__explusions_centre__expulsio"),
                       
    url(r'^editaExpulsio/(?P<pk>\d+)/$', 'editaExpulsio',
        name="aula__incidencies__edita_expulsio"),
                       
    url(r'^eliminaIncidenciaAula/(?P<pk>\d+)/$', 'eliminaIncidenciaAula',
        name="aula__horari__elimina_incidencia"),
                       
    url(r'^eliminaIncidencia/(?P<pk>\d+)/$', 'eliminaIncidencia',
        name="aula__incidencies__elimina_incidencia"),
                       
    url(r'^llistaIncidenciesProfessional/$', 'llistaIncidenciesProfessional',
        name="aula__incidencies__les_meves_incidencies"),
                       
    url(r'^alertesAcumulacioExpulsions/$', 'alertesAcumulacioExpulsions',
        name="coordinacio_alumnes__ranking__list"),
                       
    url(r'^expulsioDelCentre/(?P<pk>\d+)/$', 'expulsioDelCentre',
        name="coordinacio_alumnes__explusions_centre__expulsar"),
                       
    url(r'^expulsionsDelCentre/$', 'expulsionsDelCentre',
        name="coordinacio_alumnes__explusions_centre__expulsions"),
                       
    url(r'^expulsionsDelCentre/(?P<s>\w+)/$', 'expulsionsDelCentre',
        name="coordinacio_alumnes__explusions_centre__expulsions"),
                       
    url(r'^expulsionsDelCentreExcel/$', 'expulsionsDelCentreExcel',
        name="coordinacio_alumnes__explusions_centre__expulsions_excel"),
                       
    url(r'^editaExpulsioCentre/(?P<pk>\d+)/$', 'editaExpulsioCentre',
        name="coordinacio_alumnes__explusions_centre__edicio"),
                       
    url(r'^esborrarExpulsioCentre/(?P<pk>\d+)/$', 'esborrarExpulsioCentre',
        name="coordinacio_alumnes__explusions_centre__esborrar"),
                       
    url(r'^controlTramitacioExpulsions/$', 'controlTramitacioExpulsions',
        name="professorat__explusions__control_tramitacio"),
                                              
    url(r'^cartaExpulsioCentre/(?P<pk>\d+)/$', 'cartaExpulsioCentre',
        name="coordinacio_alumnes__explusions_centre__carta"),
                       
    url(r'^blanc/$', 'blanc',
        name="aula__incidencies__blanc"),
   
                       
    
)

