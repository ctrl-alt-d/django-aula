from django.urls import re_path
from aula.apps.extKronowin.views import sincronitzaKronowin,assignaGrups,assignaFranges,creaNivellCursGrupDesDeKronowin
urlpatterns = [
   re_path(r'^sincronitzaKronowin/$', sincronitzaKronowin,
       name="administracio__sincronitza__kronowin"),
                       
   re_path(r'^assignaGrups/$', assignaGrups,
       name="administracio__configuracio__assigna_grups_kronowin"),
                       
   re_path(r'^assignaFranges/$', assignaFranges,
       name="administracio__configuracio__assigna_franges_kronowin"),

   re_path(r'^creaNivellCursGrupDesDeKronowin/$', creaNivellCursGrupDesDeKronowin,
       name="administracio__configuracio__crea_grups_des_de_kronowin"),

]

