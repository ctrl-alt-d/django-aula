from django.conf.urls import url
from aula.apps.extSaga.views import sincronitzaSaga,assignaGrups

urlpatterns = [
   url(r'^sincronitzaSaga/$', sincronitzaSaga,
       name="administracio__sincronitza__saga"),
                       
   url(r'^assignaGrups/$', assignaGrups,
       name="administracio__configuracio__assigna_grups_saga"),
                       
]

