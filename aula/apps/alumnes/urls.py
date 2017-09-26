from django.conf.urls import patterns, url

urlpatterns = patterns('aula.apps.alumnes.views',
                       
   url(r'^triaAlumne/$', 'triaAlumne' ,
       name="obsolet__tria_alumne"),
                       
   url(r'^triaAlumneCursAjax/(?P<id_nivell>\d+)/$', 'triaAlumneCursAjax',
       name="triaAlumneCursAjax"),
                       
   url(r'^triaAlumneGrupAjax/(?P<id_curs>\d+)/$', 'triaAlumneGrupAjax',
       name="triaAlumneGrupAjax"),
                       
   url(r'^triaAlumneAlumneAjax/(?P<id_grup>\d+)/$', 'triaAlumneAlumneAjax',
       name="triaAlumneAlumneAjax"),
                       
   url(r'^assignaTutors/$', 'assignaTutors',
       name="professorat__tutors__tutors_grups"),
                       
   url(r'^elsMeusAlumnesAndAssignatures/$', 'elsMeusAlumnesAndAssignatures',
       name="aula__alumnes__alumnes_i_assignatures"),
                       
   url(r'^llistaTutorsIndividualitzats/$', 'llistaTutorsIndividualitzats',
       name="professorat__tutors__tutors_individualitzats"),
                       
   url(r'^gestionaAlumnesTutor/(?P<pk>\d+)/$', 'gestionaAlumnesTutor',
       name="professorat__tutors__gestio_alumnes_tutor"),
                       
   url(r'^informePsicopedagoc/$', 'informePsicopedagoc',
       name="psico__informes_alumne__list"),
                       
   url(r'^duplicats/$', 'duplicats',
       name="administracio__sincronitza__duplicats" ),
                       
   url(r'^fusiona/(?P<pk>\d+)/$', 'fusiona',
       name="administracio__sincronitza__fusiona"),
   
   url(r'^blanc/$', 'blanc',
       name="aula__materies__blanc"),

   url(r'^detallAlumneHorari/(?P<pk>\d+)/(?P<detall>\w+)/$', 'detallAlumneHorari',
        name="consergeria__usuari__cercaresultat"),

   url(r'^cercaUsuari/$', 'cercaUsuari',
        name="consergeria__usuari__cerca"),
)

