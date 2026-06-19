# This Python file uses the following encoding: utf-8
from django.urls import re_path

from aula.mblapp import views as mblapp_views

urlpatterns = [
    re_path(r"^hello_api/$", mblapp_views.hello_api, name="mblapp__hello__api"),
    re_path(
        r"^hello_api_login/$",
        mblapp_views.hello_api_login,
        name="mblapp__hello__apilogin",
    ),
    re_path(
        r"^hello_api_login_app/(?P<alumne_id>\d+)/$",
        mblapp_views.hello_api_login_app,
        name="mblapp__hello__apiloginapp",
    ),
    re_path(
        r"^notificacions/mes/(?P<mes>\d+)/(?P<alumne_id>\d+)/$",
        mblapp_views.notificacions_mes,
        name="appmobil__api__notificacions_mes",
    ),
    re_path(
        r"^notificacions/news/(?P<alumne_id>\d+)/$",
        mblapp_views.notificacions_news,
        name="appmobil__api__notificacions_news",
    ),
    re_path(
        r"^alumnes/dades/(?P<alumne_id>\d+)/$",
        mblapp_views.alumnes_dades,
        name="appmobil__api__alumnes_dades",
    ),
    re_path(r"^sortides/(?P<alumne_id>\d+)/$", mblapp_views.sortides, name="appmobil__api__sortides"),
    re_path(
        r"^sortides/(?P<pk>\d+)/(?P<alumne_id>\d+)/$",
        mblapp_views.detallSortida,
        name="appmobil__api__detall_sortida",
    ),
    re_path(r"^alumnes_associats/$", mblapp_views.alumnes_associats, name="appmobil__api__alunnes_associats"),
]
