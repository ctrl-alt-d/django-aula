# This Python file uses the following encoding: utf-8
import random
from aula.apps.usuaris.models import OneTimePasswd, Professor, Accio, AlumneUser, User2Professor, User2Alumne, ResponsableUser, User2Responsable, NotifUsuari
from datetime import datetime
from datetime import timedelta
from django.db.models import Q
from django.conf import settings
from aula.apps.alumnes.models import Alumne
from aula.apps.relacioFamilies.models import Responsable
import re
import dns.resolver
import smtplib
import imaplib
import email
from django.contrib.auth.models import User, Group
from aula.apps.missatgeria.models import Missatge
from aula.apps.missatgeria.missatges_a_usuaris import tipusMissatge, MAIL_REBUTJAT

def connectIMAP():
    '''
    Realitza connexió al servidor de correu segons les dades
    dels settings EMAIL_HOST_IMAP EMAIL_HOST_USER EMAIL_HOST_PASSWORD

    Retorna objecte IMAP4_SSL per accedir al correu o None si falla

    '''

    try:
        mail = imaplib.IMAP4_SSL(settings.EMAIL_HOST_IMAP)
        if mail:
            mail.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        return mail
    except:
        return None

def disconnectIMAP(mail):
    '''
    Desconnecta el servidor de correu imaplib.IMAP4_SSL mail

    '''

    if mail:
        try:
            mail.close()
            mail.logout()
        except:
            pass

def extractEmail(address):
    '''
    Comprova o recupera una adreça email de l'string address
    Només fa la comprovació sintàctica, si l'string és format per varies
    adreces potencials retorna la primera correcta

    Retorna True, adreçaOK si és vàlid
            False, address original si no correspon a email
            Exemples:
            "usuari@domini.com (Correu tutor 1) +34666555777"  -->  True, "usuari@domini.com"
            "usuari @ domini . com (Correu tutor 1)"  --> False, "usuari @ domini . com (Correu tutor 1)"

    '''

    addressToVerify=address.strip().lower()
    splitAddress = addressToVerify.split(' ')
    for a in splitAddress:
        # General Email Regex (RFC 5322 Official Standard)
        regex= '(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}'\
               '~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\['\
               '\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])'\
               '?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]'\
               '?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]'\
               '*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
        match = re.match(regex, a)
        if match:
            return True, a
    #Email Syntax Error
    return False, address

def testEmail(addressToVerify, testMailbox=False):
    '''
    Verifica si una adreça de correu és correcta
    Comprova sintaxis i domini vàlid.
    addressToVerify  string adreça que es vol verificar
    testMailbox si és True també consulta al servidor corresponent, només
    té en compte el cas 550 Non-existent email address. Altres casos no es consideren error.

    Retorna  0, adreçaOK  si s'ha obtingut una adreça vàlida
            -1, addressToVerify  si l'adreça és '' o None
            -2, addressToVerify  si sintaxis incorrecte
            -3, addressToVerify  si domini incorrecte
            -4, addressToVerify  si mailbox inexistent (codi 550)

    '''

    if not addressToVerify: return -1, addressToVerify

    valida, addressToVerify=extractEmail(addressToVerify)
    if not valida:
        return -2, addressToVerify

    splitAddress = addressToVerify.split('@')
    domain = str(splitAddress[1])
    try:
        records = dns.resolver.query(domain, 'MX')
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)
    except:
        #print('Domain Error',addressToVerify)
        return -3, addressToVerify

    if not testMailbox:
        return 0, addressToVerify

    # SMTP Conversation
    try:
        server = smtplib.SMTP(timeout=10)
        server.set_debuglevel(0)
        server.connect(mxRecord)
        server.helo(server.local_hostname)
        fromEmail=settings.DEFAULT_FROM_EMAIL.split(" ")
        fromEmail=fromEmail[len(fromEmail)-1]
        fromEmail=fromEmail[1:len(fromEmail)-1]

        code, _ = server.docmd("MAIL", "FROM:<%s>" % fromEmail)
        code, _ = server.docmd("RCPT", "TO:<%s>" % str(addressToVerify))

        server.quit()
        server.close()
    except:
        #print('Mailbox Error', addressToVerify);
        #No es pot identificar el problema, es considera vàlida
        return 0, addressToVerify

    if code == 550:
        # 550 Non-existent email address
        #print('Mailbox Error', addressToVerify, code);
        return -4, addressToVerify

    return 0, addressToVerify


def datemailTodatetime(dateEmail):
    '''
    Retorna objecte datetime a partir d'un string IMAP4 INTERNALDATE
    '''

    date=None
    if dateEmail:
        date_tuple=email.utils.parsedate_tz(dateEmail)
        if date_tuple:
            date=datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
    return(date)

def getEmailText(msg):
    '''
    Retorna el text del missatge dins de l'objecte email.message.Message msg
    '''

    for part in msg.walk():
        if part.get('content-disposition', '').startswith('attachment;'):
            continue
        if part.get_content_maintype() == 'text':
            charset = part.get_content_charset()
            text = part.get_payload(decode=True)
            subject=part.get('subject')
            if charset:
                try:
                    return str(subject)+":\n"+text.decode(charset, 'replace')
                except LookupError:
                    return str(subject)+":\n"+text.decode('ascii', 'ignore')
            return str(subject)+":\n"+text.decode(errors='ignore')
    return ''


def getMailsList(mail, num, dies):
    '''
    Retorna la llista dels identificadors de correus rebuts al
    servidor mail des del número num (no inclós) o els últims dies indicats.
    Es farà servir per al fetch de cada correu.
    mail connexió al servidor imaplib.IMAP4_SSL
    num int, numeració a partir de la qual volem els correus (num no inclòs)
    dies int, si num es None fa servir aquests dies per obtenir els correus

    Retorna la llista i últim identificador o None, None en cas d'error.

    '''

    if mail:
        # Prepara el command corresponent
        if num>0:
            #  rang mails  'num:*'  Ex:  2000:*   1:*
            cmd=str(num+1)+':*'
        else:
            #  desde data Ex: '(SENTSINCE "2-Feb-2020")'
            months=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            data=datetime.now()-timedelta(days=dies)
            data=str(data.day)+"-"+months[data.month-1]+"-"+str(data.year)
            cmd='(SENTSINCE "'+data+'")'
        #print(cmd)
        try:
            _, response_text = mail.select()
            ultim = int(response_text[0].decode("utf-8"))
            _ , dades = mail.search(None, cmd )
            mail_ids = dades[0]
            id_list = mail_ids.split()
            if id_list and len(id_list)>0:
                ultim = int(id_list[len(id_list) - 1].decode("utf-8")) #  search retorna bytes
                if num>=0 and ultim>num:
                    # Comprova que n'hi han nous emails
                    return id_list, ultim
            return None, ultim
        except Exception as e:
            print ("Error getMailsList:", str(e))
            return None, 0
    return None, 0

def informaDSN(destinataris,usuari,emailRetornat,motiu,data,url):
    '''
    Envia missatges Djau per cada destinatari. Informa de l'error de l'adreça email de l'usuari.
    destinataris  query d'usuaris (User)
    usuari  a qui fa referència el missatge, el propietari de l'adreça errònia (User o Alumne)
    emailRetornat string, adreça que ha rebutjat el correu
    motiu string, explicació original del servidor
    data datetime, en la qual el servidor va rebre el correu
    url string, enllaç per a fer el canvi de la configuració de l'usuari afectat
    Si l'usuari (no alumne) s'ha connectat al Djau des de la data aleshores també rep el missatge

    '''
    
    missatge = MAIL_REBUTJAT
    tipus_de_missatge = tipusMissatge(missatge)
    missatge = missatge.format(str(usuari) if usuari else "desconegut", emailRetornat, str(data), motiu)
    usuari_notificacions, new = User.objects.get_or_create( username = 'TP')
    if new:
        usuari_notificacions.is_active = False
        usuari_notificacions.first_name = u"Usuari Tasques Programades"
        usuari_notificacions.save()
    if not destinataris or not destinataris.exists() or not usuari:
        destinataris= Group.objects.get_or_create( name = 'administradors' )[0].user_set.all()
        url=geturlconf('ADM',usuari)
    msg = Missatge( remitent = usuari_notificacions, text_missatge = missatge,
                tipus_de_missatge = tipus_de_missatge, enllac=url )
    for d in destinataris:
        msg.envia_a_usuari( d , 'VI')

def geturlconf(tipus, usuari, responsable=None):
    '''
    Retorna la url per a poder fer el canvi de la configuració de l'usuari
    tipus: Qui ha d'accedir a la configuració, pot ser 'ADM' administrador,  'TUT' tutor, 'USU'  usuari
    usuari: A quin usuari s'ha de modificar la configuració (User o Alumne)
    responsable: És el responsable a qui s'ha de modificar la configuració o None.  
    Retorna string amb la url o '' si no existeix l'usuari o és el cas 'USU' per alumne.
    '''

    if usuari is None: return ''
    al=AlumneUser(pk=usuari.pk).getAlumne()
    if al or responsable:
        codi=al.pk
    else:
        codi=usuari.pk
    if tipus=='ADM':
        if responsable:
            url='/admin/relacioFamilies/responsable/{0}/change/'.format(responsable.pk) if responsable.pk else '' # administrador per responsable
        elif al:
            url='/admin/alumnes/alumne/{0}/change/'.format(codi) if codi else '' # administrador per alumne
        else:
            url='/admin/auth/user/{0}/change/'.format(codi) if codi else ''     # administrador per usuari no alumne
    else:
        if tipus=='TUT' and (al or responsable):
            url='/open/configuraConnexio/{0}/'.format(codi) if codi else '' # tutor per modificar alumne o responsable
        else:
            if tipus=='USU' and not al:
                url='/usuaris/canviDadesUsuari/'   # usuari no alumne
            else:
                url=''
    return url

def informa(emailRetornat, status, action, data, diagnostic, text):
    '''
    Envia notificacions per email retornat
    emailRetornat adreça que ha rebutjat el correu
    status codi d'error
    action actuació del servidor de correu
    data en la qual el servidor va rebre el correu
    diagnostic explicació del problema
    text  missatge del correu
    Si l'email retornat correspon a un alumne o responsable --> notifica al tutor
    Si correspon a un altre usuari --> notifica a l'usuari
    En tots els casos, inclosos desconeguts, notifica als administradors

    '''

    motiu=status+" "+ action +" "+ diagnostic
    administradors = Group.objects.get_or_create( name = 'administradors' )[0].user_set.all()
    correus = (Q( correu = emailRetornat ) | Q( responsables__correu_relacio_familia = emailRetornat))
    alumnes=Alumne.objects.filter(correus).filter(data_baixa__isnull = True).distinct()
    for almn in alumnes:
        # És un correu d'alumne o responsable
        tutors=almn.tutorsDelGrupDeLAlumne()
        usuari_almn=almn.get_user_associat()
        if almn.correu==emailRetornat:
            #Alumne
            informaDSN(tutors,usuari_almn,emailRetornat,motiu,data,
                       geturlconf('TUT', usuari_almn))
            informaDSN(administradors,usuari_almn,emailRetornat,motiu,data,
                       geturlconf('ADM', usuari_almn))
        for r in almn.get_responsables():
            #Responsables
            if r.correu_relacio_familia==emailRetornat:
                informaDSN(tutors,usuari_almn,emailRetornat,motiu,data,
                           geturlconf('TUT', usuari_almn, responsable=r))
                informaDSN(administradors,usuari_almn,emailRetornat,motiu,data,
                           geturlconf('ADM', usuari_almn, responsable=r))
    
    altres=User.objects.filter(email = emailRetornat)
    if altres.exists():
        # És un correu d'usuari no alumne ni responsable
        for usuari in altres:
            informaDSN(usuari,usuari,emailRetornat,motiu,data,
                    geturlconf('USU',usuari))
            informaDSN(administradors,usuari,emailRetornat,motiu,data,
                       geturlconf('ADM',usuari))
    if not alumnes.exists() and not altres.exists():
        # És desconegut, pot correspondre a casos d'alumnes en procés de matrícula
        informaDSN(administradors,None,emailRetornat,motiu,data, geturlconf('ADM',None))
    
def setUltimControl(num):
    '''
    Registra a la base de dades una Accio amb el número de l'últim
    email verificat
    num número de l'últim email. string o bytes.
    '''

    if num is None: return 
    if type(num) is bytes:
        num=num.decode("utf-8")
    usuari_notificacions, new = User.objects.get_or_create( username = 'TP')
    if new:
        usuari_notificacions.is_active = False
        usuari_notificacions.first_name = u"Usuari Tasques Programades"
        usuari_notificacions.save()
    Accio.objects.create(
            tipus = 'DS',
            usuari = usuari_notificacions,
            l4 = False,
            impersonated_from = None,
            text = u"Comprovació emails rebutjats. ;"+str(num)
            )

def getUltimControl():
    '''
    Retorna el número de l'últim email verificat segons els registres d'Accio
    o retorna None si no n'hi ha cap
    Retorna un int o None
    '''

    control=Accio.objects.filter(tipus='DS').order_by( '-moment' )
    if control.exists():
        ultimFetch=int(control[0].text.split(";")[1])
    else:
        ultimFetch=0
    return ultimFetch

def checkDSN(msg):
    '''
    Comprova si el missatge correspon a un Delivery Status Notification
    Informa si és el cas i mostra les dades a Ajuda i Avisos
    '''
    
    if (msg.is_multipart() and len(msg.get_payload()) > 1 and
        msg.get_payload(1).get_content_type() == 'message/delivery-status'):
        # email is DSN
        text=''
        for m in msg.get_payload():
            if m.get_content_type() == 'message/rfc822':
                text=getEmailText(m)
                break
        for dsn in msg.get_payload(1).get_payload():
            if dsn.get_content_type() == 'text/plain':
                fr=dsn.get('Final-Recipient')
                if fr: emailRetornat=fr.split(';')[1].strip()
                st=dsn.get('status')
                if st: status=st
                act=dsn.get('action')
                if act: action=act
                ad=dsn.get('Arrival-Date')
                if ad: data=datemailTodatetime(ad)
                dc=dsn.get('diagnostic-code')
                try:
                    if dc and type(dc) is str: diagnostic=dc.split(';')[1]
                    else: diagnostic=str(dc)
                except:
                    diagnostic = 'Unknown error'
        informa(emailRetornat, status, action, data, diagnostic, text)  
        
def controlDSN(dies=1):
    '''
    Verifica si s'han rebut correus d'error delivery status notification (DSN) a partir
    de l'ultima vegada. Si és el primer control aleshores comprova els últims dies passats per paràmetre.
    Per cada correu identifica destinatari erroni i informa al tutor o a l'administrador de Django.

    Retorna True si ok o False si no pot accedir al correu o no pot finalitzar totes les verificacions.
    '''
    
    if settings.EMAIL_BACKEND and (settings.EMAIL_BACKEND == 'django_gsuite_email.GSuiteEmailBackend' \
        or settings.EMAIL_BACKEND == 'gmailapi_backend.service.GmailApiBackend'):
        return gmailcontrolDSN(dies)
    else:
        return imapcontrolDSN(dies) 
    
def imapcontrolDSN(dies):
    '''
    Verifica si s'han rebut correus d'error delivery status notification (DSN) a partir
    de l'ultima vegada. Si és el primer control aleshores comprova els últims dies passats per paràmetre.
    Per cada correu identifica destinatari erroni i informa al tutor o a l'administrador de Django.

    Retorna True si ok o False si no pot accedir al correu o no pot finalitzar totes les verificacions.
    '''

    mail=connectIMAP()
    if mail is None: return False
    ultimFetch=getUltimControl()
    id_list, id_last=getMailsList(mail, ultimFetch, dies)
    if not bool(id_list):
        if id_last>=ultimFetch: setUltimControl(id_last)
        return False
    i=0
    while i<len(id_list):
        try:
            num=id_list[i]
            status, data = mail.fetch(num, '(RFC822)')
        except:
            if i>0: setUltimControl(id_list[i-1])
            return False
        i=i+1
        # the content data at the '(RFC822)' format comes on
        # a list with a tuple with header, content, and the closing
        # byte b')'
        for response_part in data:
            # so if its a tuple...
            if isinstance(response_part, tuple):
                # we go for the content at its second element
                # skipping the header at the first and the closing
                # at the third
                msg = email.message_from_bytes(response_part[1])
                checkDSN(msg)
    if len(id_list)>0: setUltimControl(id_list[len(id_list)-1])
    disconnectIMAP(mail)
    return True

def getMessages(service, ultimFetch, dies):
    '''
    Retorna la llista dels identificadors de correus rebuts
    des del número ultimFetch o dels últims dies indicats.
    service connexió a l'API de Gmail
    ultimFetch int, numeració a partir de la qual volem els correus (no inclòs)
    dies int, si ultimFetch es None fa servir aquests dies per obtenir els correus

    Retorna la llista i l'últim identificador.

    '''
    
    from datetime import date
    from operator import itemgetter
    today = date.today()
    last = today - timedelta(days=dies)
    # Dates have to formatted in YYYY/MM/DD format for gmail
    query = "after: {0}".format(last.strftime('%Y/%m/%d'))
    result = service.users().messages().list(userId='me', q=query, labelIds = ['INBOX', ]).execute()
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, labelIds = ['INBOX', ], pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    lista=[]
    for m in messages:
        historyId = service.users().messages().get(userId='me', id=m.get('id')).execute()['historyId']
        if ultimFetch is None or int(historyId) > ultimFetch:
            #Selecciona els nous
            m['historyId']=historyId
            lista.append(m)
    #Ordena la llista, quedarà de més antic a més modern
    lista = sorted(lista, key=itemgetter('historyId'))
    return lista, int(service.users().getProfile(userId='me').execute()['historyId'])
    
def gmailcontrolDSN(dies):
    '''
    Verifica si s'han rebut correus d'error delivery status notification (DSN) a partir
    de l'ultima vegada. Si és el primer control aleshores comprova els últims dies passats per paràmetre.
    Per cada correu identifica destinatari erroni i informa al tutor o a l'administrador de Django.

    Retorna True si ok o False si no pot accedir al correu o no pot finalitzar totes les verificacions.
    '''
    # for encoding/decoding messages in base64
    from base64 import urlsafe_b64decode    
    from django.core.mail import get_connection
    
    mail = get_connection(fail_silently=True)
    if mail is None: return False
    if mail.open() is None: return False
    ultimFetch = getUltimControl()
    id_list, id_last = getMessages(mail.connection, ultimFetch, dies)
    if not bool(id_list):
        if id_last>ultimFetch: setUltimControl(id_last)
        return False
    i=0
    for msg in id_list:
        try:
            data = mail.connection.users().messages().get(userId='me', id=msg['id'], format='raw').execute()
        except:
            if i>0:
                historyId = mail.connection.users().messages().get(userId='me', id=id_list[i-1]['id']).execute()['historyId'] 
                setUltimControl(historyId)
            return False
        i=i+1
        for response_part,value in data.items():
            if response_part=='raw':
                msg_str = str(urlsafe_b64decode(value.encode('ASCII')), 'utf-8')
                msg = email.message_from_string(msg_str)
                checkDSN(msg)
    if len(id_list)>0:
        historyId = mail.connection.users().messages().get(userId='me', id=id_list[len(id_list)-1]['id']).execute()['historyId'] 
        setUltimControl(historyId)
    mail.close()
    return True

def enviaOneTimePasswd( email ):
    nUsuaris = 0
    nErrors = 0
    errors = []
    responsables = Responsable.objects.filter( correu_relacio_familia__iexact = email )
    for resp in responsables:
        resultat = enviaOneTimePasswdAlumne( resp, email )
        nUsuaris += 1
        if resultat['errors']:
            nErrors += 1
            errors.append( ', '.join( resultat['errors'] ) )

    alumnes = Alumne.objects.filter( correu__iexact = email )
    for alumne in alumnes:
        resultat = enviaOneTimePasswdAlumne( alumne, email )
        nUsuaris += 1
        if resultat['errors']:
            nErrors += 1
            errors.append( ', '.join( resultat['errors'] ) )

    professors = Professor.objects.filter( email__iexact = email )
    for professor in professors:
        resultat = enviaOneTimePasswdProfessor(professor)
        nUsuaris += 1
        if resultat['errors']:
            nErrors += 1
            errors.append( ', '.join( resultat['errors'] ) )

    return   {  'errors':   [ u"Hi ha hagut errors recuperant la contrasenya:",  ] + errors
                            if nErrors>0 else [],
                'infos':    [ u"{0} correus enviats.".format( nUsuaris - nErrors  ),
                              u"Comprovi la seva bústia de correu." ]
                            if nUsuaris - nErrors > 0 else [],
                'warnings': [ u"No és possible recuperar aquest compte.",
                              u"Revisi l'adreça informada." ,
                              u"Contacti amb el tutor o amb el cap d'estudis."  ]
                            if nUsuaris == 0 else [], }

def enviaOneTimePasswdAlumne( alumne, email, force = False ):

    usuari = alumne.get_user_associat().username
    actiu = alumne.get_user_associat().is_active

    infos = []
    warnings = []
    errors = []

    #comprovo que no s'hagi enviat més de 2 recuperacions en un dia:
    fa_24h = datetime.now() - timedelta( days = 1 )
    total_enviats = OneTimePasswd.objects.filter( usuari =alumne.user_associat, moment_expedicio__gte = fa_24h  ).count()
    if total_enviats >= 3:
        errors.append( u'Màxim número de missatges enviats a aquest correu durant les darrers 24h.' )
    elif alumne.esBaixa():
        warnings.append( u"Aquest usuari és baixa. No se li pot enviar codi d'accés.")
        errors.append( u"Error enviant codi de recuperació d'accés")
    else:
        #preparo el codi a la bdd:
        clau = str( random.randint( 100000, 999999) ) + str( random.randint( 100000, 999999) )
        OneTimePasswd.objects.create(usuari = alumne.user_associat, clau = clau)

        #envio missatge:
        urlDjangoAula = settings.URL_DJANGO_AULA
        url = "{0}/usuaris/recoverPasswd/{1}/{2}".format( urlDjangoAula, usuari, clau )
        txtCapcelera = u"Enviat missatge a {0} .".format( email )
        infos.append(txtCapcelera)
        assumpte = u"{0} - Recuperar/Obtenir accés a l'aplicatiu Djau de {1}".format(alumne.nom, settings.NOM_CENTRE )
        missatge = [
                     u"Aquest missatge ha estat enviat per un sistema automàtic. No responguis  a aquest e-mail, el missatge no serà llegit per ningú.",
                     u"",
                     u"Per qualsevol dubte/notificació posa't en contacte amb el tutor/a.",
                     u"",
                     u"La pàgina principal del portal de relació amb famílies de l'Institut és:",
                     u"{0}".format( urlDjangoAula ),
                     u"El vostre codi d'usuari és: **  {0}  **".format( usuari ),
                     u"",
                     u"Si no disposeu de contrasenya, podeu obtenir accés al portal de {0} amb aquest enllaç:".format(alumne.nom),
                     u"{0}".format( url ),
                     u"",
                     u"Aquest enllaç romandrà operatiu durant 30 minuts.",
                     u"",
                     u"""Instruccions:""",
                     u"Punxeu o copieu l'enllaç al vostre navegador. El sistema us tornarà a informar del vostre nom d'usuari ({0}) ".format( usuari ),
                     u"i us preguntarà quina contrasenya voleu. Com a mesura suplementària de seguretat us demanarà també alguna altra dada.",
                     u"Recordeu usuari i contrasenya per futures connexions al portal de relació amb famílies.",
                     u"  ",
                     u"Cordialment,",
                     u"  ",
                     settings.NOM_CENTRE,
                    ]

        from django.core.mail import send_mail
        enviatOK = True
        try:
            fromuser = settings.DEFAULT_FROM_EMAIL
            send_mail(assumpte,
                      u'\n'.join( missatge ),
                      fromuser,
                      [ email ],
                      fail_silently=False)
            infos.append('Missatge enviat correctament.')
        except:
            infos = []
            enviatOK = False

        if not enviatOK:
            errors.append( u'Hi ha hagut un error enviant la passwd.'  )

    return   {  'errors':  errors, 'infos': infos, 'warnings':warnings, }



def enviaOneTimePasswdProfessor( professor, force = False ):

    usuari = professor.getUser().username
    correu = professor.getUser().email

    infos = []
    warnings = []
    errors = []

    #comprovo que no s'hagi enviat més de 2 recuperacions en un dia:
    fa_24h = datetime.now() - timedelta( days = 1 )
    total_enviats = OneTimePasswd.objects.filter( usuari =professor.getUser(), moment_expedicio__gte = fa_24h  ).count()
    if total_enviats >= 3:
        errors.append( u'Màxim número de missatges enviats a aquest correu durant les darrers 24h.' )
    elif not correu:
        warnings.append( u"Comprova que l'adreça electrònica d'aquest professor estigui informada")
        errors.append( u"Error enviant codi de recuperació d'accés" )
#    elif not professor.getUser().is_active:
#        warnings.append( u"Aquest professor no és actiu. No se li pot enviar codi d'accés.")
#        errors.append( u"Error enviant codi de recuperació d'accés")
    else:
        #preparo el codi a la bdd:
        clau = str( random.randint( 100000, 999999) ) + str( random.randint( 100000, 999999) )
        OneTimePasswd.objects.create(usuari = professor.getUser(), clau = clau)

        #envio missatge:
        urlDjangoAula = settings.URL_DJANGO_AULA
        url = "{0}/usuaris/recoverPasswd/{1}/{2}".format( urlDjangoAula, usuari, clau )
        txtCapcelera = u"Enviat missatge a {0} .".format(
                                correu
                                                                )
        infos.append(txtCapcelera)
        missatge = [
                     u"La pàgina principal del programa de relació famílies de l'Institut és:",
                     u"{0}".format( urlDjangoAula ),
                     u"El vostre codi d'usuari és: **  {0}  **".format( usuari ),
                     u"",
                     u"Si no disposeu de contrasenya, podeu obtenir accés al portal de {0} amb aquest enllaç:".format(professor.getUser().first_name),
                     u"{0}".format( url ),
                     u"",
                     u"Aquest enllaç romandrà operatiu durant 30 minuts.",
                     u"",
                     u"""Instruccions:""",
                     u"Punxeu o copieu l'enllaç al vostre navegador. El sistema us tornarà a informar del vostre nom d'usuari ({0}) ".format( usuari ),
                     u"i us preguntarà quina contrasenya voleu. Com a mesura suplementària de seguretat us demanarà també alguna altra dada.",
                     u"Recordeu usuari i contrasenya per futures connexions a l'aplicatiu.",
                     u"  ",
                     settings.NOM_CENTRE,
                    ]

        from django.core.mail import send_mail
        enviatOK = True
        try:
            fromuser = settings.DEFAULT_FROM_EMAIL
            send_mail(u"Accés a l'aplicatiu de {0}".format( settings.NOM_CENTRE),
                      u'\n'.join( missatge ),
                      fromuser,
                      [  correu ] ,
                      fail_silently=False)
            infos.append('Missatge enviat correctament.')
        except:
            infos = []
            enviatOK = False

        if not enviatOK:
            errors.append( u'Hi ha hagut un error enviant la passwd.'  )

    return   {  'errors':  errors, 'infos': infos, 'warnings':warnings, }


def enviaBenvingudaAlumne( alumne, force = False ):

    correusFamilia = alumne.get_correus_relacio_familia()

    infos = []
    warnings = []
    errors = []

    if not correusFamilia:
        if alumne.edat()<18:
            warnings.append( u"Comprova que l'adreça electrònica d'almenys un dels responsables estigui informada")
        else:
            warnings.append( u"Comprova que l'adreça electrònica de l'alumne o un dels responsables estigui informada")
        errors.append( u"Error enviant correu de benvinguda" )
    elif alumne.esBaixa():
        warnings.append( u"Aquest alumne és baixa. No se li pot enviar codi d'accés.")
        errors.append( u"Error enviant correu de benvinguda")
    else:
        #envio missatge:
        urlDjangoAula = settings.URL_DJANGO_AULA
        textTutorial = settings.CUSTOM_PORTAL_FAMILIES_TUTORIAL

        txtCapcelera = u"Enviat missatge a {0} .".format(
                                u", ".join( correusFamilia )
                                                                )
        infos.append(txtCapcelera)
        assumpte = u"Alta a l'aplicatiu Djau de {0}".format( settings.NOM_CENTRE )

        missatge = settings.CUSTOM_MESSAGE_BENVINGUDA_FAMILIES



        from django.core.mail import send_mail
        enviatOK = True
        try:
            fromuser = settings.DEFAULT_FROM_EMAIL
            send_mail(assumpte,
                      u'\n'.join( missatge ),
                      fromuser,
                      correusFamilia,
                      fail_silently=False)
            infos.append('Missatge enviat correctament.')
        except:
            infos = []
            enviatOK = False

        if not enviatOK:
            errors.append( u'Hi ha hagut un error enviant la benvinguda.'  )

    return   {  'errors':  errors, 'infos': infos, 'warnings':warnings, }


def bloqueja( alumne, motiu ):
    actiu =  alumne.esta_relacio_familia_actiu()

    infos = []
    warnings = []
    errors = []

    if actiu and alumne.get_user_associat() is not None and alumne.user_associat.is_active:
        alumne.user_associat.is_active = False
        alumne.user_associat.save()
        alumne.motiu_bloqueig = motiu
        #alumne.credentials = credentials
        alumne.save()
        infos.append(u'Accés desactivat amb èxit.')
    return   {  'errors':  errors, 'infos': infos, 'warnings':warnings, }

def desbloqueja( alumne ):
    actiu =  alumne.esta_relacio_familia_actiu()

    infos = []
    warnings = []
    errors = []

    if not actiu:
        #Si no té user associat en creo un:
        usuari_associat = alumne.get_user_associat()

        #Desbloquejo:
        esPotDesbloquejar = alumne.get_correus_relacio_familia() \
                            and usuari_associat is not None \
                            and not alumne.esBaixa()
        if esPotDesbloquejar:
            usuari_associat.is_active = True
            usuari_associat.save()
            alumne.motiu_bloqueig = u''
            #alumne.credentials = credentials
            alumne.save()
            infos.append(u'Accés activat amb èxit.')
        else:
            errors.append(u'No es pot desbloquejar, comprova que té adreça de correu dels pares i no és baixa.')

    return   {  'errors':  errors, 'infos': infos, 'warnings':warnings, }

def getRol(usuari, request):
    '''
    Comprova quin tipus d'usuari correspon.
    Si es tracta d'un alumne retorna None, None, Alumne
    Si es tracta d'un responsable retorna None, Responsable, Alumne o None, Responsable, None
    Si es tracta d'un professor retorna Professor, None, None
    Si no es tracta de cap cas retorna None, None, None
    '''
    if usuari.username.startswith("almn"):
        alumne = User2Alumne( usuari )
        return None, None, alumne
    elif usuari.username.startswith("resp"):
        responsable = User2Responsable( usuari )
        if responsable and responsable.get_alumnes_associats():
            if "alumne_actual" in request.session:
                pk = request.session["alumne_actual"] 
                alumne = Alumne.objects.filter( pk = pk )
                if alumne.exists():
                    alumne=alumne.first()
                    return None, responsable, alumne
        return None, responsable, None
    professor = User2Professor( usuari )
    return professor, None, None

def creaNotifUsuari(usuari, alumne, tipus='N'):
    '''
    Apunta una notificació a l'usuari-alumne.
    tipus 'N' Notificació, 'R' Revisió
    '''
    notificacio=NotifUsuari()
    notificacio.usuari=usuari
    notificacio.alumne=alumne
    notificacio.tipus=tipus
    notificacio.save()
    return notificacio

def ultimaNotificacio(usuari, alumne):
    '''
    usuari
    alumne
    retorna la data-hora de l'última notificació o
    retorna None si no existeix
    '''
    if usuari: ultima=NotifUsuari.objects.filter(usuari=usuari, alumne=alumne, tipus='N').order_by('-moment').first()
    else: ultima=NotifUsuari.objects.filter(alumne=alumne, tipus='N').order_by('-moment').first()
    if ultima: return ultima.moment
    #DEPRECATED vvv
    # Per compatibilitat amb dades existents
    try:
        if alumne.relacio_familia_darrera_notificacio:
            return alumne.relacio_familia_darrera_notificacio
    except:
        pass
    #DEPRECATED ^^^
    return None

def set_notificacio(element, notificacio, tipus='N'):
    if not notificacio: return
    notifs=element.notificacions_familia.filter(usuari=notificacio.usuari, tipus=tipus)
    if notifs:
        for n in notifs: element.notificacions_familia.remove(n)
    element.notificacions_familia.add(notificacio)

def set_revisio(element, revisio):
    set_notificacio(element, revisio, tipus='R')

def get_notif_revisio(element, usuari, fmt_data=None):
    '''
    Retorna str, str amb notificació, revisió de l'usuari
    '''
    if not fmt_data: fmt_data='%d/%m/%Y %H:%M'
    revisc=notifc=''
    #DEPRECATED vvv
    # Per compatibilitat amb dades existents
    try:
        if hasattr(element, "data_hora_pagament"):
            if element.data_hora_pagament:
                #data_hora_pagament serveix per a saber moment del pagament o moment de notificació
                if element.pagament_realitzat:
                    revisc=element.data_hora_pagament.strftime(fmt_data)
                else:
                    notifc=element.data_hora_pagament.strftime(fmt_data)
        else:
            if element.relacio_familia_revisada:
                revisc=element.relacio_familia_revisada.strftime(fmt_data)
            if element.relacio_familia_notificada:
                notifc=element.relacio_familia_notificada.strftime(fmt_data)
            else:
                notifc=revisc
    except:
        pass
    #DEPRECATED ^^^
    if User2Professor( usuari ):
        notif = element.notificacions_familia.filter(tipus='N').order_by('moment').first()
        revis = element.notificacions_familia.filter(tipus='R').order_by('moment').first()
    else:
        notif = element.notificacions_familia.filter(usuari=usuari, tipus='N').order_by('-moment').first()
        revis = element.notificacions_familia.filter(usuari=usuari, tipus='R').order_by('-moment').first()
    if notif: notif=notif.moment.strftime(fmt_data)
    else: notif=notifc
    if revis: revis=revis.moment.strftime(fmt_data)
    else: revis=revisc
    return notif, revis
    