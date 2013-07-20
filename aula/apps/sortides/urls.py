from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('aula.apps.sortides.views',
                       
    url(r'^sortidesList/$', 'sortidesList',name = "aula__sortides__list"),
    url(r'^sortidaEdit/$', 'sortidaEdit',name = "aula__sortides__edit"),
    url(r'^sortidaEdit/(?P<pk>\d+)/$', 'sortidaEdit', name = 'aula__sortides__edit_by_pk'),

)