from django.conf.urls import url

from aula.apps.aules import views as aula_views

urlpatterns = [

    url(r'^consultaAulaPerAula/$', aula_views.consultaAulaPerAula,
        name="gestio__reserva_aula__list"),
    url(r'^detallAulaReserves/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/(?P<pk>\d+)/$', 
        aula_views.detallAulaReserves,
        name="gestio__aula__detallaulareserves"),
    url(r'^tramitarReservaAula/(?P<pk>\d+)/(?P<pk_franja>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 
        aula_views.tramitarReservaAula,
        name="gestio__aula__tramitarreservaaula"),
    url(r'^eliminarReservaAula/(?P<pk>\d+)/(?P<pk_aula>\d+)/(?P<year>\d{4})/(?P<month>\d+)/(?P<day>\d+)/$', 
        aula_views.eliminarReservaAula,
        name="gestio__aula__eliminarreservaaula"),



]