from django.conf.urls import url
from aula.apps.sortides import views as sortides_views

urlpatterns = [
                       
    url(r'^sortidesMeves/$', sortides_views.sortidesMevesList,name = "sortides__meves__list"),
    url(r'^sortidesGestio/$', sortides_views.sortidesGestioList,name = "sortides__gestio__list"),
    url(r'^sortidesConsergeria/$', sortides_views.sortidesConsergeriaList, name="sortides__consergeria__list"),
    url(r'^sortidesAll/$', sortides_views.sortidesAllList,name = "sortides__all__list"),
    
    url(r'^sortidaEdit/$', sortides_views.sortidaEdit,name = "sortides__sortides__edit", kwargs={'origen':'Meves'}),
    url(r'^sortidaEditGestio/$', sortides_views.sortidaEdit,name = "sortides__sortides__editGestio", kwargs={'origen':'Gestio'}),
    url(r'^sortidaEditAll/$', sortides_views.sortidaEdit,name = "sortides__sortides__editAll", kwargs={'origen':'All'}),

    url(r'^sortidaEdit/(?P<pk>\d+)/$', sortides_views.sortidaEdit, name = 'sortides__sortides__edit_by_pk', kwargs={'origen':'Meves'}),
    url(r'^sortidaEditGestio/(?P<pk>\d+)/$', sortides_views.sortidaEdit, name = 'sortides__sortides__editGestio_by_pk', kwargs={'origen':'Gestio'}),
    url(r'^sortidaEditAll/(?P<pk>\d+)/$', sortides_views.sortidaEdit, name = 'sortides__sortides__editAll_by_pk', kwargs={'origen':'All'}),

    url(r'^sortidaClonar/(?P<pk>\d+)/$', sortides_views.sortidaEdit, name = 'sortides__sortides__clonar_by_pk', kwargs={ 'clonar':True, 'origen':'Meves',  }),

    url(r'^alumnesConvocats/(?P<pk>\d+)/$', sortides_views.alumnesConvocats, name = 'sortides__sortides__alumnesConvocats', kwargs={'origen':'Meves'}),
    url(r'^alumnesConvocatsGestio/(?P<pk>\d+)/$', sortides_views.alumnesConvocats, name = 'sortides__sortides__alumnesConvocatsGestio', kwargs={'origen':'Gestio'}),
    url(r'^alumnesConvocatsAll/(?P<pk>\d+)/$', sortides_views.alumnesConvocats, name = 'sortides__sortides__alumnesConvocatsAll', kwargs={'origen':'All'}),

    url(r'^alumnesFallen/(?P<pk>\d+)/$', sortides_views.alumnesFallen, name = 'sortides__sortides__alumnesConvocats', kwargs={'origen':'Meves'}),
    url(r'^alumnesFallenGestio/(?P<pk>\d+)/$', sortides_views.alumnesFallen, name = 'sortides__sortides__alumnesFallenGestio', kwargs={'origen':'Gestio'}),
    url(r'^alumnesFallenAll/(?P<pk>\d+)/$', sortides_views.alumnesFallen, name = 'sortides__sortides__alumnesFallenAll', kwargs={'origen':'All'}),

    url(r'^alumnesJustificats/(?P<pk>\d+)/$', sortides_views.alumnesJustificats, name = 'sortides__sortides__alumnesJustificats', kwargs={'origen':'Meves'}),
    url(r'^alumnesJustificatsGestio/(?P<pk>\d+)/$', sortides_views.alumnesJustificats, name = 'sortides__sortides__alumnesJustificatsGestio', kwargs={'origen':'Gestio'}),
    url(r'^alumnesJustificatsAll/(?P<pk>\d+)/$', sortides_views.alumnesJustificats, name = 'sortides__sortides__alumnesJustificatsAll', kwargs={'origen':'All'}),

    url(r'^professorsAcompanyants/(?P<pk>\d+)/$', sortides_views.professorsAcompanyants, name = 'sortides__sortides__professorsAcompanyants', kwargs={'origen':'Meves'}),
    url(r'^professorsAcompanyantsGestio/(?P<pk>\d+)/$', sortides_views.professorsAcompanyants, name = 'sortides__sortides__professorsAcompanyantsGestio', kwargs={'origen':'Gestio'}),
    url(r'^professorsAcompanyantsAll/(?P<pk>\d+)/$', sortides_views.professorsAcompanyants, name = 'sortides__sortides__professorsAcompanyantsAll', kwargs={'origen':'All'}),

    url(r'^esborrar/(?P<pk>\d+)/$', sortides_views.esborrar, name = 'sortides__sortides__esborrar', kwargs={'origen':'Meves'}),
    url(r'^esborrarGestio/(?P<pk>\d+)/$', sortides_views.esborrar, name = 'sortides__sortides__esborrarGestio', kwargs={'origen':'Gestio'}),
    url(r'^esborrarAll/(?P<pk>\d+)/$', sortides_views.esborrar, name = 'sortides__sortides__esborrarAll', kwargs={'origen':'All'}),

    url(r'^sortidaExcel/(?P<pk>\d+)/$', sortides_views.sortidaExcel, name = 'sortides__sortides__sortidaExcel'),



    url(r'^sortidaiCal/', sortides_views.sortidaiCal, name = 'sortides__sortides__ical'),

    url(r'^imprimir/(?P<pk>\d+)/(?P<din>\d+)$', sortides_views.imprimir, name = 'sortides__sortides__imprimir' ),

    url(r'^pagoOnline/(?P<pk>\d+)/$', sortides_views.pagoOnline, name='sortides__sortides__pago_on_line'),
    url(r'^pagoOnlineKO/(?P<pk>\d+)/$', sortides_views.pagoOnlineKO, name='sortides__sortides__pago_on_lineKO'),
    url(r'^passarella/(?P<pk>\d+)/$', sortides_views.passarella, name='sortides__sortides__passarella'),

    url(r'^retornTransaccio/(?P<pk>\d+)/$', sortides_views.retornTransaccio, name='sortides__sortides__retorn_transaccio'),

    url(r'^detallPagament/(?P<pk>\d+)/$', sortides_views.detallPagament, name='sortides__sortides__detall_pagament'),
    
    url(r'^quotes/$', sortides_views.assignaQuotes, name='gestio__quotes__assigna'),
    url(r'^quotes/(?P<curs>\d+)/(?P<tipus>\d+)/(?P<nany>\d+)/(?P<auto>.*)/$', sortides_views.quotesCurs, name='gestio__quotes__assigna'),
    url(r'^totals/$', sortides_views.totalsQuotes, name='gestio__quotes__descarrega'),
    url(r'^blanc/$', sortides_views.blanc, name="gestio__quotes__blanc"),

    url(r'^pagoEfectiu/(?P<pk>\d+)/$', sortides_views.pagoEfectiu, name='sortides__sortides__pago_efectiu'),

]