from django.conf.urls import patterns, url

urlpatterns = patterns('aula.apps.sortides.views',
                       
    url(r'^sortidesList/$', 'sortidesList',name = "sortides__sortides__list"),
    url(r'^sortidaEdit/$', 'sortidaEdit',name = "sortides__sortides__edit"),
    url(r'^sortidaEdit/(?P<pk>\d+)/$', 'sortidaEdit', name = 'sortides__sortides__edit_by_pk'),

)