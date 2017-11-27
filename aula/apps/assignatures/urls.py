from django.conf.urls import patterns

urlpatterns = patterns('aula.apps.assignatures.views',
    (r'^$', 'main_page'),
)

