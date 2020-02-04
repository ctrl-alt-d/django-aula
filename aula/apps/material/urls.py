from django.conf.urls import url

from aula.apps.material import views as recursos_views

urlpatterns = [

    # url(r'^lesMevesReservesDAula/$', aula_views.reservaAulaList,
    #     name="gestio__reserva_aula__list"),
    #
    # # wizard per aula
    # url(r'^consultaAulaPerAula/$', aula_views.consultaAulaPerAula,
    #     name="gestio__reserva_aula__consulta"),
    # url(r'^detallAulaReserves/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
    #     aula_views.detallAulaReserves,
    #     name="gestio__reserva_aula__detallaulareserves"),
    #
    # # wizard per franja
    # url(r'^consultaAulaPerFranja/$', aula_views.consultaAulaPerFranja,
    #     name="gestio__reserva_aula__consulta"),
    # url(r'^detallFranjaReserves/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
    #     aula_views.detallFranjaReserves,
    #     name="gestio__reserva_aula__detallfranjareserves"),
    #
    # # wizard last step
    # url(r'^tramitarReservaAula/(?P<pk_aula>\d+)/(?P<pk_franja>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$',
    #     aula_views.tramitarReservaAula,
    #     name="gestio__reserva_aula__tramitarreservaaula"),
    #
    # # wizard last step
    # url(r'^tramitarReservaAula/$',
    #     aula_views.tramitarReservaAula,
    #     name="gestio__reserva_aula__tramitarreservaaulal4"),
    #
    #
    # url(r'^eliminarReservaAula/(?P<pk>\d+)/$',
    #     aula_views.eliminarReservaAula,
    #     name="gestio__reserva_aula__eliminarreservaaula"),
    #
    # url(r'^getStatus',
    #     aula_api_views.getStatus,
    #     name="gestio__reserva_aula__getStatus"),

    url(r'^assignaComentaris/',
            recursos_views.assignaComentarisARecurs,
            name="gestio__recurs__assignacomentari"),

]