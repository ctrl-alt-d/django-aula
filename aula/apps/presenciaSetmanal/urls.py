from django.conf.urls import url

from aula.apps.presenciaSetmanal import views

urlpatterns = [
    #Exemple: presenciaPiolin
    url(r'^$', views.index, name='aula__presencia_setmanal__index'),
    #Exemple: presenciaPiolin/5
    url(r'^(?P<grup_id>\d+)/(?P<dataReferenciaStr>.*)/(?P<nomesPropies>.*)/$', views.detallgrup, name='aula__presencia_setmanal__detallgrup_data'),
    url(r'^(?P<grup_id>\d+)/$', views.detallgrup, name='aula__presencia_setmanal__detallgrup'),


    url(r'modificaEstatControlAssistencia/(?P<codiEstat>.*)/(?P<idAlumne>\d+)/(?P<idImpartir>\d+)$',
        views.modificaEstatControlAssistencia),

    url(r'modificaEstatControlAssistenciaGrup/(?P<codiEstat>.*)/(?P<idImpartir>\d+)$',
        views.modificaEstatControlAssistenciaGrup),
]