from django.conf.urls import patterns, url

urlpatterns = patterns('aula.apps.sortides.views',
                       
    url(r'^sortidesMeves/$', 'sortidesMevesList',name = "sortides__meves__list"),
    url(r'^sortidesGestio/$', 'sortidesGestioList',name = "sortides__gestio__list"),
    url(r'^sortidesAll/$', 'sortidesAllList',name = "sortides__all__list"),
    
    url(r'^sortidaEdit/$', 'sortidaEdit',name = "sortides__sortides__edit", kwargs={'origen':'Meves'}),
    url(r'^sortidaEditGestio/$', 'sortidaEdit',name = "sortides__sortides__editGestio", kwargs={'origen':'Gestio'}),
    url(r'^sortidaEditAll/$', 'sortidaEdit',name = "sortides__sortides__editAll", kwargs={'origen':'All'}),

    url(r'^sortidaEdit/(?P<pk>\d+)/$', 'sortidaEdit', name = 'sortides__sortides__edit_by_pk', kwargs={'origen':'Meves'}),
    url(r'^sortidaEditGestio/(?P<pk>\d+)/$', 'sortidaEdit', name = 'sortides__sortides__editGestio_by_pk', kwargs={'origen':'Gestio'}),
    url(r'^sortidaEditAll/(?P<pk>\d+)/$', 'sortidaEdit', name = 'sortides__sortides__editAll_by_pk', kwargs={'origen':'All'}),

    url(r'^alumnesConvocats/(?P<pk>\d+)/$', 'alumnesConvocats', name = 'sortides__sortides__alumnesConvocats', kwargs={'origen':'Meves'}),
    url(r'^alumnesConvocatsGestio/(?P<pk>\d+)/$', 'alumnesConvocats', name = 'sortides__sortides__alumnesConvocatsGestio', kwargs={'origen':'Gestio'}),
    url(r'^alumnesConvocatsAll/(?P<pk>\d+)/$', 'alumnesConvocats', name = 'sortides__sortides__alumnesConvocatsAll', kwargs={'origen':'All'}),

    url(r'^alumnesFallen/(?P<pk>\d+)/$', 'alumnesFallen', name = 'sortides__sortides__alumnesConvocats', kwargs={'origen':'Meves'}),
    url(r'^alumnesFallenGestio/(?P<pk>\d+)/$', 'alumnesFallen', name = 'sortides__sortides__alumnesFallenGestio', kwargs={'origen':'Gestio'}),
    url(r'^alumnesFallenAll/(?P<pk>\d+)/$', 'alumnesFallen', name = 'sortides__sortides__alumnesFallenAll', kwargs={'origen':'All'}),

    url(r'^alumnesJustificats/(?P<pk>\d+)/$', 'alumnesJustificats', name = 'sortides__sortides__alumnesJustificats', kwargs={'origen':'Meves'}),
    url(r'^alumnesJustificatsGestio/(?P<pk>\d+)/$', 'alumnesJustificats', name = 'sortides__sortides__alumnesJustificatsGestio', kwargs={'origen':'Gestio'}),
    url(r'^alumnesJustificatsAll/(?P<pk>\d+)/$', 'alumnesJustificats', name = 'sortides__sortides__alumnesJustificatsAll', kwargs={'origen':'All'}),

    url(r'^professorsAcompanyants/(?P<pk>\d+)/$', 'professorsAcompanyants', name = 'sortides__sortides__professorsAcompanyants', kwargs={'origen':'Meves'}),
    url(r'^professorsAcompanyantsGestio/(?P<pk>\d+)/$', 'professorsAcompanyants', name = 'sortides__sortides__professorsAcompanyantsGestio', kwargs={'origen':'Gestio'}),
    url(r'^professorsAcompanyantsAll/(?P<pk>\d+)/$', 'professorsAcompanyants', name = 'sortides__sortides__professorsAcompanyantsAll', kwargs={'origen':'All'}),

    url(r'^esborrar/(?P<pk>\d+)/$', 'esborrar', name = 'sortides__sortides__esborrar', kwargs={'origen':'Meves'}),
    url(r'^esborrarGestio/(?P<pk>\d+)/$', 'esborrar', name = 'sortides__sortides__esborrarGestio', kwargs={'origen':'Gestio'}),
    url(r'^esborrarAll/(?P<pk>\d+)/$', 'esborrar', name = 'sortides__sortides__esborrarAll', kwargs={'origen':'All'}),

    url(r'^sortidaExcel/(?P<pk>\d+)/$', 'sortidaExcel', name = 'sortides__sortides__sortidaExcel'),



    url(r'^sortidaiCal/', 'sortidaiCal', name = 'sortides__sortides__ical'),

)