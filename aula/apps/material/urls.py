from django.conf.urls import url

from aula.apps.material import views as recursos_views

urlpatterns = [

     url(r'^lesMevesReservesDeRecurs/$', recursos_views.reservaRecursList,
         name="gestio__reserva_recurs__list"),

     # wizard per recurs
     url(r'^consultaRecursPerRecurs/$', recursos_views.consultaRecursPerRecurs,
         name="gestio__reserva_recurs__consulta"),
     url(r'^detallRecursReserves/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
         recursos_views.detallRecursReserves,
         name="gestio__reserva_recurs__detallrecursreserves"),
    #
    # # wizard per franja
    # url(r'^consultaAulaPerFranja/$', aula_views.consultaAulaPerFranja,
    #     name="gestio__reserva_aula__consulta"),
    # url(r'^detallFranjaReserves/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
    #     aula_views.detallFranjaReserves,
    #     name="gestio__reserva_aula__detallfranjareserves"),
    #
     # wizard last step
     url(r'^tramitarReservaRecurs/(?P<pk_recurs>\d+)/(?P<pk_franja>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$',
         recursos_views.tramitarReservaRecurs,
         name="gestio__reserva_recurs__tramitarreservarecurs"),

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