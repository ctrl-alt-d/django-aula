from django.urls import path
from aula.apps.matricula.views import OmpleDades, changeEstat, condicions, LlistaMatFinals, LlistaMatConf,\
            Confirma, VerificaConfirma, ActivaMatricula, blanc, ResumConfirmacions
            
app_name = 'matricula'

urlpatterns = [
    path('confirma/<int:nany>/', Confirma, name='relacio_families__matricula__confirma'),
    path('resum/', ResumConfirmacions, name='gestio__resum__matricula'),
    path('dades/', OmpleDades, name='relacio_families__matricula__dades'),
    path('activa/', ActivaMatricula, name='gestio__activa__matricula'),
    path('matricula/', LlistaMatConf, name='gestio__llistat__matricula'),
    path('matricula/<int:curs>/<int:nany>/<tipus>/', LlistaMatFinals, name='gestio__llistat__matricula'),
    path('matricula/<int:pk>/<int:curs>/<int:nany>/<tipus>/', VerificaConfirma, name='gestio__llistat__matricula'),
    path('changeestat/<int:pk>/<tipus>/', changeEstat, name='changeestat'),
    path('condicions/', condicions, name ="varis__condicions__matricula" )    ,
    path('blanc/', blanc, name="gestio__blanc__matricula"),
]
