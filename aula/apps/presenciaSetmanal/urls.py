from django.urls import re_path

from aula.apps.presenciaSetmanal import views

urlpatterns = [
    #Exemple: presenciaPiolin
    re_path(r'^$', views.index, name='aula__presencia_setmanal__index'),
    #Exemple: presenciaPiolin/5
    re_path(r'^(?P<grup_id>\d+)/(?P<dataReferenciaStr>.*)/(?P<nomesPropies>.*)/$', views.detallgrup, name='aula__presencia_setmanal__detallgrup_data'),
    re_path(r'^(?P<grup_id>\d+)/$', views.detallgrup, name='aula__presencia_setmanal__detallgrup'),


    re_path(r'modificaEstatControlAssistencia/(?P<codiEstat>.*)/(?P<idAlumne>\d+)/(?P<idImpartir>\d+)$',
        views.modificaEstatControlAssistencia),

    re_path(r'modificaEstatControlAssistenciaGrup/(?P<codiEstat>.*)/(?P<idImpartir>\d+)$',
        views.modificaEstatControlAssistenciaGrup),
]