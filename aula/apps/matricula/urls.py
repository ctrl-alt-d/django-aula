from django.urls import path
from aula.apps.matricula.views import OmpleDades, changeEstat, condicions, LlistaMatFinals, LlistaMatConf,\
    Confirma, VerificaConfirma, ActivaMatricula, blanc, ResumConfirmacions, matDobleview
            
app_name = 'matricula'

urlpatterns = [
    path('confirma/<int:nany>/', Confirma, name='relacio_families__matricula__confirma'),
    path('resum/', ResumConfirmacions, name='gestio__matricula__resum'),
    path('escollir/', matDobleview, name='relacio_families__matricula__escollir'),
    path('dades/', OmpleDades, name='relacio_families__matricula__dades'),
    path('activa/', ActivaMatricula, name='gestio__matricula__activa'),
    path('matricula/', LlistaMatConf, name='gestio__matricula__llistat'),
    path('matricula/<int:curs>/<int:nany>/<tipus>/', LlistaMatFinals, name='gestio__matricula__llistat'),
    path('matricula/<int:pk>/<int:curs>/<int:nany>/<tipus>/', VerificaConfirma, name='gestio__matricula__llistat'),
    path('changeestat/<int:pk>/<tipus>/', changeEstat, name='changeestat'),
    path('condicions/', condicions, name ="varis__condicions__matricula" )    ,
    path('blanc/', blanc, name="gestio__matricula__blanc"),
]
