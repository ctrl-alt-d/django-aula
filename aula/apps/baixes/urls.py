from django.urls import re_path
from   aula.apps.baixes import views as baixes_views

urlpatterns = [
    re_path(r'^feina/(?P<pk_imparticio>\d*)/$', baixes_views.feina,
     name="aula__horari__feina"),
                       
    re_path(r'^complementFormulariTria/$', baixes_views.complementFormulariTria,
     name="professorat__baixes__complement_formulari_tria")
                       ,
    re_path(r'^complementFormulariOmple/(?P<pk_professor>\d*)/(?P<dia>\d{2})/(?P<mes>\d{2})/(?P<year>\d{4})/$', baixes_views.complementFormulariOmple,
     name="professorat__baixes__complement_formulari_omple"),

    re_path(r'^complementFormulariImpresioTria/$', baixes_views.complementFormulariImpresioTria,
     name="professorat__baixes__complement_formulari_impressio_tria"),
                       
    re_path(r'^complementFormulariImprimeix/(?P<dia>\d{2})/(?P<mes>\d{2})/(?P<year>\d{4})/$', baixes_views.complementFormulariOmple,
     name="professorat__baixes__complement_formulari_imprimeix"),

    ]

