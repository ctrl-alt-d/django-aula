from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('aula.apps.relacioFamilies.views',
    url(r'^elMeuInforme/$', 'elMeuInforme', 
        name='relacio_families__informe__el_meu_informe'),
                       
    url(r'^elMeuInforme/(?P<pk>\d+)/$', 'elMeuInforme',
        name="relacio_families__informe__el_meu_informe"),
    
    url(r'^dadesRelacioFamilies/$', 'dadesRelacioFamilies',
        name="tutoria__relacio_families__dades_relacio_families"),
    
    url(r'^configuraConnexio/(?P<pk>\d+)/$', 'configuraConnexio',
        name="tutoria__relacio_families___configura_connexio"), 
      
    url(r'^bloquejaDesbloqueja/(?P<pk>\d+)/$', 'bloquejaDesbloqueja',
        name="tutoria__relacio_families__bloqueja_desbloqueja"), 
      
    url(r'^enviaBenvinguda/(?P<pk>\d+)/$', 'enviaBenvinguda',
        name="tutoria__relacio_families__envia_benvinguda"),
    
    url(r'^canviParametres/$', 'canviParametres',
        name="relacio_families__configuracio__canvi_parametres"),         
)