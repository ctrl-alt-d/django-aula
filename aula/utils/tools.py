# This Python file uses the following encoding: utf-8

#----write pdf-------------------------------------
from django import http
from django.template.loader import get_template
from django.template import Context
from django.conf import settings

from io import StringIO
import cgi
from django.core.validators import validate_ipv4_address
from django.core.exceptions import ValidationError
from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.http import HttpRequest
from importlib import import_module
from threading import Thread
from django.contrib.auth.models import User
from django.utils.datetime_safe import datetime

try:
    import ho.pisa as pisa
except:
    pass

#--------------------------------------------------

def unicode(text, codi=None):
    return str(text)

def calculate_my_time_off(user):
    if user.is_anonymous:
        return settings.CUSTOM_TIMEOUT
    else:
        m=(settings.CUSTOM_TIMEOUT_GROUP.get(g.name, settings.CUSTOM_TIMEOUT) for g in user.groups.all())
        if bool(m):
            return max(m)
        return settings.CUSTOM_TIMEOUT


def getClientAdress( request ):
    
    ip = request.get_host()
    
    try:
        validate_ipv4_address( ip )
    except ValidationError:
        ip = ''
    
    return ip
    
#         #TODO:  HttpRequest.get_host()  at https://docs.djangoproject.com/en/dev/ref/request-response/
#     try:
#         FORWARDED_FOR_FIELDS = [
#             'REMOTE_ADDR',
#             'HTTP_X_FORWARDED_FOR',
#             'HTTP_X_FORWARDED_HOST',
#             'HTTP_X_FORWARDED_SERVER',
#         ]
#         for field in FORWARDED_FOR_FIELDS:
#             if field in request.META:
#                 if ',' in request.META[field]:
#                     parts = request.META[field].split(',')
#                     request.META[field] = parts[-1].strip()
#         client_address = request.META['HTTP_X_FORWARDED_FOR']
#     except:
#         client_address = request.META['REMOTE_ADDR']
#         
#     return client_address

def lowpriority():
    """ Set the priority of the process to below-normal."""

    pass
    
def getSoftColor( obj ):
    strc = unicode( obj ) + u'con mucha marcha'
    i = 0
    j = 77
    for s in strc:
        i += ( 103 * ord( s ) ) % 2001
        j = j % 573 + i * 5
    i = i*i
    
    gros = 200 + i%55
    mitja1 = 100 + j%155 
    mitja2 = 150 + (i+j)%105
    
    color=(None,None,None)
    if i%3 == 0:
        if i%2 ==0:
            color = ( gros, mitja1, mitja2 )
        else: 
            color = ( gros, mitja2, mitja1 )
    elif i%3 == 1:
        if i%2 ==0:
            color = ( mitja1, gros, mitja2 )
        else: 
            color = ( mitja2, gros, mitja1 )
    elif i%3 == 2:
        if i%2 ==0:
            color = ( mitja1, mitja2, gros )
        else:
            color = ( mitja2, mitja1, gros )
        
    return u'#{0:02X}{1:02X}{2:02X}'.format( color[0], color[1], color[2] )


def getImpersonateUser( request ):
    user = request.session['impersonacio'] if  request.session.has_key('impersonacio') else request.user
    l4 = request.session['l4'] if  request.session.has_key('l4') else False
    return ( user, l4, )

def getRealUser( request ):
    return request.user

def sessioImpersonada( request ):
    (user, _ ) = getImpersonateUser(request)
    return request and request.user.is_authenticated and request.user.pk != user.pk

class classebuida(object):
    pass

class llista(list):
    def compte(self):
        return self.__len__()
    def __init__(self, *args, **kwargs):
        super(llista,self).__init__(*args,**kwargs)    

class diccionari(dict):
    def compte(self):
        return self.__len__()
    def itemsEnOrdre(self):
        return iter(sorted(self.items()))
    def __init__(self, *args, **kwargs):
        super(dict,self).__init__(*args,**kwargs)    



def add_secs_to_time(timeval, secs_to_add):
    import datetime
    dummy_date = datetime.date(1, 1, 1)
    full_datetime = datetime.datetime.combine(dummy_date, timeval)
    added_datetime = full_datetime + datetime.timedelta(seconds=secs_to_add)
    return added_datetime.time()





def write_pdf(template_src, context_dict):
    
        
    template = get_template(template_src)
    #template = Template(filename = template_src, input_encoding = "utf-8")
    context = Context(context_dict)
    html  = template.render(context)
    result = StringIO.StringIO()
    pdf = pisa.pisaDocument(StringIO.StringIO( html.encode("utf-8")), dest=result, encoding='UTF-8', link_callback=fetch_resources)
    if not pdf.err:
        response = http.HttpResponse( result.getvalue(), mimetype='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=qualitativa.pdf'
    else:
        response = http.HttpResponse('''Gremlin's ate your pdf! %s''' % cgi.escape(html))

    
    return response

def fetch_resources(uri, rel):
    import os.path
    from django.conf import settings
    path = os.path.join(settings.MEDIA_ROOT, uri.replace(settings.MEDIA_URL, ""))
    return path

def obtenirMotorBD():
    #Obtenir el nom del motor de la BD.
    motorBD = None
    try:
        motorBD = settings.DATABASES['default']['ENGINE']
    except:
        raise Exception("BD per defecte no trobada.")
    return motorBD

def executaAmbOSenseThread(objecteThread):
    # type: (Thread) -> None
    #Executa el thread de forma convencional o executa sense threads.
    #No podem usar els threads en cas de treballar amb sqlite3. (O almenys no ho podem fer fàcilment.)
    if obtenirMotorBD() == 'django.db.backends.sqlite3':
        #No hi ha multithread en SQLITE3. Executo sense el thread.
        objecteThread.run()
    else:
        objecteThread.start()

def initComplet():
    from aula.apps.alumnes.models import Alumne,  Curs, Grup, Nivell
    from aula.apps.incidencies.models import Sancio, Expulsio, Incidencia
    from aula.apps.presencia.models import Impartir, ControlAssistencia, NoHaDeSerALAula
    from aula.apps.baixes.models import Feina
    from aula.apps.horaris.models import Horari, Festiu
    from aula.apps.aules.models import ReservaAula
    from aula.apps.avaluacioQualitativa.models import ItemQualitativa, AvaluacioQualitativa, RespostaAvaluacioQualitativa
    from aula.apps.extEsfera.models import Grup2Aula as esfgrup2aula
    from aula.apps.extSaga.models import Grup2Aula as saggrup2aula
    from aula.apps.extKronowin.models import Grup2Aula as krogrup2aula, Franja2Aula
    from aula.apps.extUntis.models import Agrupament
    from aula.apps.tutoria.models import SeguimentTutorial, ResumAnualAlumne, SeguimentTutorialPreguntes, SeguimentTutorialRespostes, Actuacio, Tutor, TutorIndividualitzat, CartaAbsentisme
    from aula.apps.assignatures.models import Assignatura
    from aula.apps.sortides.models import Sortida, Pagament, NotificaSortida
    from aula.apps.missatgeria.models import Missatge, DetallMissatge, Destinatari
    from aula.apps.usuaris.models import Accio
    from django.db.models import Q
    
    try:
        avui=datetime.now()
        
        #Modifica data per evitar restricció per antiguitat
        Incidencia.objects.update(dia_incidencia=avui.date())
        Incidencia.objects.all().delete()
        Expulsio.objects.all().delete()
        Sancio.objects.all().delete()
        ControlAssistencia.objects.all().delete()
        Feina.objects.all().delete()
        Impartir.objects.all().delete()
        Horari.objects.all().delete()
        Festiu.objects.all().delete()
        ReservaAula.objects.all().delete()
        RespostaAvaluacioQualitativa.objects.all().delete()
        ItemQualitativa.objects.all().delete()
        AvaluacioQualitativa.objects.all().delete()
        esfgrup2aula.objects.all().delete()
        saggrup2aula.objects.all().delete()
        krogrup2aula.objects.all().delete()
        Franja2Aula.objects.all().delete()
        Agrupament.objects.all().delete()
        NotificaSortida.objects.all().delete()
        Pagament.objects.all().delete()
        Sortida.objects.all().delete()
        NoHaDeSerALAula.objects.all().delete()

        #Modifica data per evitar restricció per antiguitat
        Actuacio.objects.update(moment_actuacio=avui)
        Actuacio.objects.all().delete()
        CartaAbsentisme.objects.all().delete()
        SeguimentTutorialRespostes.objects.all().delete()
        SeguimentTutorialPreguntes.objects.all().delete()
        SeguimentTutorial.objects.all().delete()
        ResumAnualAlumne.objects.all().delete()
        Tutor.objects.all().delete()
        TutorIndividualitzat.objects.all().delete()
        Assignatura.objects.all().delete()
        Destinatari.objects.all().delete()
        DetallMissatge.objects.all().delete()
        Missatge.objects.all().delete()
        Accio.objects.all().delete()
    except Exception as e:
        return ["Error:"+str(e)]
    
    # crea grup altres si no existeix
    nivell, nnivell=Nivell.objects.get_or_create(nom_nivell='ALL')
    if (nnivell):
        nivell.descripcio_nivell='ALL'
        nivell.save()
    curs, ncurs=Curs.objects.get_or_create(nivell=nivell, nom_curs='1')
    if (ncurs):
        curs.nom_curs_complert="ALL-1"
    curs.data_inici_curs=None
    curs.data_fi_curs=None
    curs.save()
    grup, ngrup=Grup.objects.get_or_create(curs=curs, nom_grup='altres')
    if (ngrup):
        grup.descripcio_grup='altres'
        grup.save()


    alt=Grup.objects.get(descripcio_grup='altres')
    #Passa tots els alumnes a grup altres
    Alumne.objects.all().update(grup=alt)
    
    #Esborra alumnes que són baixa
    es_baixa =  Q(data_baixa__isnull = False ) & Q(data_baixa__lt = avui )
    Alumne.objects.filter(es_baixa).delete()
    # Esborra usuaris alumne sense alumne associat
    User.objects.filter(username__startswith='almn',alumne__isnull=True).delete()
    
    #Esborra els grups actuals menys 'altres'
    Grup.objects.exclude(descripcio_grup='altres').delete()
    Curs.objects.filter(grup__isnull=True).delete()
    Nivell.objects.filter(curs__isnull=True).delete()
    
    return []
 
def init_session(session_key):
    """
    Initialize same session as done for ``SessionMiddleware``.
    """
    engine = import_module(settings.SESSION_ENGINE)
    return engine.SessionStore(session_key)


def allLogout(user=None):
    """
    Read all available users and all available not expired sessions. Then
    logout from each session.
    """
    start = datetime.now()
    request = HttpRequest()
 
    sessions = Session.objects.filter(expire_date__gt=start)

    for session in sessions:
        username = session.get_decoded().get('_auth_user_id')
        if user is None or str(user.id)!=str(username):
            #  Logout de l'usuari si no és el que executa el procés
            request.session = init_session(session.session_key)
            logout(request)

def disableLogins(user):
    # Llista d'usuaris actius, excepte l'usuari que executa el procés
    actius=User.objects.filter(is_active=True).exclude(pk=user.id).values_list('id')
    usuaris_actius=[item for sublist in list(actius) for item in sublist]
    # Impedeix que els usuaris puguin fer Login
    User.objects.filter(pk__in=usuaris_actius).update(is_active=False)
    # Logout de tots els usuaris excepte el que executa el procés
    allLogout(user)
    return usuaris_actius
         
def enableLogins(usuaris_actius):
    # Torna a deixar actius a tots els usuaris de la llista
    User.objects.filter(pk__in=usuaris_actius).update(is_active=True)

def closeDB():
    #Tanca les connexions amb la base de dades
    from django.db import connections
    for conn in connections.all():
        conn.close()

class processInitComplet(Thread):
    
    def __init__ (self, user):
        Thread.__init__(self)
        self.user = user
      
    def run(self):        
        from aula.apps.missatgeria.missatges_a_usuaris import FI_INITDB, ERROR_INITDB, tipusMissatge
        from aula.apps.missatgeria.models import Missatge

        warnings=[]
        infos=[]

        usuaris_actius=disableLogins(self.user)
        # Incialitza tota la base de dades
        errors=initComplet()
        enableLogins(usuaris_actius)

        if not bool(errors):
            infos.append(u'Inicialització finalitzada')
            missatge = FI_INITDB
        else:
            infos.append(u'Errors a la inicialització')
            missatge = ERROR_INITDB

        #Deixar missatge a la base de dades (utilitzar self.user )
        tipus_de_missatge = tipusMissatge(missatge)
        msg = Missatge( 
                    remitent= self.user, 
                    text_missatge = missatge,
                    tipus_de_missatge = tipus_de_missatge)
        msg.afegeix_errors( errors )
        msg.afegeix_warnings(warnings)
        msg.afegeix_infos(infos)    
        importancia = 'VI' if len( errors )> 0 else 'IN'
        msg.envia_a_usuari(self.user, importancia=importancia)
        
        #Tanca les connexions del thread amb la base de dades
        closeDB()
