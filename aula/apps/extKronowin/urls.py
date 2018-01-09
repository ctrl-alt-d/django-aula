from django.conf.urls import url
from aula.apps.extKronowin.views import sincronitzaKronowin,assignaGrups,assignaFranges,creaNivellCursGrupDesDeKronowin
urlpatterns = [
   url(r'^sincronitzaKronowin/$', sincronitzaKronowin,
       name="administracio__sincronitza__kronowin"),
                       
   url(r'^assignaGrups/$', assignaGrups,
       name="administracio__configuracio__assigna_grups_kronowin"),
                       
   url(r'^assignaFranges/$', assignaFranges,
       name="administracio__configuracio__assigna_franges_kronowin"),

   url(r'^creaNivellCursGrupDesDeKronowin/$', creaNivellCursGrupDesDeKronowin,
       name="administracio__configuracio__crea_grups_des_de_kronowin"),

]

