from django.urls import re_path
from aula.apps.usuaris import views as usuaris_views

urlpatterns = [
                       
    re_path(r'^canviDadesUsuari/$', usuaris_views.canviDadesUsuari,
     name="usuari__dades__canvi"),
                       
    re_path(r'^impersonacio/$', usuaris_views.impersonacio,
     name="usuari__impersonacio__impersonacio"),
              
    re_path(r'^resetPasswd/$', usuaris_views.resetPasswd,
     name="administracio__professorat__reset_passwd"),
              
    re_path(r'^canviDePasswd/$', usuaris_views.canviDePasswd,
     name="usuari__dades__canvi_passwd"),
              
    re_path(r'^resetImpersonacio/$', usuaris_views.resetImpersonacio,
     name="usuari__impersonacio__reset"),
              
    re_path(r'^elsProfessors/$', usuaris_views.elsProfessors,
     name="professorat__professors__list"),
              
    re_path(r'^login/$', usuaris_views.loginUser,
     name="nologin__usuari__login"),
              
    re_path(r'^recoverPasswd/(?P<username>\w{1,20})/(?P<oneTimePasswd>\w{1,50})/$', usuaris_views.recoverPasswd,
     name="nologin__usuari__recover_password"),
              
    re_path(r'^sendPasswdByEmail/$', usuaris_views.sendPasswdByEmail,
     name="nologin__usuari__send_pass_by_email"),

    re_path(r'^cercaProfessor/$', usuaris_views.cercaProfessor,
     name="gestio__professor__cerca"),
              
    re_path(r'^detallProfessorHorari/(?P<pk>\d+)/(?P<detall>\w+)/$', usuaris_views.detallProfessorHorari,
     name="gestio__professor__cercaresultat"),  

    re_path(r'^integraCalendari/$', usuaris_views.integraCalendari,
     name="gestio__calendari__integra"),

    re_path(r'^ElMeuCalendari/(?P<clau>[0-9a-f-]+)/$', usuaris_views.comparteixCalendari,
     name="gestio__calendari__comparteix"),

    re_path(r'^detallProfessorHorari/$', usuaris_views.blanc,
     name="gestio__blanc__blanc"),
]