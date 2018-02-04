from django.conf.urls import url

from aula.apps.aules import views as aula_views

urlpatterns = [

    url(r'^consultaAula/$', aula_views.consultaAula,
        name="gestio__reserva_aula__list"),
    url(r'^reservaAulaHorari/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$', aula_views.detallAulaReserves,
        name="gestio__aula__detallaulareserves"),
    url(r'^tramitarReservaAula/(?P<pk>\d+)/(?P<pk_franja>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', aula_views.tramitarReservaAula,
        name="gestio__aula__tramitarreservaaula"),


]