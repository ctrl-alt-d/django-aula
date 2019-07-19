from django.conf.urls import include, url
from rest_framework.authtoken import views as authViews
from . import views

from rest_framework.routers import DefaultRouter

#router = DefaultRouter()
#router.register(r'login/', authViews.obtain_auth_token)
#router.register(r'filtre/(\w+)/(\w+)/$', views.getImpartirPerData),
#urlpatterns = router.urls

urlpatterns = [
    url(r'^ajuda/$', views.Ajuda.as_view()),
    url(r'^getImpartirPerData/(?P<paramData>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<idUsuari>[A-Za-z0-9\.]+)$', views.ListImpartirPerData.as_view()),
    url(r'^getControlAssistencia/(?P<idImpartir>[0-9]+)/(?P<idUsuari>[A-Za-z0-9\.]+)/$', views.ListControlAssistencia.as_view()),
    url(r'^login/', authViews.obtain_auth_token)
]

'''
urlpatterns = [
    url(r'^ajuda/$', views.ajuda),
    url(r'^login/$', views.login),
    url(r'^getImpartirPerData/(?P<paramData>[0-9]{4}-[0-9]{2}-[0-9]{2})/(?P<idUsuari>[A-Za-z0-9\.]+)/$',
        views.getImpartirPerData),
    url(r'^getControlAssistencia/(?P<idImpartir>[0-9]+)/(?P<idUsuari>[A-Za-z0-9\.]+)/$', views.getControlAssistencia),
    url(r'^getFrangesHoraries/(?P<idUsuari>[A-Za-z0-9\.]+)/$', views.getFrangesHoraries),
    url(r'^getEstatControlAssistencia/(?P<idUsuari>[A-Za-z0-9\.]+)/$', views.getEstatControlAssistencia),
    url(r'^getProfes/(?P<idUsuari>[A-Za-z0-9\.]+)/$', views.getProfes),
    url(r'^putControlAssistencia/(?P<idImpartir>[0-9]+)/(?P<idUsuari>[A-Za-z0-9\.]+)/$', views.putControlAssistencia),
    url(r'^putGuardia/(?P<idUsuari>[A-Za-z0-9\.]+)/$', views.putGuardia),
    url(r'^getAPILevel/$', views.getAPILevel),
    url(r'^test/', views.test),
    ]
'''