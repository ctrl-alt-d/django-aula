from django.urls import re_path

from aula.apps.aules import views as aula_views
from aula.apps.aules import api_views as aula_api_views

urlpatterns = [

    re_path(r'^lesMevesReservesDAula/$', aula_views.reservaAulaList,
        name="gestio__reserva_aula__list"),

    # wizard per aula
    re_path(r'^consultaAulaPerAula/$', aula_views.consultaAulaPerAula,
        name="gestio__reserva_aula__consulta"),
    re_path(r'^detallAulaReserves/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$', 
        aula_views.detallAulaReserves,
        name="gestio__reserva_aula__detallaulareserves"),

    # wizard per franja
    re_path(r'^consultaAulaPerFranja/$', aula_views.consultaAulaPerFranja,
        name="gestio__reserva_aula__consulta"),
    re_path(r'^detallFranjaReserves/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$', 
        aula_views.detallFranjaReserves,
        name="gestio__reserva_aula__detallfranjareserves"),

    # wizard last step
    re_path(r'^tramitarReservaAula/(?P<pk_aula>\d+)/(?P<pk_franja>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 
        aula_views.tramitarReservaAula,
        name="gestio__reserva_aula__tramitarreservaaula"),
    
    # wizard last step
    re_path(r'^tramitarReservaAula/$', 
        aula_views.tramitarReservaAula,
        name="gestio__reserva_aula__tramitarreservaaulal4"),
    

    re_path(r'^eliminarReservaAula/(?P<pk>\d+)/$', 
        aula_views.eliminarReservaAula,
        name="gestio__reserva_aula__eliminarreservaaula"),

    re_path(r'^getStatus',
        aula_api_views.getStatus,
        name="gestio__reserva_aula__getStatus"),

    re_path(r'^assignaComentaris/',
            aula_views.assignaComentarisAAules,
            name="gestio__aula__assignacomentari"),

]