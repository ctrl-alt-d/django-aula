
from django.urls import re_path
from aula.apps.missatgeria import views as missatgeria_views

urlpatterns = [

    re_path(r'^elMeuMur/$', missatgeria_views.elMeuMur, {'pg':1},
        name ="varis__elmur__veure" ),
                       
    re_path(r'^elMeuMur/(?P<tipus>\w+)/$', missatgeria_views.elMeuMur, {'pg':1},
        name ="varis__elmur__veure" ),
                       
    re_path(r'^elMeuMur/(?P<pg>\d+)/$', missatgeria_views.elMeuMur,
        name ="varis__elmur__veure_by_pg" ),

    re_path(r'^enviaMissatgeTutors/$', missatgeria_views.enviaMissatgeTutors,
        name ="consergeria__missatges__envia_tutors" ),
                       
    re_path(r'^enviaMissatgeAdministradors/$', missatgeria_views.enviaMissatgeAdministradors,
        name ="varis__avisos__envia_avis_administradors" ),
                       
    re_path(r'^llegeix/(?P<pk>\d+)/$', missatgeria_views.llegeix,
        name ="varis__avisos__seguir_missatge" ),

    re_path(r'^enviaMissatgeProfessorsPas/$', missatgeria_views.enviaMissatgeProfessorsPas,
       name="varis__prof_i_pas__envia_professors_i_pas"),
    
    re_path(r'^enviaEmailFamilies/$', missatgeria_views.EmailFamilies,
       name="varis__mail__enviaEmailFamilies"),
    
    ]

