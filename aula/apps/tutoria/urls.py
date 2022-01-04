from django.urls import re_path
from aula.apps.tutoria import views as tutoria_views

urlpatterns = [
    re_path(r'^lesMevesActuacions/$', tutoria_views.lesMevesActuacions,
        name="tutoria__actuacions__list"),
                       
    re_path(r'^lesMevesActuacionsPsico/$', tutoria_views.lesMevesActuacions,
        name="psico__actuacions__list"),
                       
    re_path(r'^novaActuacio/$', tutoria_views.novaActuacio,
        name="tutoria__actuacions__alta"),
                       
    re_path(r'^editaActuacio/(?P<pk>\d+)/$', tutoria_views.editaActuacio,
        name="tutoria__actuacions__edicio"),
                       
    re_path(r'^esborraActuacio/(?P<pk>\d+)/$', tutoria_views.esborraActuacio,
        name="tutoria__actuacions__esborrat"),

    re_path(r'^incidenciesGestionadesPelTutor/$', tutoria_views.incidenciesGestionadesPelTutor,
        name="tutoria__incidencies__list"),

    re_path(r'^justificaFaltesPre/$', tutoria_views.justificaFaltesPre,
        name="tutoria__justificar__pre_justificar"),
                       
    re_path(r'^elsMeusAlumnesTutorats/$', tutoria_views.elsMeusAlumnesTutorats,
        name="tutoria__alumnes__list"),
                       
    re_path(r'^elsMeusAlumnesTutoratsEntreDates/$', tutoria_views.elsMeusAlumnesTutoratsEntreDates,
        name="tutoria__assistencia__list_entre_dates"),
                       
    re_path(r'^detallTutoriaAlumne/(?P<pk>\d+)/(?P<detall>\w+)/$', tutoria_views.detallTutoriaAlumne,
        name="tutoria__alumne__detall"),
                       
    re_path(r'^justificaFaltes/(?P<pk>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', tutoria_views.justificaFaltes,
        name="tutoria__justificar__by_pk_and_date"),
                       
    re_path(r'^informeSetmanal/$', tutoria_views.informeSetmanal,
        name="tutoria__alumne__informe_setmanal"),
                       
    re_path(r'^informeCompletFaltesIncidencies/$', tutoria_views.informeCompletFaltesIncidencies,
        name="coordinacio_alumnes__alumne__informe_faltes_incidencies"),
                       
    re_path(r'^tutoriaInformeFaltesIncidencies/$', tutoria_views.informeCompletFaltesIncidencies,
        name="tutoria__informe__informe_faltes_incidencies"),                       
                       
    re_path(r'^informeSetmanalPrint/(?P<pk>\w+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<suport>\w+)/$', tutoria_views.informeSetmanalPrint,
        name="tutoria__alumne__informe_setmanal_print"),
                       
    re_path(r'^justificador/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', tutoria_views.justificador,
        name="tutoria__justificar__justificador"),
                       
    re_path(r'^justificaNext/(?P<pk>\d+)/$', tutoria_views.justificaNext,
        name="tutoria__justificar__justificaNext"),

    re_path(r'^faltaNext/(?P<pk>\d+)/$', tutoria_views.faltaNext,
        name="tutoria__justificar__faltaNext"),

    re_path(r'^calendariCursEscolarTutor/$', tutoria_views.calendariCursEscolarTutor,
        name="tutoria__obsolet__treure"),
                       
    re_path(r'^seguimentTutorialPreguntes/$', tutoria_views.seguimentTutorialPreguntes,
        name="coordinacio_pedagogica__seguiment_tutorial__preguntes"),
                       
    re_path(r'^seguimentTutorialFormulari/$', tutoria_views.seguimentTutorialFormulari,
        name="tutoria__seguiment_tutorial__formulari"),
                         
    re_path(r'^gestioCartes/$', tutoria_views.gestioCartes,
        name="tutoria__cartes_assistencia__gestio_cartes"),
                         
    re_path(r'^novaCarta/(?P<pk_alumne>\d+)/$', tutoria_views.novaCarta,
        name="tutoria__cartes_assistencia__nova_carta"),
                       
    re_path(r'^esborraCarta/(?P<pk_carta>\d+)/$', tutoria_views.esborraCarta,
        name="tutoria__cartes_assistencia__esborrar_carta"),
                       
    re_path(r'^imprimirCarta/(?P<pk_carta>\d+)/$', tutoria_views.imprimirCarta, { 'flag':True,},
        name="tutoria__cartes_assistencia__imprimir_carta"),
                       
    re_path(r'^imprimirCartaNoFlag/(?P<pk_carta>\d+)/$', tutoria_views.imprimirCarta, { 'flag':False,} ,
        name="tutoria__cartes_assistencia__imprimir_carta_no_flag"),
                       
    re_path(r'^totesLesCartes/$', tutoria_views.totesLesCartes,
        name="coordinacio_alumnes__assistencia__cartes"),

    re_path(r'^baixesBlanc/$', tutoria_views.blanc,
        name="professorat__baixes__blanc"),

    re_path(r'^tutorsBlanc/$', tutoria_views.blanc,
        name="professorat__tutors__blanc"),


    #sortides
    re_path(r'^justificarSortida/$', tutoria_views.justificarSortida,
    name="tutoria__justificarSortida__list"),
                       
    re_path(r'^justificarSortidaAlumne/(?P<pk>\d+)/$', tutoria_views.justificarSortidaAlumne,
        name="tutoria__justificarSortida__detall"),
                       
]

