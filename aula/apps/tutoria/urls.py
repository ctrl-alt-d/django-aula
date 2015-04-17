from django.conf.urls import patterns, url

urlpatterns = patterns('aula.apps.tutoria.views',
    url(r'^lesMevesActuacions/$', 'lesMevesActuacions',
        name="tutoria__actuacions__list"),
                       
    url(r'^lesMevesActuacionsPsico/$', 'lesMevesActuacions',
        name="psico__actuacions__list"),
                       
    url(r'^novaActuacio/$', 'novaActuacio',
        name="tutoria__actuacions__alta"),
                       
    url(r'^editaActuacio/(?P<pk>\d+)/$', 'editaActuacio',
        name="tutoria__actuacions__edicio"),
                       
    url(r'^esborraActuacio/(?P<pk>\d+)/$', 'esborraActuacio',
        name="tutoria__actuacions__esborrat"),
                       
    url(r'^justificaFaltesPre/$', 'justificaFaltesPre',
        name="tutoria__justificar__pre_justificar"),
                       
    url(r'^elsMeusAlumnesTutorats/$', 'elsMeusAlumnesTutorats',
        name="tutoria__alumnes__list"),
                       
    url(r'^elsMeusAlumnesTutoratsEntreDates/$', 'elsMeusAlumnesTutoratsEntreDates',
        name="tutoria__assistencia__list_entre_dates"),
                       
    url(r'^detallTutoriaAlumne/(?P<pk>\d+)/(?P<detall>\w+)/$', 'detallTutoriaAlumne',
        name="tutoria__alumne__detall"),
                       
    url(r'^justificaFaltes/(?P<pk>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'justificaFaltes',
        name="tutoria__justificar__by_pk_and_date"),
                       
    url(r'^informeSetmanal/$', 'informeSetmanal',
        name="tutoria__alumne__informe_setmanal"),
                       
    url(r'^informeCompletFaltesIncidencies/$', 'informeCompletFaltesIncidencies',
        name="coordinacio_alumnes__alumne__informe_faltes_incidencies"),
                       
    url(r'^tutoriaInformeFaltesIncidencies/$', 'informeCompletFaltesIncidencies',
        name="tutoria__informe__informe_faltes_incidencies"),                       
                       
    url(r'^informeSetmanalPrint/(?P<pk>\w+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<suport>\w+)/$', 'informeSetmanalPrint',
        name="tutoria__alumne__informe_setmanal_print"),
                       
    url(r'^justificador/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 'justificador',
        name="tutoria__justificar__justificador"),
                       
    url(r'^justificaNext/(?P<pk>\d+)/$', 'justificaNext',
        name="tutoria__justificar__next"),
                       
    url(r'^calendariCursEscolarTutor/$', 'calendariCursEscolarTutor',
        name="tutoria__obsolet__treure"),
                       
    url(r'^seguimentTutorialPreguntes/$', 'seguimentTutorialPreguntes',
        name="coordinacio_pedagogica__seguiment_tutorial__preguntes"),
                       
    url(r'^seguimentTutorialFormulari/$', 'seguimentTutorialFormulari',
        name="tutoria__seguiment_tutorial__formulari"),
                         
    url(r'^gestioCartes/$', 'gestioCartes',
        name="tutoria__cartes_assistencia__gestio_cartes"),
                         
    url(r'^novaCarta/(?P<pk_alumne>\d+)/$', 'novaCarta',
        name="tutoria__cartes_assistencia__nova_carta"),
                       
    url(r'^esborraCarta/(?P<pk_carta>\d+)/$', 'esborraCarta',
        name="tutoria__cartes_assistencia__esborrar_carta"),
                       
    url(r'^imprimirCarta/(?P<pk_carta>\d+)/$', 'imprimirCarta', { 'flag':True,},
        name="tutoria__cartes_assistencia__imprimir_carta"),
                       
    url(r'^imprimirCartaNoFlag/(?P<pk_carta>\d+)/$', 'imprimirCarta', { 'flag':False,} ,
        name="tutoria__cartes_assistencia__imprimir_carta_no_flag"),
                       
    url(r'^totesLesCartes/$', 'totesLesCartes',
        name="coordinacio_alumnes__assistencia__cartes"),

    url(r'^baixesBlanc/$', 'blanc',
        name="professorat__baixes__blanc"),

    url(r'^tutorsBlanc/$', 'blanc',
        name="professorat__tutors__blanc"),


    #sortides
    url(r'^justificarSortida/$', 'justificarSortida',
    name="tutoria__justificarSortida__list"),
                       
    url(r'^justificarSortidaAlumne/(?P<pk>\d+)/$', 'justificarSortidaAlumne',
        name="tutoria__justificarSortida__detall"),
                       
)

