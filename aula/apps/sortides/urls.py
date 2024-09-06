from django.urls import re_path
from aula.apps.sortides import views as sortides_views

urlpatterns = [

    re_path(r'^sortidesMeves/$', sortides_views.sortidesMevesList, name="sortides__meves__list"),
    re_path(r'^sortidesMeves/(?P<tipus>\w+)/$', sortides_views.sortidesMevesList, name='sortides__meves__list_by_tipus'),
    re_path(r'^sortidesGestio/$', sortides_views.sortidesGestioList, name="sortides__gestio__list"),
    re_path(r'^sortidesGestio/(?P<tipus>\w+)/$', sortides_views.sortidesGestioList,name = "sortides__gestio__list_by_tipus"),
    re_path(r'^sortidesConsergeria/$', sortides_views.sortidesConsergeriaList, name="sortides__consergeria__list"),
    re_path(r'^sortidesAll/$', sortides_views.sortidesAllList, name="sortides__all__list"),
    re_path(r'^sortidesAll/(?P<tipus>\w+)/$', sortides_views.sortidesAllList,name = "sortides__all__list"),

    re_path(r'^sortidaEdit/(?P<tipus>\w+)/$', sortides_views.sortidaEdit,name = "sortides__sortides__edit", kwargs={'origen':'Meves'}),
    re_path(r'^sortidaEditGestio/$', sortides_views.sortidaEdit,name = "sortides__sortides__editGestio", kwargs={'origen':'Gestio'}),
    re_path(r'^sortidaEditAll/$', sortides_views.sortidaEdit,name = "sortides__sortides__editAll", kwargs={'origen':'All'}),

    re_path(r'^sortidaEdit/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.sortidaEdit, name = 'sortides__sortides__edit_by_pk', kwargs={'origen':'Meves'}),
    re_path(r'^sortidaEditGestio/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.sortidaEdit, name = 'sortides__sortides__editGestio_by_pk', kwargs={'origen':'Gestio'}),
    re_path(r'^sortidaEditAll/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.sortidaEdit, name = 'sortides__sortides__editAll_by_pk', kwargs={'origen':'All'}),

    re_path(r'^sortidaClonar/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.sortidaEdit, name = 'sortides__sortides__clonar_by_pk', kwargs={ 'clonar':True, 'origen':'Meves' }),

    re_path(r'^alumnesConvocats/(?P<pk>\d+)/$', sortides_views.alumnesConvocats, name = 'sortides__sortides__alumnesConvocats', kwargs={'origen':'Meves'}),
    re_path(r'^alumnesConvocatsGestio/(?P<pk>\d+)/$', sortides_views.alumnesConvocats, name = 'sortides__sortides__alumnesConvocatsGestio', kwargs={'origen':'Gestio'}),
    re_path(r'^alumnesConvocatsAll/(?P<pk>\d+)/$', sortides_views.alumnesConvocats, name = 'sortides__sortides__alumnesConvocatsAll', kwargs={'origen':'All'}),

    re_path(r'^alumnesFallen/(?P<pk>\d+)/$', sortides_views.alumnesFallen, name = 'sortides__sortides__alumnesConvocats', kwargs={'origen':'Meves'}),
    re_path(r'^alumnesFallenGestio/(?P<pk>\d+)/$', sortides_views.alumnesFallen, name = 'sortides__sortides__alumnesFallenGestio', kwargs={'origen':'Gestio'}),
    re_path(r'^alumnesFallenAll/(?P<pk>\d+)/$', sortides_views.alumnesFallen, name = 'sortides__sortides__alumnesFallenAll', kwargs={'origen':'All'}),

    re_path(r'^alumnesJustificats/(?P<pk>\d+)/$', sortides_views.alumnesJustificats, name = 'sortides__sortides__alumnesJustificats', kwargs={'origen':'Meves'}),
    re_path(r'^alumnesJustificatsGestio/(?P<pk>\d+)/$', sortides_views.alumnesJustificats, name = 'sortides__sortides__alumnesJustificatsGestio', kwargs={'origen':'Gestio'}),
    re_path(r'^alumnesJustificatsAll/(?P<pk>\d+)/$', sortides_views.alumnesJustificats, name = 'sortides__sortides__alumnesJustificatsAll', kwargs={'origen':'All'}),

    re_path(r'^professorsAcompanyants/(?P<pk>\d+)/$', sortides_views.professorsAcompanyants, name = 'sortides__sortides__professorsAcompanyants', kwargs={'origen':'Meves'}),
    re_path(r'^professorsAcompanyantsGestio/(?P<pk>\d+)/$', sortides_views.professorsAcompanyants, name = 'sortides__sortides__professorsAcompanyantsGestio', kwargs={'origen':'Gestio'}),
    re_path(r'^professorsAcompanyantsAll/(?P<pk>\d+)/$', sortides_views.professorsAcompanyants, name = 'sortides__sortides__professorsAcompanyantsAll', kwargs={'origen':'All'}),

    re_path(r'^alumnesConvocats/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.alumnesConvocats, name = 'sortides__sortides__alumnesConvocats', kwargs={'origen':'Meves'}),
    re_path(r'^alumnesConvocatsGestio/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.alumnesConvocats, name = 'sortides__sortides__alumnesConvocatsGestio', kwargs={'origen':'Gestio'}),
    re_path(r'^alumnesConvocatsAll/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.alumnesConvocats, name = 'sortides__sortides__alumnesConvocatsAll', kwargs={'origen':'All'}),

    re_path(r'^alumnesFallen/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.alumnesFallen, name = 'sortides__sortides__alumnesConvocats', kwargs={'origen':'Meves'}),
    re_path(r'^alumnesFallenGestio/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.alumnesFallen, name = 'sortides__sortides__alumnesFallenGestio', kwargs={'origen':'Gestio'}),
    re_path(r'^alumnesFallenAll/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.alumnesFallen, name = 'sortides__sortides__alumnesFallenAll', kwargs={'origen':'All'}),

    re_path(r'^alumnesJustificats/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.alumnesJustificats, name = 'sortides__sortides__alumnesJustificats', kwargs={'origen':'Meves'}),
    re_path(r'^alumnesJustificatsGestio/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.alumnesJustificats, name = 'sortides__sortides__alumnesJustificatsGestio', kwargs={'origen':'Gestio'}),
    re_path(r'^alumnesJustificatsAll/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.alumnesJustificats, name = 'sortides__sortides__alumnesJustificatsAll', kwargs={'origen':'All'}),

    re_path(r'^professorsAcompanyants/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.professorsAcompanyants, name = 'sortides__sortides__professorsAcompanyants', kwargs={'origen':'Meves'}),
    re_path(r'^professorsAcompanyantsGestio/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.professorsAcompanyants, name = 'sortides__sortides__professorsAcompanyantsGestio', kwargs={'origen':'Gestio'}),
    re_path(r'^professorsAcompanyantsAll/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.professorsAcompanyants, name = 'sortides__sortides__professorsAcompanyantsAll', kwargs={'origen':'All'}),

    re_path(r'^esborrar/(?P<pk>\d+)/$', sortides_views.esborrar, name = 'sortides__sortides__esborrar', kwargs={'origen':'Meves'}),
    re_path(r'^esborrarGestio/(?P<pk>\d+)/$', sortides_views.esborrar, name = 'sortides__sortides__esborrarGestio', kwargs={'origen':'Gestio'}),
    re_path(r'^esborrarAll/(?P<pk>\d+)/$', sortides_views.esborrar, name = 'sortides__sortides__esborrarAll', kwargs={'origen':'All'}),

    re_path(r'^sortidaExcel/(?P<pk>\d+)/$', sortides_views.sortidaExcel, name = 'sortides__sortides__sortidaExcel'),



    re_path(r'^sortidaiCal/', sortides_views.sortidaiCal, name = 'sortides__sortides__ical'),

    re_path(r'^imprimir/(?P<pk>\d+)/(?P<din>\d+)$', sortides_views.imprimir, name = 'sortides__sortides__imprimir' ),

    re_path(r'^pagoOnline/(?P<pk>\d+)/$', sortides_views.pagoOnline, name='sortides__sortides__pago_on_line'),
    re_path(r'^pagoOnlineKO/(?P<pk>\d+)/$', sortides_views.pagoOnlineKO, name='sortides__sortides__pago_on_lineKO'),
    re_path(r'^passarella/(?P<pk>\d+)/$', sortides_views.passarella, name='sortides__sortides__passarella'),

    re_path(r'^retornTransaccio/(?P<pk>\d+)/$', sortides_views.retornTransaccio, name='sortides__sortides__retorn_transaccio'),

    re_path(r'^detallPagament/(?P<pk>\d+)/$', sortides_views.detallPagament, name='sortides__sortides__detall_pagament'),
    re_path(r'^detallPagament/(?P<pk>\d+)/(?P<tipus>\w+)/$', sortides_views.detallPagament, name='sortides__sortides__detall_pagament'),
    
    re_path(r'^quotes/$', sortides_views.assignaQuotes, name='gestio__quotes__assigna'),
    re_path(r'^quotes/(?P<curs>\d+)/(?P<tipus>\d+)/(?P<nany>\d+)/(?P<auto>.*)/$', sortides_views.quotesCurs, name='gestio__quotes__assigna'),
    re_path(r'^totals/$', sortides_views.totalsQuotes, name='gestio__quotes__descarrega'),
    re_path(r'^blanc/$', sortides_views.blanc, name="gestio__quotes__blanc"),

    re_path(r'^pagoEfectiu/(?P<pk>\d+)/$', sortides_views.pagoEfectiu, name='sortides__sortides__pago_efectiu'),

]