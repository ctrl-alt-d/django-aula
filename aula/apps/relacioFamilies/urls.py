from django.urls import re_path, path
from aula.apps.relacioFamilies import views as relacioFamilies_views

urlpatterns = [
    re_path(r'^elMeuInforme/$', relacioFamilies_views.elMeuInforme,
        name='relacio_families__informe__el_meu_informe'),
                       
    re_path(r'^dadesRelacioFamilies/$', relacioFamilies_views.dadesRelacioFamilies,
        name="tutoria__relacio_families__dades_relacio_families"),
    
    re_path(r'^configuraConnexio/(?P<pk>\d+)/$', relacioFamilies_views.configuraConnexio,
            name="tutoria__relacio_families___configura_connexio"),

    re_path(r'^qrTokens/(?P<pk>\d+)/$', relacioFamilies_views.qrTokens,
            name="tutoria__relacio_families___qr_tokens"),

    re_path(r'^qrTokens/$', relacioFamilies_views.qrTokens,
            name="tutoria__relacio_families___qr_tokens_all"),
    re_path(r'^qrs/$', relacioFamilies_views.qrs,
            name="tutoria__relacio_families__qrs"),
    re_path(r'^gestionaQRs/(?P<pk>\d+)/$', relacioFamilies_views.gestionaQRs,
            name="tutoria__relacio_families__gestionaQRs"),

    re_path(r'^bloquejaDesbloqueja/(?P<pk>\d+)/$', relacioFamilies_views.bloquejaDesbloqueja,
        name="tutoria__relacio_families__bloqueja_desbloqueja"), 
      
    re_path(r'^enviaBenvinguda/(?P<pk>\d+)/$', relacioFamilies_views.enviaBenvinguda,
        name="tutoria__relacio_families__envia_benvinguda"),
    
    re_path(r'^elMeuInforme/(?P<pk>\d+)/$', relacioFamilies_views.elMeuInforme,
        name="relacio_families__informe__el_meu_informe"),
    
    re_path(r'^canviParametres/$', relacioFamilies_views.canviParametres,
        name="relacio_families__configuracio__canvi_parametres"),         
    
    path('blanc/', relacioFamilies_views.blanc, name="relacio_families__comunicats__blanc"),
    
    path('comunicat/', relacioFamilies_views.comunicatAbsencia, name="relacio_families__comunicats__absencia"),
    
    path('anteriors/', relacioFamilies_views.comunicatsAnteriors, name="relacio_families__comunicats__anteriors"),
    
    path('horesAlumneAjax/<idalumne>/<dia>/', relacioFamilies_views.horesAlumneAjax,
        name="relacio_families__horesAlumneAjax"),
]