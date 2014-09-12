# This Python file uses the following encoding: utf-8
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

import os.path
site_media_site_css = os.path.join(os.path.dirname(__file__), 'site-css' )
site_media_web_demo = os.path.join(os.path.dirname(__file__), '../demo/static-web/demo' )

urlpatterns = patterns('',
    (r'^menu/$', 'aula.utils.views.menu'),
    #(r'^$', 'missatgeria.views.elMeuMur'),
    #(r'^$', 'presencia.views.mostraImpartir'),       
    url(r'^$', 'aula.utils.views.menu', name = "blanc__blanc__blanc"),       
    (r'^alumnes/', include('aula.apps.alumnes.urls')),
    #(r'^horaris/', include('horaris.urls')),
    (r'^extKronowin/', include('aula.apps.extKronowin.urls')),
    (r'^extSaga/', include('aula.apps.extSaga.urls')),
    url(r'^promocions/(?P<grup>\d+)/$', 'aula.apps.alumnes.views.mostraGrupPromocionar', name = 'administracio__promocions__grups'),
    url(r'^promocions/nou-alumne', 'aula.apps.alumnes.views.nouAlumnePromocionar', name = 'administracio__promocions__noualumne'),
    url(r'^promocions/', 'aula.apps.alumnes.views.llistaGrupsPromocionar', name = 'administracio__promocions__llista'),
    (r'^presencia/', include('aula.apps.presencia.urls')),
    (r'^incidencies/', include('aula.apps.incidencies.urls')),
    (r'^missatgeria/', include('aula.apps.missatgeria.urls')),
    (r'^usuaris/', include('aula.apps.usuaris.urls')),
    (r'^utils/', include('aula.utils.urls')),
    (r'^tutoria/', include('aula.apps.tutoria.urls')),
    (r'^avaluacioQualitativa/', include('aula.apps.avaluacioQualitativa.urls')),
    (r'^todo/', include('aula.apps.todo.urls')),
    (r'^sortides/', include('aula.apps.sortides.urls')),
    (r'^baixes/', include('aula.apps.baixes.urls')),
    (r'^open/', include('aula.apps.relacioFamilies.urls')),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    # Login i logout automàtics
    #(r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change', {'post_change_redirect': '/'}, name="password_change"),
    (r'^logout/$', 'aula.utils.views.logout_page'),
    #fitxers estàtics:
    (r'^site-css/(?P<path>.*)$', 'django.views.static.serve',{'document_root': site_media_site_css}),
    (r'^error500$', TemplateView.as_view(template_name='500.html') ),

)

try:
    
    urlpatterns_custom = patterns('',
                            (r'^customising/', include('customising.urls')),
                            )
    urlpatterns += urlpatterns_custom
except:    
    pass



    
