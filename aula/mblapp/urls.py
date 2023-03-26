# This Python file uses the following encoding: utf-8
from django.urls import re_path

from aula.mblapp import views as mblapp_views

urlpatterns = [
    re_path(r'^hello_api/$', mblapp_views.hello_api,
        name='mblapp__hello__api'),
    re_path(r'^hello_api_login/$', mblapp_views.hello_api_login,
        name='mblapp__hello__apilogin'),
    re_path(r'^hello_api_login_app/$', mblapp_views.hello_api_login_app,
            name='mblapp__hello__apiloginapp'),
]