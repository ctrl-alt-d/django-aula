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
    # # wizard per franja
    url(r'^consultaRecursPerFranja/$', recurs_views.consultaRecursPerFranja,
        name="gestio__reserva_recurs__consulta"),
    url(r'^detallMassiuFranjaReserves/(?P<year_inici>\d{4})/(?P<year_fi>\d{4})/(?P<month_inici>\d+)/(?P<month_fi>\d+)/(?P<day_inici>\d+)/(?P<day_fi>\d+)/(?P<pk>\d+)/$',
        recurs_views.detallMassiuFranjaReserves,
        name="gestio__reserva_recurs__detallfranjareserves"),
    url(r'^detallFranjaReserves/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$',
        recurs_views.detallFranjaReserves,
        name="gestio__reserva_recurs__detallfranjareserves"),
    url(r'^consultaMassivaRecurs/$', recurs_views.consultaMassivaRecurs,
        name="gestio__reserva_massiva_recurs__consulta"),
    # wizard last step
    url(r'^tramitarReservaRecurs/(?P<pk_recurs>\d+)/(?P<pk_franja>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$',
         recurs_views.tramitarReservaRecurs,
         name="gestio__reserva_recurs__tramitarreservarecurs"),
    url(r'^tramitarReservaMassivaRecurs/(?P<pk_recurs>\d+)/(?P<pk_franja>\d+)/(?P<year_inici>\d{4})/(?P<year_fi>\d{4})/(?P<month_inici>\d+)/(?P<month_fi>\d+)/(?P<day_inici>\d+)/(?P<day_fi>\d+)/$',
         recurs_views.tramitarReservaMassivaRecurs,
         name="gestio__reserva_massiva_recurs__tramitarreservamassivarecurs"),
    url(r'^eliminarReservaRecurs/(?P<pk>\d+)/$',
        recurs_views.eliminarReservaRecurs,
        name="gestio__reserva_recurs__eliminarreservarecurs"),
    url(r'^assignaComentaris/',
            recurs_views.assignaComentarisARecurs,
            name="gestio__recurs__assignacomentari"),

]