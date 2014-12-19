from django.conf.urls import patterns, url

urlpatterns = patterns('aula.apps.sortides.views',
                       
    url(r'^sortidesMeves/$', 'sortidesMevesList',name = "sortides__meves__list"),
    url(r'^sortidesGestio/$', 'sortidesGestioList',name = "sortides__gestio__list"),
    
    
    url(r'^sortidaEdit/$', 'sortidaEdit',name = "sortides__sortides__edit"),
    url(r'^sortidaEditGestio/$', 'sortidaEdit',name = "sortides__sortides__editGestio", kwargs={'esGestio':True}),

    url(r'^sortidaEdit/(?P<pk>\d+)/$', 'sortidaEdit', name = 'sortides__sortides__edit_by_pk'),
    url(r'^sortidaEditGestio/(?P<pk>\d+)/$', 'sortidaEdit', name = 'sortides__sortides__editGestio_by_pk', kwargs={'esGestio':True}),

    url(r'^alumnesConvocats/(?P<pk>\d+)/$', 'alumnesConvocats', name = 'sortides__sortides__alumnesConvocats'),
    url(r'^alumnesConvocatsGestio/(?P<pk>\d+)/$', 'alumnesConvocats', name = 'sortides__sortides__alumnesConvocatsGestio', kwargs={'esGestio':True}),

    url(r'^alumnesFallen/(?P<pk>\d+)/$', 'alumnesFallen', name = 'sortides__sortides__alumnesConvocats'),
    url(r'^alumnesFallenGestio/(?P<pk>\d+)/$', 'alumnesFallen', name = 'sortides__sortides__alumnesFallenGestio', kwargs={'esGestio':True}),

    url(r'^esborrar/(?P<pk>\d+)/$', 'esborrar', name = 'sortides__sortides__esborrar'),
    url(r'^esborrarGestio/(?P<pk>\d+)/$', 'esborrar', name = 'sortides__sortides__esborrarGestio', kwargs={'esGestio':True}),

    url(r'^sortidaiCal/', 'sortidaiCal', name = 'sortides__sortides__ical'),

)