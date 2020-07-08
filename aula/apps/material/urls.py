from django.conf.urls import url

from aula.apps.material import views as recurs_views

urlpatterns = [

     url(r'^lesMevesReservesDeRecurs/$', recurs_views.reservaRecursList,
         name="gestio__reserva_recurs__list"),

     # wizard per recurs
     url(r'^consultaRecursPerRecurs/$', recurs_views.consultaRecursPerRecurs,
         name="gestio__reserva_recurs__consulta"),
     url(r'^detallRecursReserves/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
         recurs_views.detallRecursReserves,
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
         recurs_views.tramitarReservaRecurs,
         name="gestio__reserva_recurs__tramitarreservarecurs"),

    # # wizard last step
    # url(r'^tramitarReservaAula/$',
    #     aula_views.tramitarReservaAula,
    #     name="gestio__reserva_aula__tramitarreservaaulal4"),
    #
    #
    url(r'^eliminarReservaRecurs/(?P<pk>\d+)/$',
        recurs_views.eliminarReservaRecurs,
        name="gestio__reserva_recurs__eliminarreservarecurs"),
    #
    # url(r'^getStatus',
    #     aula_api_views.getStatus,
    #     name="gestio__reserva_aula__getStatus"),

    url(r'^assignaComentaris/',
            recurs_views.assignaComentarisARecurs,
            name="gestio__recurs__assignacomentari"),

]