# This Python file uses the following encoding: utf-8
from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

import os.path
site_media = os.path.join(
   os.path.dirname(__file__), 'site-css'
)

urlpatterns = patterns('',
    (r'^menu/$', 'aula.utils.views.menu'),
    #(r'^$', 'missatgeria.views.elMeuMur'),
    #(r'^$', 'presencia.views.mostraImpartir'),       
    url(r'^$', 'aula.utils.views.menu', name = "blanc__blanc__blanc"),       
    (r'^alumnes/', include('aula.apps.alumnes.urls')),
    #(r'^horaris/', include('horaris.urls')),
    (r'^extKronowin/', include('aula.apps.extKronowin.urls')),
    (r'^extSaga/', include('aula.apps.extSaga.urls')),
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
    (r'^login/$', 'django.contrib.auth.views.login'),
    url(r'^password_change/$', 'django.contrib.auth.views.password_change', {'post_change_redirect': '/'}, name="password_change"),
    (r'^logout/$', 'aula.utils.views.logout_page'),
    #fitxers estàtics:
    (r'^site-css/(?P<path>.*)$', 'django.views.static.serve',{'document_root': site_media}),

)

try:
    
    urlpatterns_custom = patterns('',
                            (r'^customising/', include('customising.urls')),
                            )
    urlpatterns += urlpatterns_custom
except:    
    pass



    