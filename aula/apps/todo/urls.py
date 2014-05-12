from django.conf.urls import patterns,url

urlpatterns = patterns('aula.apps.todo.views',
    url(r'^list/$', 'list', name="varis__todo__list" ),
    url(r'^edita/$', 'edita', name="varis__todo__edit" ),
    url(r'^edita/(?P<pk>\d+)/$', 'edita', name="varis__todo__edit_by_pk" ),
    url(r'^esborra/(?P<pk>\d+)/$', 'esborra', name="varis__todo__del" ),
)