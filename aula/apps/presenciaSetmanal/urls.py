from django.conf.urls import url

from aula.apps.presenciaSetmanal import views

urlpatterns = [
    #Exemple: presenciaPiolin
    url(r'^$', views.index, name='presencia_setmanal__index__index'),
    #Exemple: presenciaPiolin/5
    url(r'^(?P<grup_id>\d+)/(?P<dataReferenciaStr>.*)/$', views.detallgrup, name='presencia_setmanal__index__detallgrup'),
    url(r'^(?P<grup_id>\d+)/$', views.detallgrup, name='presencia_setmanal__index__detallgrup'),

    url(r'modificaEstatControlAssistencia/(?P<codiEstat>.*)/(?P<idAlumne>\d+)/(?P<idImpartir>\d+)$',
        views.modificaEstatControlAssistencia, name='modificaEstatControlAssistencia'),

    url(r'modificaEstatControlAssistenciaGrup/(?P<codiEstat>.*)/(?P<idImpartir>\d+)$',
        views.modificaEstatControlAssistenciaGrup, name='modificaEstatControlAssistenciaGrup'),
]