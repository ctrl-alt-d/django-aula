from django.conf.urls.defaults import patterns,url

urlpatterns = patterns('aula.apps.extKronowin.views',
   url(r'^sincronitzaKronowin/$', 'sincronitzaKronowin',
       name="administracio__sincronitza__kronowin"),
                       
   url(r'^assignaGrups/$', 'assignaGrups',
       name="administracio__configuracio__assigna_grups_kronowin"),
                       
   url(r'^assignaFranges/$', 'assignaFranges',
       name="administracio__configuracio__assigna_franges_kronowin"),
)

