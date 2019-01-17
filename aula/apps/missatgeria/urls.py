
from django.conf.urls import url
from aula.apps.missatgeria import views as missatgeria_views

urlpatterns = [

    url(r'^elMeuMur/$', missatgeria_views.elMeuMur, {'pg':1},
        name ="varis__elmur__veure" ),
                       
    url(r'^elMeuMur/(?P<tipus>\w+)/$', missatgeria_views.elMeuMur, {'pg':1},
        name ="varis__elmur__veure" ),
                       
    url(r'^elMeuMur/(?P<pg>\d+)/$', missatgeria_views.elMeuMur,
        name ="varis__elmur__veure_by_pg" ),

    url(r'^enviaMissatgeTutors/$', missatgeria_views.enviaMissatgeTutors,
        name ="consergeria__missatges__envia_tutors" ),
                       
    url(r'^enviaMissatgeAdministradors/$', missatgeria_views.enviaMissatgeAdministradors,
        name ="varis__avisos__envia_avis_administradors" ),
                       
    url(r'^llegeix/(?P<pk>\d+)/$', missatgeria_views.llegeix,
        name ="varis__avisos__seguir_missatge" ),

    url(r'^enviaMissatgeProfessorsPas/$', missatgeria_views.enviaMissatgeProfessorsPas,
       name="varis__prof_i_pas__envia_professors_i_pas"),

    ]

