# This Python file uses the following encoding: utf-8
from django.conf.urls import include, url
from django.urls import path
from django.views.generic import TemplateView
from django.contrib import admin
from aula.utils.views import keepalive,menu,logout_page
from aula.apps.alumnes.views import mostraGrupPromocionar,nouAlumnePromocionar,llistaGrupsPromocionar
from django.contrib.auth.views import PasswordChangeView
from django.views.static import serve
admin.autodiscover()

import os.path
site_media_site_css = os.path.join(os.path.dirname(__file__), 'site-css' )
site_media_web_demo = os.path.join(os.path.dirname(__file__), '../demo/static-web/demo' )

urlpatterns = [
    url(r'^keepalive$', keepalive, name="blanc__blanc__keepalive"),
    url(r'^select2/', include('aula.django_select2.urls')),
    url(r'^menu/$', menu),
    #(r'^$', 'missatgeria.views.elMeuMur'),
    #(r'^$', 'presencia.views.mostraImpartir'),       
    url(r'^$', menu, name = "blanc__blanc__blanc"),
    url(r'^alumnes/', include('aula.apps.alumnes.urls')),
    #(r'^horaris/', include('horaris.urls')),
    url(r'^extKronowin/', include('aula.apps.extKronowin.urls')),
    url(r'^extSaga/', include('aula.apps.extSaga.urls')),
    url(r'^extEsfera/', include('aula.apps.extEsfera.urls')),
    url(r'^promocions/(?P<grup>\d+)/$', mostraGrupPromocionar, name = 'administracio__promocions__grups'),
    url(r'^promocions/nou-alumne', nouAlumnePromocionar, name = 'administracio__alumnes__noualumne'),
    url(r'^promocions/', llistaGrupsPromocionar, name = 'administracio__promocions__llista'),
    url(r'^presencia/', include('aula.apps.presencia.urls', ), ),
    url(r'^incidencies/', include('aula.apps.incidencies.urls')),
    url(r'^missatgeria/', include('aula.apps.missatgeria.urls')),
    url(r'^usuaris/', include('aula.apps.usuaris.urls')),
    url(r'^utils/', include('aula.utils.urls')),
    url(r'^tutoria/', include('aula.apps.tutoria.urls')),
    url(r'^avaluacioQualitativa/', include('aula.apps.avaluacioQualitativa.urls')),
    url(r'^todo/', include('aula.apps.todo.urls')),
    url(r'^sortides/', include('aula.apps.sortides.urls')),
    url(r'^baixes/', include('aula.apps.baixes.urls')),
    url(r'^open/', include('aula.apps.relacioFamilies.urls')),
    url(r'^aules/', include('aula.apps.aules.urls')),
    url(r'^presenciaSetmanal/', include('aula.apps.presenciaSetmanal.urls')),
    url(r'^extUntis/', include('aula.apps.extUntis.urls')),
    # Uncomment the next line to enable the admin:
    path('admin/', admin.site.urls),
    # Login i logout automàtics
    #(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^password_change/$', PasswordChangeView.as_view(), {'post_change_redirect': '/'}, name="password_change"),
    url(r'^logout/$', logout_page),
    #fitxers estàtics:
    url(r'^site-css/(?P<path>.*)$', serve,{'document_root': site_media_site_css}),
    url(r'^error500$', TemplateView.as_view(template_name='500.html') ),

]

try:
    
    urlpatterns_custom = [
                            url(r'^customising/', include('customising.urls')),
                            ]
    urlpatterns += urlpatterns_custom
except:    
    pass



    
