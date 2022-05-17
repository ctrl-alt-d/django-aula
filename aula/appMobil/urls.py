from django.conf.urls import url
from django.urls import re_path

from aula.appMobil import views as appmobil_views
from aula.appMobil.views import MyTokenObtainPairView

urlpatterns = [
    url(r'^login/$', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^notificacions/mes/(?P<mes>\d+)/$', appmobil_views.notificacions_mes, name='appmobil__api__notificacions_mes'),
    url(r'^notificacions/news/$', appmobil_views.notificacions_news, name='appmobil__api__notificacions_news'),
    url(r'^alumnes/dades/$', appmobil_views.alumnes_dades, name='appmobil__api__alumnes_dades'),

]