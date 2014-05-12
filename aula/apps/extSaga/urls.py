from django.conf.urls import patterns,url

urlpatterns = patterns('aula.apps.extSaga.views',
   url(r'^sincronitzaSaga/$', 'sincronitzaSaga',
       name="administracio__sincronitza__saga"),
                       
   url(r'^assignaGrups/$', 'assignaGrups',
       name="administracio__configuracio__assigna_grups_saga"),
                       
)

