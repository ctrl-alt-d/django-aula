from django.conf.urls import url
from aula.apps.usuaris import views as usuaris_views

urlpatterns = [
                       
    url(r'^canviDadesUsuari/$', usuaris_views.canviDadesUsuari,
     name="usuari__dades__canvi"),
                       
    url(r'^impersonacio/$', usuaris_views.impersonacio,
     name="usuari__impersonacio__impersonacio"),
              
    url(r'^resetPasswd/$', usuaris_views.resetPasswd,
     name="administracio__professorat__reset_passwd"),
              
    url(r'^canviDePasswd/$', usuaris_views.canviDePasswd,
     name="usuari__dades__canvi_passwd"),
              
    url(r'^resetImpersonacio/$', usuaris_views.resetImpersonacio,
     name="usuari__impersonacio__reset"),
              
    url(r'^elsProfessors/$', usuaris_views.elsProfessors,
     name="professorat__professors__list"),
              
    url(r'^login/$', usuaris_views.loginUser,
     name="nologin__usuari__login"),
              
    url(r'^recoverPasswd/(?P<username>\w{1,20})/(?P<oneTimePasswd>\w{1,50})/$', usuaris_views.recoverPasswd,
     name="nologin__usuari__recover_password"),
              
    url(r'^sendPasswdByEmail/$', usuaris_views.sendPasswdByEmail,
     name="nologin__usuari__send_pass_by_email"),

    url(r'^cercaProfessor/$', usuaris_views.cercaProfessor,
     name="gestio__professor__cerca"),
              
    url(r'^detallProfessorHorari/(?P<pk>\d+)/(?P<detall>\w+)/$', usuaris_views.detallProfessorHorari,
     name="gestio__professor__cercaresultat"),  

    url(r'^integraCalendari/$', usuaris_views.integraCalendari,
     name="gestio__calendari__integra"),

    url(r'^ElMeuCalendari/(?P<clau>[0-9a-f-]+)/$', usuaris_views.comparteixCalendari,
     name="gestio__calendari__comparteix"),

    url(r'^detallProfessorHorari/$', usuaris_views.blanc,
     name="gestio__blanc__blanc"),
]