from django.urls import re_path
from aula.apps.alumnes import views as alumnes_views
urlpatterns = [
   re_path(r'^triaAlumne/$', alumnes_views.triaAlumne ,
       name="obsolet__tria_alumne"),
                       
   re_path(r'^triaAlumneCursAjax/(?P<id_nivell>\d+)/$', alumnes_views.triaAlumneCursAjax,
       name="triaAlumneCursAjax"),

   re_path(r'^triaAlumneGrupAjax/(?P<id_curs>\d+)/$', alumnes_views.triaAlumneGrupAjax,
       name="triaAlumneGrupAjax"),
                       
   re_path(r'^triaAlumneAlumneAjax/(?P<id_grup>\d+)/$', alumnes_views.triaAlumneAlumneAjax,
       name="triaAlumneAlumneAjax"),
                       
   re_path(r'^assignaTutors/$', alumnes_views.assignaTutors,
       name="professorat__tutors__tutors_grups"),
                       
   re_path(r'^elsMeusAlumnesAndAssignatures/$', alumnes_views.elsMeusAlumnesAndAssignatures,
       name="aula__alumnes__alumnes_i_assignatures"),
                       
   re_path(r'^llistaTutorsIndividualitzats/$', alumnes_views.llistaTutorsIndividualitzats,
       name="professorat__tutors__tutors_individualitzats"),
                       
   re_path(r'^gestionaAlumnesTutor/(?P<pk>\d+)/$', alumnes_views.gestionaAlumnesTutor,
       name="professorat__tutors__gestio_alumnes_tutor"),
                       
   re_path(r'^informePsicopedagoc/$', alumnes_views.informePsicopedagoc,
       name="psico__informes_alumne__list"),
                       
   re_path(r'^nomsentitw0/$', alumnes_views.canviarNomSentitW0,
       name="psico__nomsentit__w0"),
                       
   re_path(r'^nomsentitw1/$', alumnes_views.canviarNomSentitW1,
       name="psico__nomsentit__w1"),
                       
   re_path(r'^nomsentitw2/(?P<pk>\d+)/$', alumnes_views.canviarNomSentitW2,
       name="psico__nomsentit__w2"),
                       
   re_path(r'^duplicats/$', alumnes_views.duplicats,
       name="administracio__sincronitza__duplicats" ),
                       
   re_path(r'^fusiona/(?P<pk>\d+)/$', alumnes_views.fusiona,
       name="administracio__sincronitza__fusiona"),
   
   re_path(r'^blanc/$', alumnes_views.blanc,
       name="aula__materies__blanc"),

   re_path(r'^detallAlumneHorari/(?P<pk>\d+)/(?P<detall>\w+)/$', alumnes_views.detallAlumneHorari,
        name="gestio__usuari__cercaresultat"),

   re_path(r'^cercaUsuari/$', alumnes_views.cercaUsuari,
        name="gestio__usuari__cerca"),

    re_path(r'^blanc/$', alumnes_views.blanc,
        name="aula__alumnes__blanc"),                       

    #amorilla@xtec.cat             
    re_path(r'^Llista completa/$', alumnes_views.llistaAlumnescsv,
        name="coordinacio_alumnes__llistaAlumnescsv__llistat" ),  


]

