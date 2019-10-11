from django.conf.urls import url
from aula.apps.alumnes import views as alumnes_views
urlpatterns = [
   url(r'^triaAlumne/$', alumnes_views.triaAlumne ,
       name="obsolet__tria_alumne"),
                       
   url(r'^triaAlumneCursAjax/(?P<id_nivell>\d+)/$', alumnes_views.triaAlumneCursAjax,
       name="triaAlumneCursAjax"),

   url(r'^triaAlumneGrupAjax/(?P<id_curs>\d+)/$', alumnes_views.triaAlumneGrupAjax,
       name="triaAlumneGrupAjax"),
                       
   url(r'^triaAlumneAlumneAjax/(?P<id_grup>\d+)/$', alumnes_views.triaAlumneAlumneAjax,
       name="triaAlumneAlumneAjax"),
                       
   url(r'^assignaTutors/$', alumnes_views.assignaTutors,
       name="professorat__tutors__tutors_grups"),
                       
   url(r'^elsMeusAlumnesAndAssignatures/$', alumnes_views.elsMeusAlumnesAndAssignatures,
       name="aula__alumnes__alumnes_i_assignatures"),
                       
   url(r'^llistaTutorsIndividualitzats/$', alumnes_views.llistaTutorsIndividualitzats,
       name="professorat__tutors__tutors_individualitzats"),
                       
   url(r'^gestionaAlumnesTutor/(?P<pk>\d+)/$', alumnes_views.gestionaAlumnesTutor,
       name="professorat__tutors__gestio_alumnes_tutor"),
                       
   url(r'^informePsicopedagoc/$', alumnes_views.informePsicopedagoc,
       name="psico__informes_alumne__list"),
                       
   url(r'^duplicats/$', alumnes_views.duplicats,
       name="administracio__sincronitza__duplicats" ),
                       
   url(r'^fusiona/(?P<pk>\d+)/$', alumnes_views.fusiona,
       name="administracio__sincronitza__fusiona"),
   
   url(r'^blanc/$', alumnes_views.blanc,
       name="aula__materies__blanc"),

   url(r'^detallAlumneHorari/(?P<pk>\d+)/(?P<detall>\w+)/$', alumnes_views.detallAlumneHorari,
        name="gestio__usuari__cercaresultat"),

   url(r'^cercaUsuari/$', alumnes_views.cercaUsuari,
        name="gestio__usuari__cerca"),

    url(r'^blanc/$', alumnes_views.blanc,
        name="aula__alumnes__blanc"),                       

    #amorilla@xtec.cat             
    url(r'^Llista completa/$', alumnes_views.llistaAlumnescsv,
        name="coordinacio_alumnes__llistaAlumnescsv__llistat" ),  


]

