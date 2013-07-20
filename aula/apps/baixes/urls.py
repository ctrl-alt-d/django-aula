from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('aula.apps.baixes.views',
    url(r'^feina/(?P<pk_imparticio>\d*)/$', 'feina',
     name="aula__horari__feina"),
                       
    url(r'^complementFormulariTria/$', 'complementFormulariTria',
     name="professorat__baixes__complement_formulari_tria")
                       ,
    url(r'^complementFormulariOmple/(?P<pk_professor>\d*)/(?P<dia>\d{2})/(?P<mes>\d{2})/(?P<year>\d{4})/$', 'complementFormulariOmple',
     name="professorat__baixes__complement_formulari_omple"),

    url(r'^complementFormulariImpresioTria/$', 'complementFormulariImpresioTria',
     name="professorat__baixes__complement_formulari_impressio_tria"),
                       
    url(r'^complementFormulariImprimeix/(?P<dia>\d{2})/(?P<mes>\d{2})/(?P<year>\d{4})/$', 'complementFormulariOmple',
     name="professorat__baixes__complement_formulari_imprimeix"),

    )

