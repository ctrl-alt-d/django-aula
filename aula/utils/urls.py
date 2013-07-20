from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('aula.utils.views',
                       
    url(r'^carregaInicial/$', 'carregaInicial',
        name ="administracio__configuracio__carrega_inicial" )    ,
                       
    url(r'^about/$', 'about',
        name ="varis__about__about" )    ,
                       
    url(r'^calendariDevelop/$', 'calendariDevelop',
        name ="help__calendari__calendari" )    ,

    url(r'^opcionsSincro/$', 'blanc',
        name ="administracio__sincronitza__blanc" )    ,



                       
)

