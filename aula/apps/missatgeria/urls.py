
from django.conf.urls import patterns, url

urlpatterns = patterns('aula.apps.missatgeria.views',
                       
    url(r'^elMeuMur/$', 'elMeuMur', {'pg':1}, 
        name ="varis__elmur__veure" ),
                       
    url(r'^elMeuMur/(?P<pg>\d+)/$', 'elMeuMur', 
        name ="varis__elmur__veure_by_pg" ),
                       
    url(r'^enviaMissatgeTutors/$', 'enviaMissatgeTutors', 
        name ="consergeria__missatges__envia_tutors" ),
                       
    url(r'^enviaMissatgeAdministradors/$', 'enviaMissatgeAdministradors', 
        name ="varis__avisos__envia_avis_administradors" ),
                       
    url(r'^llegeix/(?P<pk>\d+)/$', 'llegeix', 
        name ="varis__avisos__seguir_missatge" ),
    
)

