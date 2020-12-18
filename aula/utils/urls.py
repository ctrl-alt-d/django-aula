from django.conf.urls import url
from aula.utils.views import carregaInicial, calendariDevelop, blanc, about, pagamentOnLine, initDB, estadistiques

urlpatterns = [
                       
    url(r'^carregaInicial/$', carregaInicial,
        name ="administracio__configuracio__carrega_inicial" )    ,
                       
    url(r'^about/$', about,
        name ="varis__about__about" )    ,

    url(r'^estadistiques/$', estadistiques,
        name="varis__estadistiques__estadistiques"),

    url(r'^pagamentOnLine/$', pagamentOnLine,
        name ="varis__pagament__pagament_online" )    ,
                       
    url(r'^calendariDevelop/$', calendariDevelop,
        name ="help__calendari__calendari" )    ,

    url(r'^opcionsSincro/$', blanc,
        name ="administracio__sincronitza__blanc" )    ,

    url(r'^initDB/$', initDB,
        name ="administracio__init__inicialitzaDB" )    ,

]
