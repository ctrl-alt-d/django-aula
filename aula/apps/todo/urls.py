from django.urls import re_path
from aula.apps.todo.views import list, edita, esborra

urlpatterns = [
    re_path(r'^list/$', list, name="varis__todo__list" ),
    re_path(r'^edita/$', edita, name="varis__todo__edit" ),
    re_path(r'^edita/(?P<pk>\d+)/$', edita, name="varis__todo__edit_by_pk" ),
    re_path(r'^esborra/(?P<pk>\d+)/$', esborra, name="varis__todo__del" ),
]