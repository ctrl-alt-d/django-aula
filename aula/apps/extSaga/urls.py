from django.urls import re_path
from aula.apps.extSaga.views import sincronitzaSaga,assignaGrups

urlpatterns = [
   re_path(r'^sincronitzaSaga/$', sincronitzaSaga,
       name="administracio__sincronitza__saga"),
                       
   re_path(r'^assignaGrups/$', assignaGrups,
       name="administracio__configuracio__assigna_grups_saga"),
                       
]

