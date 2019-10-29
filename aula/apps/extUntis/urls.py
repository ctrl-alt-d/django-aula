from django.conf.urls import url
from aula.apps.extUntis.views import sincronitzaUntis
urlpatterns = [
   url(r'^sincronitzaUntis/$', sincronitzaUntis,
       name="administracio__sincronitza__Untis"),

]

