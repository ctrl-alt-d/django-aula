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
    re_path(r'^capture_token_api/$', mblapp_views.capture_token_api,
            name='mblapp__api__capture_token_api'),
    re_path(r'^syncro_data_api/$', mblapp_views.syncro_data_api,
            name='mblapp__api__syncro_data_api'),

]