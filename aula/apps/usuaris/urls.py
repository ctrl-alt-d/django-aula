from django.conf.urls import patterns, url

urlpatterns = patterns('aula.apps.usuaris.views',
                       
    url(r'^canviDadesUsuari/$', 'canviDadesUsuari', 
     name="usuari__dades__canvi"),
                       
    url(r'^impersonacio/$', 'impersonacio', 
     name="usuari__impersonacio__impersonacio"),
              
    url(r'^resetPasswd/$', 'resetPasswd', 
     name="administracio__professorat__reset_passwd"),
              
    url(r'^canviDePasswd/$', 'canviDePasswd', 
     name="usuari__dades__canvi_passwd"),
              
    url(r'^resetImpersonacio/$', 'resetImpersonacio', 
     name="usuari__impersonacio__reset"),
              
    url(r'^elsProfessors/$', 'elsProfessors', 
     name="professorat__professors__list"),
              
    url(r'^login/$', 'loginUser', 
     name="nologin__usuari__login"),
              
    url(r'^recoverPasswd/(?P<username>\w{1,20})/(?P<oneTimePasswd>\w{1,50})/$', 'recoverPasswd', 
     name="nologin__usuari__recover_password"),
              
    url(r'^sendPasswdByEmail/$', 'sendPasswdByEmail', 
     name="nologin__usuari__send_pass_by_email"),

    url(r'^cercaUsuari/$', 'cercaUsuari',
     name="usuari__cerca"),
              
    
)

