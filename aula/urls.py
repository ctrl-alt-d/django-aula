# This Python file uses the following encoding: utf-8
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.contrib import admin
from aula.utils.views import keepalive,menu,logout_page
from aula.apps.alumnes.views import mostraGrupPromocionar,nouAlumnePromocionar,llistaGrupsPromocionar
from django.contrib.auth.views import PasswordChangeView
from django.views.static import serve
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.views.generic.base import RedirectView
from django.conf import settings

admin.autodiscover()
admin.site.enable_nav_sidebar = False

import os.path
import private_storage.urls
site_media_site_css = os.path.join(os.path.dirname(__file__), 'site-css' )
site_media_web_demo = os.path.join(os.path.dirname(__file__), '../demo/static-web/demo' )

urlpatterns = [
    re_path(r'^api-token-auth/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    re_path(r'^api-token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^api-token-verify/', TokenVerifyView.as_view(), name='token_verify'),
    re_path(r'^keepalive$', keepalive, name="blanc__blanc__keepalive"),
    path("select2/", include("django_select2.urls")),
    re_path(r'^menu/$', menu),
    #(r'^$', 'missatgeria.views.elMeuMur'),
    #(r'^$', 'presencia.views.mostraImpartir'),       
    re_path(r'^$', menu, name = "blanc__blanc__blanc"),
    re_path(r'^alumnes/', include('aula.apps.alumnes.urls')),
    #(r'^horaris/', include('horaris.urls')),
    re_path(r'^extKronowin/', include('aula.apps.extKronowin.urls')),
    re_path(r'^extSaga/', include('aula.apps.extSaga.urls')),
    re_path(r'^extEsfera/', include('aula.apps.extEsfera.urls')),
    re_path(r'^promocions/(?P<grup>\d+)/$', mostraGrupPromocionar, name = 'administracio__promocions__grups'),
    re_path(r'^promocions/nou-alumne', nouAlumnePromocionar, name = 'administracio__alumnes__noualumne'),
    re_path(r'^promocions/', llistaGrupsPromocionar, name = 'administracio__promocions__llista'),
    re_path(r'^presencia/', include('aula.apps.presencia.urls', ), ),
    re_path(r'^incidencies/', include('aula.apps.incidencies.urls')),
    re_path(r'^missatgeria/', include('aula.apps.missatgeria.urls')),
    re_path(r'^usuaris/', include('aula.apps.usuaris.urls')),
    re_path(r'^utils/', include('aula.utils.urls')),
    re_path(r'^tutoria/', include('aula.apps.tutoria.urls')),
    re_path(r'^avaluacioQualitativa/', include('aula.apps.avaluacioQualitativa.urls')),
    re_path(r'^todo/', include('aula.apps.todo.urls')),
    re_path(r'^sortides/', include('aula.apps.sortides.urls')),
    re_path(r'^baixes/', include('aula.apps.baixes.urls')),
    re_path(r'^open/', include('aula.apps.relacioFamilies.urls')),
    re_path(r'^aules/', include('aula.apps.aules.urls')),
    re_path(r'^recursos/', include('aula.apps.material.urls')),
    re_path(r'^presenciaSetmanal/', include('aula.apps.presenciaSetmanal.urls')),
    re_path(r'^extUntis/', include('aula.apps.extUntis.urls')),
    re_path(r'^matricula/', include('aula.apps.matricula.urls', namespace='matricula')),
    re_path(r'^extPreinscripcio/', include('aula.apps.extPreinscripcio.urls')),
    re_path(r'^api/token/', include('aula.mblapp.urls')),
    re_path(r'^api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # Uncomment the next line to enable the admin:
    re_path(r'^admin/login/', RedirectView.as_view(url=settings.LOGIN_URL, permanent=True, query_string=True)),
    path('admin/', admin.site.urls),
    # Login i logout automàtics
    #(r'^login/$', 'django.contrib.auth.views.login'),
    re_path(r'^password_change/$', PasswordChangeView.as_view(), {'post_change_redirect': '/'}, name="password_change"),
    re_path(r'^logout/$', logout_page),
    #fitxers estàtics:
    re_path(r'^site-css/(?P<path>.*)$', serve,{'document_root': site_media_site_css}),
    re_path(r'^error500$', TemplateView.as_view(template_name='500.html') ),
    re_path('^private-media/', include(private_storage.urls)),

]



try:
    
    urlpatterns_custom = [
                            re_path(r'^customising/', include('customising.urls')),
                            ]
    urlpatterns += urlpatterns_custom
except:    
    pass



    
