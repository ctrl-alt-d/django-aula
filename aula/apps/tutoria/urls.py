from django.conf.urls import url
from aula.apps.tutoria import views as tutoria_views

urlpatterns = [
    url(r'^lesMevesActuacions/$', tutoria_views.lesMevesActuacions,
        name="tutoria__actuacions__list"),
                       
    url(r'^lesMevesActuacionsPsico/$', tutoria_views.lesMevesActuacions,
        name="psico__actuacions__list"),
                       
    url(r'^novaActuacio/$', tutoria_views.novaActuacio,
        name="tutoria__actuacions__alta"),
                       
    url(r'^editaActuacio/(?P<pk>\d+)/$', tutoria_views.editaActuacio,
        name="tutoria__actuacions__edicio"),
                       
    url(r'^esborraActuacio/(?P<pk>\d+)/$', tutoria_views.esborraActuacio,
        name="tutoria__actuacions__esborrat"),

    url(r'^incidenciesGestionadesPelTutor/$', tutoria_views.incidenciesGestionadesPelTutor,
        name="tutoria__incidencies__list"),

    url(r'^justificaFaltesPre/$', tutoria_views.justificaFaltesPre,
        name="tutoria__justificar__pre_justificar"),
                       
    url(r'^elsMeusAlumnesTutorats/$', tutoria_views.elsMeusAlumnesTutorats,
        name="tutoria__alumnes__list"),
                       
    url(r'^elsMeusAlumnesTutoratsEntreDates/$', tutoria_views.elsMeusAlumnesTutoratsEntreDates,
        name="tutoria__assistencia__list_entre_dates"),
                       
    url(r'^detallTutoriaAlumne/(?P<pk>\d+)/(?P<detall>\w+)/$', tutoria_views.detallTutoriaAlumne,
        name="tutoria__alumne__detall"),
                       
    url(r'^justificaFaltes/(?P<pk>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', tutoria_views.justificaFaltes,
        name="tutoria__justificar__by_pk_and_date"),
                       
    url(r'^informeSetmanal/$', tutoria_views.informeSetmanal,
        name="tutoria__alumne__informe_setmanal"),
                       
    url(r'^informeCompletFaltesIncidencies/$', tutoria_views.informeCompletFaltesIncidencies,
        name="coordinacio_alumnes__alumne__informe_faltes_incidencies"),
                       
    url(r'^tutoriaInformeFaltesIncidencies/$', tutoria_views.informeCompletFaltesIncidencies,
        name="tutoria__informe__informe_faltes_incidencies"),                       
                       
    url(r'^informeSetmanalPrint/(?P<pk>\w+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<suport>\w+)/$', tutoria_views.informeSetmanalPrint,
        name="tutoria__alumne__informe_setmanal_print"),
                       
    url(r'^justificador/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', tutoria_views.justificador,
        name="tutoria__justificar__justificador"),
                       
    url(r'^justificaNext/(?P<pk>\d+)/$', tutoria_views.justificaNext,
        name="tutoria__justificar__next"),
                       
    url(r'^calendariCursEscolarTutor/$', tutoria_views.calendariCursEscolarTutor,
        name="tutoria__obsolet__treure"),
                       
    url(r'^seguimentTutorialPreguntes/$', tutoria_views.seguimentTutorialPreguntes,
        name="coordinacio_pedagogica__seguiment_tutorial__preguntes"),
                       
    url(r'^seguimentTutorialFormulari/$', tutoria_views.seguimentTutorialFormulari,
        name="tutoria__seguiment_tutorial__formulari"),
                         
    url(r'^gestioCartes/$', tutoria_views.gestioCartes,
        name="tutoria__cartes_assistencia__gestio_cartes"),
                         
    url(r'^novaCarta/(?P<pk_alumne>\d+)/$', tutoria_views.novaCarta,
        name="tutoria__cartes_assistencia__nova_carta"),
                       
    url(r'^esborraCarta/(?P<pk_carta>\d+)/$', tutoria_views.esborraCarta,
        name="tutoria__cartes_assistencia__esborrar_carta"),
                       
    url(r'^imprimirCarta/(?P<pk_carta>\d+)/$', tutoria_views.imprimirCarta, { 'flag':True,},
        name="tutoria__cartes_assistencia__imprimir_carta"),
                       
    url(r'^imprimirCartaNoFlag/(?P<pk_carta>\d+)/$', tutoria_views.imprimirCarta, { 'flag':False,} ,
        name="tutoria__cartes_assistencia__imprimir_carta_no_flag"),
                       
    url(r'^totesLesCartes/$', tutoria_views.totesLesCartes,
        name="coordinacio_alumnes__assistencia__cartes"),

    url(r'^baixesBlanc/$', tutoria_views.blanc,
        name="professorat__baixes__blanc"),

    url(r'^tutorsBlanc/$', tutoria_views.blanc,
        name="professorat__tutors__blanc"),


    #sortides
    url(r'^justificarSortida/$', tutoria_views.justificarSortida,
    name="tutoria__justificarSortida__list"),
                       
    url(r'^justificarSortidaAlumne/(?P<pk>\d+)/$', tutoria_views.justificarSortidaAlumne,
        name="tutoria__justificarSortida__detall"),
                       
]

