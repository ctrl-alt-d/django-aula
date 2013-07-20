from django.conf.urls.defaults import patterns

urlpatterns = patterns('aula.apps.assignatures.views',
    (r'^$', 'main_page'),
)

