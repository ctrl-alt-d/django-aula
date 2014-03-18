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
                       
    url(r'^sancio/(?P<pk>\d+)/$', 'sancio',
        name="coordinacio_alumnes__sancions__sancionar"),
                       
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
    
    url(r'^sancio/(?P<pk>\d+)/$', 'sancio',
        name="coordinacio_alumnes__sancions__sancionar"),
    
    url(r'^sancions/$', 'sancions',
        name="coordinacio_alumnes__sancions__sancions"),

    url(r'^sancions/(?P<s>\w+)/$', 'sancions',
        name="coordinacio_alumnes__sancions__sancions"),

    url(r'^sancionsExcel/$', 'sancionsExcel',
        name="coordinacio_alumnes__sancions__sancions_excel"),

    url(r'^editaSancio/(?P<pk>\d+)/$', 'editaSancio',
        name="coordinacio_alumnes__sancions__edicio"),

    url(r'^esborrarSancio/(?P<pk>\d+)/$', 'esborrarSancio',
        name="coordinacio_alumnes__sancions__esborrar"),

    url(r'^controlTramitacioExpulsions/$', 'controlTramitacioExpulsions', 
        name="coordinacio_alumnes__expulsions__control_tramitacio"),
                                              
    url(r'^cartaSancio/(?P<pk>\d+)/$', 'cartaSancio', 
        name="coordinacio_alumnes__sancions__carta"),
                       
    url(r'^blanc/$', 'blanc',
        name="aula__incidencies__blanc"),
   
                       
    
)

