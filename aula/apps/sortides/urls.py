from django.conf.urls import patterns, url

urlpatterns = patterns('aula.apps.sortides.views',
                       
    url(r'^sortidesMeves/$', 'sortidesMevesList',name = "sortides__meves__list"),
    url(r'^sortidesGestio/$', 'sortidesGestioList',name = "sortides__gestio__list"),
    url(r'^sortidaEdit/$', 'sortidaEdit',name = "sortides__sortides__edit"),
    url(r'^sortidaEdit/(?P<pk>\d+)/$', 'sortidaEdit', name = 'sortides__sortides__edit_by_pk'),

)