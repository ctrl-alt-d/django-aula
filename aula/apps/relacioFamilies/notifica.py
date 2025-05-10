# This Python file uses the following encoding: utf-8

import os
import sys
from django.conf import settings

from aula.apps.avaluacioQualitativa.models import AvaluacioQualitativa
from aula.apps.sortides.models import NotificaSortida, QuotaPagament
from aula.apps.sortides.utils_sortides import notifica_sortides
from django.core import mail
from django.core.mail import EmailMessage
from django.db import transaction
from aula.apps.usuaris.tools import creaNotifUsuari, ultimaNotificacio
from aula.apps.relacioFamilies.models import EmailPendent, DocAttach

def llista_pendents():
    if EmailPendent.objects.count()>0:
        print("Emails pendents:")
        for ep in EmailPendent.objects.all():
            print(ep)

def notifica_pendents():
    connection = mail.get_connection()
    # Obre la connexió
    connection.open()

    for ep in EmailPendent.objects.all():
        if not bool(ep.toemail):
            ep.delete()
            continue
        llistaemails=list(eval(ep.toemail))
        if len(llistaemails)==0:
            ep.delete()
            continue
        fitxers=DocAttach.objects.filter(email=ep.id)
        _, errors, pendents=enviaEmail(subject=ep.subject, body=ep.message, from_email=ep.fromemail, 
                                               bcc=llistaemails, connection=connection, attachments=fitxers)
        
        if errors>0:
            ep.toemail=str(pendents)
            ep.save()
            connection.close()
            print (u'Error enviant missatge pendent')
            print(ep)
            return
        if errors==0:
            ep.delete()
        
    # tanca la connexió
    connection.close()
    
def getNotifElements(elements, usuari, alumne):
    '''
    Busca elements que tenen pendent la notificació a aquest usuari i alumne
    elements  Query amb els elements a comprovar si n'hi ha de nous, és a dir, no notificats.
    usuari      User
    alumne    Alumne al que pertanyen els elements
    Retorna   Query amb els elements no notificats trobats.
    '''
    #DEPRECATED vvv
    # Per compatibilitat amb dades existents
    try:
        elements = elements.exclude( relacio_familia_notificada__isnull = False )
    except:
        pass
    #DEPRECATED ^^^
    Nous = elements.exclude(notificacions_familia__usuari = usuari, notificacions_familia__alumne = alumne)
    return Nous

def setNotifElements(elements, notificacio):
    '''
    Registra les notificacions als elements indicats
    '''
    for e in elements:
        e.set_notificacio(notificacio)
        
def notifica():
    from aula.apps.alumnes.models import Alumne
    from django.db import transaction
    from django.core.exceptions import ObjectDoesNotExist
    from django.db.models import Q
    from datetime import timedelta
    from datetime import datetime
    from aula.apps.presencia.models import EstatControlAssistencia
    from aula.apps.presencia.models import ControlAssistencia
    from django.core.mail import send_mail, EmailMessage
    from aula.apps.usuaris.models import Accio
    num_correus_no_enviats=0
    urlDjangoAula = settings.URL_DJANGO_AULA
    textTutorial = settings.CUSTOM_PORTAL_FAMILIES_TUTORIAL
    
    #with transaction.autocommit():  #deprecated on 1.8. Now is the default behaviuor.


    # TODO x App
    #
    # treure fa_2_setmanes
    # llista alumnes q_no_informat_adreca deprecated: tenen adreça informada o tenen token

    #actualitzo notificacions sortides:
    notifica_sortides()
    
    #Missatges pendents
    notifica_pendents()

    #Notificacions        
    ara = datetime.now()
    
    #fa_2_setmanes = ara - timedelta(  days = 14 )
    presencies_notificar = EstatControlAssistencia.objects.filter( codi_estat__in = ['F','R','J']  )
    q_no_es_baixa = Q(data_baixa__gte = ara ) | Q(data_baixa__isnull = True )
    #q_no_informat_adreca = Q( correu_relacio_familia_pare = '' ) & Q( correu_relacio_familia_mare = '' )

    llista_alumnes = (Alumne
                      .objects
                      .filter(q_no_es_baixa)
                      # .exclude( q_no_informat_adreca )
                      .values_list('pk', flat=True)
                      )
    avui = datetime.now().date()
    qualitatives_en_curs = [ q for q in AvaluacioQualitativa.objects.all()
                               if ( bool(q.data_obrir_portal_families) and
                                    bool( q.data_tancar_tancar_portal_families ) and
                                    q.data_obrir_portal_families <= avui <= q.data_tancar_tancar_portal_families
                                   )
                           ]


    for alumne_id in llista_alumnes:
        try:
            alumne = Alumne.objects.get( pk = alumne_id )
            # Bucle dels responsables i alumne
            # La configuració de notificació és diferent per cada responsable o alumne.
            destinataris = [(r, 'resp') for r in alumne.get_responsables() if r] + [(alumne, 'almn')]

            for usuari, tipus in destinataris:
                if not usuari: continue
                correu = usuari.get_correu_relacio()
                relacio_familia_darrera_notificacio = ultimaNotificacio(usuari.get_user_associat(), alumne)
                periodicitat_faltes = usuari.periodicitat_faltes
                periodicitat_incidencies = usuari.periodicitat_incidencies
                adreca_mail_informada = bool( correu )
                app_instalada = alumne.qr_portal_set.exists()
                
                usuari=usuari.get_user_associat()
    
                fa_n_dies = ara - timedelta(  days = periodicitat_faltes )
                noves_sortides = getNotifElements(NotificaSortida.objects.filter( alumne = alumne), usuari, alumne)
                if settings.CUSTOM_QUOTES_ACTIVES:
                    fa7dies = ara - timedelta( days = 7 )
                    en7dies = ara + timedelta( days = 7 )
                    '''
                    Selecciona pagaments no comunicats o pagaments pendents que no s'han comunicat en l'última setmana i 
                    la data límit ja ha passat o falten menys de 7 dies.
                    '''
                    nous_pagaments = QuotaPagament.objects.filter(
                            Q(notificacions_familia__moment__isnull=True) | (Q(notificacions_familia__moment__lt=fa7dies) & Q(quota__dataLimit__lt=en7dies)),
                            alumne=alumne, quota__importQuota__gt=0, pagament_realitzat=False)
                    #DEPRECATED vvv
                    nous_pagaments = nous_pagaments.exclude(data_hora_pagament__isnull=False).union(QuotaPagament.objects.filter(
                            Q(data_hora_pagament__isnull=True) | (Q(data_hora_pagament__lt=fa7dies) & Q(quota__dataLimit__lt=en7dies)),
                            alumne=alumne, quota__importQuota__gt=0, pagament_realitzat=False).exclude(notificacions_familia__moment__isnull=False))
                    #DEPRECATED ^^^
                else:
                    nous_pagaments = QuotaPagament.objects.none()
                noves_incidencies = getNotifElements(alumne.incidencia_set.all(), usuari, alumne)
                noves_expulsions = getNotifElements(alumne.expulsio_set.exclude( estat = 'ES'), usuari, alumne)
                noves_sancions = getNotifElements(alumne.sancio_set.filter( impres=True ), usuari, alumne)
                noves_faltes_assistencia = getNotifElements(ControlAssistencia.objects.filter( alumne = alumne, 
                                                                              estat__pk__in = presencies_notificar ), usuari, alumne)
                noves_respostes_qualitativa = getNotifElements( alumne
                                                .respostaavaluacioqualitativa_set
                                                .filter( qualitativa__in = qualitatives_en_curs ),
                                                usuari, alumne)
    
                #comprovo si hi ha novetats de presencia i incidències
                fa_dies_que_no_notifiquem = relacio_familia_darrera_notificacio is None or \
                                            relacio_familia_darrera_notificacio < fa_n_dies
                hiHaNovetatsPresencia =  periodicitat_faltes > 0 and \
                                         fa_dies_que_no_notifiquem and \
                                         noves_faltes_assistencia.exists()
                hiHaNovetatsQualitativa = noves_respostes_qualitativa.exists()
                hiHaNovetatsSortides = noves_sortides.exists()
                hiHaNovetatsPagaments = nous_pagaments.exists()
                hiHaNovetatsIncidencies = ( periodicitat_incidencies and
                                           ( noves_incidencies.exists() or noves_expulsions.exists() or noves_sancions.exists() )
                                          )
                hiHaNovetats =  (
                                 hiHaNovetatsQualitativa or
                                 hiHaNovetatsPresencia or
                                 hiHaNovetatsSortides and not settings.CUSTOM_SORTIDES_OCULTES_A_FAMILIES or
                                 hiHaNovetatsPagaments or
                                 hiHaNovetatsIncidencies
                                 )                  
                #print u'Avaluant a {0}'.format( alumne )
                enviatOK = False
                if hiHaNovetats and adreca_mail_informada:
                    #enviar correu i marcar novetats com a notificades:
                    assumpte = u"{0} - Notificacions al Djau - {1}".format(alumne.nom, settings.NOM_CENTRE )
                    missatge = [u"Aquest missatge ha estat enviat per un sistema automàtic. No responguis  a aquest e-mail, el missatge no serà llegit per ningú.",
                                u"",
                                u"Per qualsevol dubte/notificació posa't en contacte amb el tutor/a.",
                                u"",
                                u"Benvolgut/da,",
                                u"",
                                u"Us comuniquem que teniu noves notificacions de l'alumne {0} a l'aplicació Djau del centre {1}".format(alumne.nom+' '+alumne.cognoms, urlDjangoAula),
                                u"",
                                u"Recordeu que el vostre nom d'usuari és: {0}".format( usuari.username ),
                                u"",
                                u"Per qualsevol dubte que tingueu al respecte poseu-vos en contacte amb el tutor/a.",
                                u"",
                                u"Cordialment,",
                                u"",
                                settings.NOM_CENTRE,
                                u"",
                                u"{0}".format( textTutorial ),
                                ]
                    
                    try:                        
                        fromuser = settings.DEFAULT_FROM_EMAIL
                        if settings.DEBUG:
                            print (u'Enviant missatge a {0}'.format( usuari ))
                        email = EmailMessage(
                            assumpte,
                            u'\n'.join(missatge),
                            fromuser, #from
                            [],   #to
                            [correu],  #Bcc
                        )
                        email.send(fail_silently=False)
                        enviatOK = True
                    except:
                        if settings.DEBUG:
                            print (u'Error enviant missatge a {0}'.format( usuari ))
                        enviatOK = False
                        #Enviar msg a admins, ull! podem inundar de missatges si fallen tots els alumnes.
                        num_correus_no_enviats += 1
                #actualitzo QR's
                if hiHaNovetats:
                    n_tokens = alumne.qr_portal_set.update( novetats_detectades_moment = ara  )
                else:
                    n_tokens = None
    
                enviatOK = enviatOK or bool(n_tokens)  # s'ha enviat per algun dels mitjants
                if enviatOK:                    
                    notifAlumne=creaNotifUsuari(usuari, alumne, 'N')
                    setNotifElements(noves_sortides, notifAlumne)
                    setNotifElements(nous_pagaments, notifAlumne)
                    setNotifElements(noves_incidencies, notifAlumne)
                    setNotifElements(noves_expulsions, notifAlumne)
                    setNotifElements(noves_sancions, notifAlumne)
                    setNotifElements(noves_faltes_assistencia, notifAlumne)
                    setNotifElements(noves_respostes_qualitativa, notifAlumne)
                    
                    #LOGGING
                    Accio.objects.create( 
                            tipus = 'NF',
                            usuari = usuari,
                            l4 = False,
                            impersonated_from = None,
                            text = u"""Notifica Relació Famílies a {0}.""".format( usuari )
                        )   
                                
        except ObjectDoesNotExist:
            pass
    # si hi ha correus que han fallat informar a l'admin
    if num_correus_no_enviats > 0:
        raise Exception(u"No s'han pogut enviar {} missatges a famílies.".format(num_correus_no_enviats))


def pendentEmail(subject, body, from_email, bcc, attachments=None):
    '''
    Prepara un EmailPendent.
    bcc és una llista
    '''
    
    import unicodedata
    
    with transaction.atomic():
        ep=EmailPendent(subject=subject, message=body, fromemail=from_email, toemail=str(bcc))
        ep.save()
        if attachments:
            for f in attachments:
                # Elimina accents del nom de fitxer
                newname=unicodedata.normalize('NFKD',f.name).encode('ascii','ignore').decode('UTF-8')
                if f.name!=newname:
                    f.name=newname
                file_instance = DocAttach(fitxer=f)
                file_instance.email=ep
                file_instance.save()

class FitxerSuperaMida(Exception):
    def __init__(self, message, code=None, params=None):
        super().__init__(message, code, params)
        self.message = message
        self.code = code
        self.params = params
    
    def __str__(self):
        if hasattr(self, 'message') and bool(self.message):
            if isinstance(self.message, dict):
                return str(list(self.message))
            return str(self.message)
        else:
            return '(FitxerSuperaMida)La mida del fitxer supera el límit.'

def enviaEmail(subject, body, from_email, bcc, connection=None, attachments=None):
    '''
    Envia email a llista de destinataris bcc. Fracciona la llista de destinataris si fa falta.
    bcc és una llista.
    retorna quantitat ok, quantitat errors, llista destinataris pendents
    Provoca error FitxerSuperaMida si els fitxers adjunts són massa grans
    '''
    
    email = EmailMessage(subject, body, from_email, reply_to=[from_email], connection=connection)
    cont=0
    total=len(bcc)
    correctes=0
    errors=0
    maxdest=settings.CUSTOM_MAX_EMAIL_RECIPIENTS
    if maxdest<=0: maxdest=10
        
    if attachments:
        midatotal=0
        for f in attachments:
            if isinstance(f, DocAttach):
                name=f.fitxer.name
                content_type=None
                f=open(os.path.join(settings.PRIVATE_STORAGE_ROOT, name), 'rb')
            else:
                name=f.name
                content_type=f.content_type
            f.seek(0, os.SEEK_END)
            mida=f.tell()
            midatotal=midatotal+mida
            if mida<=settings.FILE_UPLOAD_MAX_MEMORY_SIZE and midatotal<=settings.FILE_UPLOAD_MAX_MEMORY_SIZE*3:
                f.seek(0)
                email.attach(name, f.read(), content_type)
            else:
                fitxerMB=settings.FILE_UPLOAD_MAX_MEMORY_SIZE/1024/1024
                totalMB=fitxerMB*3
                raise FitxerSuperaMida('Mida dels fitxers inadequada.'+ \
                            ' Un fitxer no pot superar {0} MB i tots els fitxers {1} MB.'.format(fitxerMB, totalMB))

    while cont<total:
        if cont+maxdest<=total:
            destinataris=bcc[cont:cont+maxdest]
        else:
            destinataris=bcc[cont:total]

        try:          
            email.to=[]
            email.cc=[]
            email.bcc=destinataris
            if settings.DEBUG:
                print (u'Enviant mail a {0} adreces'.format(len(destinataris)))
            if email.send()==1: correctes=correctes + len(destinataris)
            else:
                errors = total-cont
                return correctes, errors, bcc[cont:total]
        except Exception as e:
            print("Error a enviaEmail: "+str(e))
            errors = total-cont
            return correctes, errors, bcc[cont:total]
        
        cont=cont+maxdest    

    return correctes, 0, []

def notificaSenseCorreus():
    '''
    Selecciona els alumnes que no tenen cap email informat.
    Cada alumne ha de tenir correu_relacio_familia d'un dels responsables o correu propi si és major d'edat.
    Retorna Query amb els alumnes sense correu.
    '''
    
    from aula.apps.alumnes.models import Alumne
    from django.db.models import Q
    from datetime import datetime
      
    ara = datetime.now()
    q_no_es_baixa = Q(data_baixa__gte = ara ) | Q(data_baixa__isnull = True )
    
    #DEPRECATED vvv
    if not Alumne.objects.filter(responsables__correu_relacio_familia__isnull = False).exists():
        return Alumne.objects.none()
    #DEPRECATED ^^^
    alumnesSenseCorreu=Alumne.objects.filter(q_no_es_baixa).exclude(responsables__correu_relacio_familia__isnull = False)
    alumnesMajorsEdat=[]
    if alumnesSenseCorreu.exists():
        for a in alumnesSenseCorreu:
            if a.edat()>=18 and a.get_correu_relacio():
                # És major d'edat i té correu propi
                alumnesMajorsEdat.append(a.id)
    # Retorna alumnes majors sense correu o menors sense correu dels responsables
    return alumnesSenseCorreu.exclude(id__in=alumnesMajorsEdat)

def enviaEmailFamilies(assumpte, missatge, fitxers=None):
    '''Envia email a tots els correus d'alumnes
    
    Envia a tots el mateix assumpte, missatge i fitxers adjunts.
    Utilitza la configuració dels settings per al remitent
    Retorna la quantitat de correus als que s'ha enviat el missatge i la quantitat als que no
    Deixa pendents els que no s'han enviat. Els missatges pendents s'envien amb l'script notifica_families.sh. 
    '''
    
    from aula.apps.alumnes.models import Alumne
    from django.db.models import Q
    from datetime import datetime
      
    ara = datetime.now()
    q_no_es_baixa = Q(data_baixa__gte = ara ) | Q(data_baixa__isnull = True )
    
    sense_correu = notificaSenseCorreus()
    correus_alumnes = Alumne.objects.filter(q_no_es_baixa).difference(sense_correu)\
                                .values_list('responsables__correu_relacio_familia', 'correu')
    
    # crea llista de correus
    correus_alumnes=[item for sublist in list(correus_alumnes) for item in sublist if item]
    # elimina repetits
    correus_alumnes=list(set(correus_alumnes))

    connection = mail.get_connection()
    # Obre la connexió
    connection.open()
    
    subject = u"{0} - {1}".format(assumpte, settings.NOM_CENTRE )
    body = u'\n'.join(
        [u"{0}".format( missatge ),
                u"",
                u"",
                u"Aquest missatge ha estat enviat per un sistema automàtic. No responguis  a aquest e-mail, el missatge no serà llegit per ningú.",
                u"Per qualsevol dubte/notificació posa't en contacte amb el tutor/a.",
                u"",
                ]
        )
                   
    fromuser = settings.DEFAULT_FROM_EMAIL
    
    if settings.DEBUG:
        print (u'Enviant mail famílies a {0} adreces'.format(len(correus_alumnes)))
        # Enviament a ADMINS per a verificació si DEBUG
        correus_alumnes=correus_alumnes+[x[1] for x in settings.ADMINS]

    correctes, errors, pendents=enviaEmail(subject, body, from_email=fromuser, bcc=correus_alumnes, connection=connection, attachments=fitxers)
    if errors>0:
        pendentEmail(subject, body, from_email=fromuser, bcc=pendents, attachments=fitxers)
        
    # tanca la connexió
    connection.close()
    
    return correctes, errors
