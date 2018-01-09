from django.conf.urls import url
from   aula.apps.baixes import views as baixes_views

urlpatterns = [
    url(r'^feina/(?P<pk_imparticio>\d*)/$', baixes_views.feina,
     name="aula__horari__feina"),
                       
    url(r'^complementFormulariTria/$', baixes_views.complementFormulariTria,
     name="professorat__baixes__complement_formulari_tria")
                       ,
    url(r'^complementFormulariOmple/(?P<pk_professor>\d*)/(?P<dia>\d{2})/(?P<mes>\d{2})/(?P<year>\d{4})/$', baixes_views.complementFormulariOmple,
     name="professorat__baixes__complement_formulari_omple"),

    url(r'^complementFormulariImpresioTria/$', baixes_views.complementFormulariImpresioTria,
     name="professorat__baixes__complement_formulari_impressio_tria"),
                       
    url(r'^complementFormulariImprimeix/(?P<dia>\d{2})/(?P<mes>\d{2})/(?P<year>\d{4})/$', baixes_views.complementFormulariOmple,
     name="professorat__baixes__complement_formulari_imprimeix"),

    ]

