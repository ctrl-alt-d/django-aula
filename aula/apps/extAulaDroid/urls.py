from django.conf.urls import include, url
from django.conf import settings
from rest_framework.authtoken import views as authViews
from . import views

from rest_framework.routers import DefaultRouter

if hasattr(settings, 'CUSTOM_MODUL_EXTAULADROID_ACTIU' ) and settings.CUSTOM_MODUL_EXTAULADROID_ACTIU:
    urlpatterns = [
        url(r'^login/', authViews.obtain_auth_token),
        url(r'^ajuda/$', views.Ajuda.as_view()),
        url(r'^putGuardia/$', views.PutGuardia.as_view()),
        url(r'^getImpartirPerData/(?P<paramData>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<idUsuari>[A-Za-z0-9\.]+)/$', 
            views.GetImpartirPerData.as_view()),
        url(r'^getControlAssistencia/(?P<idImpartir>[0-9]+)/(?P<idUsuari>[A-Za-z0-9\.]+)/$', 
            views.GetControlAssistencia.as_view()),
        url(r'^putControlAssistencia/(?P<idImpartir>[0-9]+)/(?P<idUsuari>[A-Za-z0-9\.]+)/$', 
            views.PutControlAssistencia.as_view()),
        url(r'^getFrangesHoraries/$', 
            views.GetFrangesHoraries.as_view()),
        url(r'^getEstatsControlAssistencia/$', 
            views.getEstatsControlAssistencia.as_view()),
        url(r'^getProfes/$', views.getProfes.as_view()),
        url(r'^getAPILevel/$', views.getAPILevel.as_view()),
    ]
else:
    urlpatterns = []