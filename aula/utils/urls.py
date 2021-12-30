from django.urls import re_path
from aula.utils.views import carregaInicial, calendariDevelop, blanc, about, pagamentOnLine, initDB, estadistiques

urlpatterns = [
                       
    re_path(r'^carregaInicial/$', carregaInicial,
        name ="administracio__configuracio__carrega_inicial" )    ,
                       
    re_path(r'^about/$', about,
        name ="varis__about__about" )    ,

    re_path(r'^estadistiques/$', estadistiques,
        name="varis__estadistiques__estadistiques"),

    re_path(r'^pagamentOnLine/$', pagamentOnLine,
        name ="varis__pagament__pagament_online" )    ,
                       
    re_path(r'^calendariDevelop/$', calendariDevelop,
        name ="help__calendari__calendari" )    ,

    re_path(r'^opcionsSincro/$', blanc,
        name ="administracio__sincronitza__blanc" )    ,

    re_path(r'^initDB/$', initDB,
        name ="administracio__init__inicialitzaDB" )    ,

]
