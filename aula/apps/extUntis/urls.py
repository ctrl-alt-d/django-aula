from django.urls import re_path
from aula.apps.extUntis.views import sincronitzaUntis
urlpatterns = [
   re_path(r'^sincronitzaUntis/$', sincronitzaUntis,
       name="administracio__sincronitza__Untis"),

]

