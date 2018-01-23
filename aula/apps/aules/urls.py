from django.conf.urls import url

from aula.apps.aules import views as aula_views

urlpatterns = [

    url(r'^consultaAula/$', aula_views.consultaAula,
        name="gestio__reserva_aula__list"),
    #url(r'^detallAulaReserva/(?P<pk>\d+)/(?P<data>\d+)/$',  aula_views.detallAulaReserva,
    #    name="gestio__reserva_aula__detall"),

]