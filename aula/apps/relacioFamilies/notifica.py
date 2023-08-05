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
from aula.apps.usuaris.tools import informaNoCorreus, geturlconf
from aula.apps.relacioFamilies.models import EmailPendent, DocAttach

def notifica_pendents():
    connection = mail.get_connection()
    # Obre la connexió
    connection.open()

    for ep in EmailPendent.objects.all():
        if not bool(ep.toemail):
            ep.delete()
            continue
        fitxers=DocAttach.objects.filter(email=ep.id)
        _, errors, pendents=enviaEmail(subject=ep.subject, body=ep.message, from_email=ep.fromemail, 
                                               bcc=list(eval(ep.toemail)), connection=connection, attachments=fitxers)
        if errors>0:
            ep.toemail=pendents
            ep.save()
            print (u'Error enviant missatge pendent a {0}'.format(ep.toemail))
            return
        if errors==0:
            #TODO  missatge informatiu, falta usuari
            ep.delete()
        
    # tanca la connexió
    connection.close()
    
def notifica():
    from aula.apps.alumnes.models import Alumne
    from django.db import transaction
    from django.core.exceptions import ObjectDoesNotExist
    from django.db.models import Q
    from datetime import timedelta
    from django.utils.datetime_safe import datetime
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

            adreca_mail_informada = bool( alumne.correu_relacio_familia_pare or alumne.correu_relacio_familia_mare )
            app_instalada = alumne.qr_portal_set.exists()

            fa_n_dies = ara - timedelta(  days = alumne.periodicitat_faltes )
            noves_sortides = NotificaSortida.objects.filter( alumne = alumne, relacio_familia_notificada__isnull = True  )
            if settings.CUSTOM_QUOTES_ACTIVES:
                #data_hora_pagament serveix per a saber moment del pagament o moment de notificació
                fa7dies = ara - timedelta( days = 7 )
                en7dies = ara + timedelta( days = 7 )
                '''
                Selecciona pagaments no comunicats o pagaments pendents que no s'han comunicat en l'última setmana i 
                la data límit ja ha passat o falten menys de 7 dies.
                '''
                nous_pagaments = QuotaPagament.objects.filter(
                    Q(data_hora_pagament__isnull=True) | (Q(data_hora_pagament__lt=fa7dies) & Q(quota__dataLimit__lt=en7dies)),
                    alumne=alumne, quota__importQuota__gt=0, pagament_realitzat=False)
            else:
                nous_pagaments = QuotaPagament.objects.none()
            noves_incidencies = alumne.incidencia_set.filter( relacio_familia_notificada__isnull = True  )
            noves_expulsions = alumne.expulsio_set.exclude( estat = 'ES').filter(    relacio_familia_notificada__isnull = True  )
            noves_sancions = alumne.sancio_set.filter( impres=True, relacio_familia_notificada__isnull = True  )
            noves_faltes_assistencia = ControlAssistencia.objects.filter( alumne = alumne, 
                                                                          #impartir__dia_impartir__gte = fa_2_setmanes,
                                                                          relacio_familia_notificada__isnull = True,
                                                                          estat__pk__in = presencies_notificar )
            noves_respostes_qualitativa = ( alumne
                                            .respostaavaluacioqualitativa_set
                                            .filter( qualitativa__in = qualitatives_en_curs )
                                            .filter( relacio_familia_notificada__isnull = True )
                                            )

            #comprovo si hi ha novetats de presencia i incidències
            fa_dies_que_no_notifiquem = alumne.relacio_familia_darrera_notificacio is None or \
                                        alumne.relacio_familia_darrera_notificacio < fa_n_dies
            hiHaNovetatsPresencia =  alumne.periodicitat_faltes > 0 and \
                                     fa_dies_que_no_notifiquem and \
                                     noves_faltes_assistencia.exists()
            hiHaNovetatsQualitativa = noves_respostes_qualitativa.exists()
            hiHaNovetatsSortides = noves_sortides.exists()
            hiHaNovetatsPagaments = nous_pagaments.exists()
            hiHaNovetatsIncidencies = ( alumne.periodicitat_incidencies and
                                       ( noves_incidencies.exists() or noves_expulsions.exists() or noves_sancions.exists() )
                                      )
            hiHaNovetats =  (
                             hiHaNovetatsQualitativa or
                             hiHaNovetatsPresencia or
                             hiHaNovetatsSortides or
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
                            u"Recordeu que el vostre nom d'usuari és: {0}".format( alumne.get_user_associat().username ),
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
                        print (u'Enviant missatge a {0}'.format( alumne ))
                    email = EmailMessage(
                        assumpte,
                        u'\n'.join(missatge),
                        fromuser, #from
                        [],   #to
                        alumne.get_correus_relacio_familia(),  #Bcc
                    )
                    email.send(fail_silently=False)
                    enviatOK = True
                except:
                    if settings.DEBUG:
                        print (u'Error enviant missatge a {0}'.format( alumne ))
                    enviatOK = False
                    #Enviar msg a admins, ull! podem inundar de missatges si fallen tots els alumnes.
                    num_correus_no_enviats += 1
            #actualitzo QR's
            if hiHaNovetats:
                n_tokens = alumne.qr_portal_set.update( novetats_detectades_moment = ara  )

            enviatOK = enviatOK or bool(n_tokens)  # s'ha enviat per algun dels mitjants
            if enviatOK:                    
                noves_sortides.update( relacio_familia_notificada = ara )
                #data_hora_pagament serveix per a saber moment del pagament o moment de notificació
                nous_pagaments.update( data_hora_pagament = ara )
                noves_incidencies.update( relacio_familia_notificada = ara )
                noves_expulsions.update( relacio_familia_notificada = ara )
                noves_sancions.update( relacio_familia_notificada = ara )
                noves_faltes_assistencia.update( relacio_familia_notificada = ara )
                noves_respostes_qualitativa.update( relacio_familia_notificada = ara )
                #if hiHaNovetatsPresencia:
                alumne.relacio_familia_darrera_notificacio = ara
                alumne.save()

                #LOGGING
                Accio.objects.create( 
                        tipus = 'NF',
                        usuari = alumne.get_user_associat(),
                        l4 = False,
                        impersonated_from = None,
                        text = u"""Notifica Relació Famílies a {0}.""".format( alumne )
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
    
    with transaction.atomic():
        ep=EmailPendent(subject=subject, message=body, fromemail=from_email, toemail=str(bcc))
        ep.save()
        if attachments:
            for f in attachments:
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
                f=open(os.path.join(settings.PRIVATE_STORAGE_ROOT, name))
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
        except:
            errors = total-cont
            return correctes, errors, bcc[cont:total]
        
        cont=cont+maxdest    

    return correctes, 0, []

def enviaEmailFamilies(assumpte, missatge, fitxers=None):
    '''Envia email a tots els correus d'alumnes
    
    Envia a tots el mateix assumpte, missatge i fitxers adjunts.
    Utilitza la configuració dels settings per al remitent
    Retorna la quantitat de correus als que s'ha enviat el missatge i la quantitat als que no
    Deixa pendents els que no s'han enviat. Els missatges pendents s'envien amb l'script notifica_families.sh. 
    '''
    
    from aula.apps.alumnes.models import Alumne
    from django.db.models import Q
    from django.utils.datetime_safe import datetime
      
    ara = datetime.now()
    q_no_es_baixa = Q(data_baixa__gte = ara ) | Q(data_baixa__isnull = True )
    q_no_informat_adreca = Q( correu_relacio_familia_pare = '' ) & Q( correu_relacio_familia_mare = '' ) & \
                    Q(correu_tutors='') & Q(rp1_correu='')&Q(rp2_correu='')&Q(correu='')
    
    # Notifica als tutors els alumnes que no tenen cap email
    alumnesSenseCorreu=Alumne.objects.filter(q_no_es_baixa).filter( q_no_informat_adreca )

    if alumnesSenseCorreu.exists():
        for a in alumnesSenseCorreu:
            tutors=a.tutorsDelGrupDeLAlumne()
            informaNoCorreus(tutors,a.get_user_associat(),geturlconf('TUT',a.get_user_associat()))

    correus_alumnes = Alumne.objects.filter(q_no_es_baixa).values_list(
        'correu_relacio_familia_pare','correu_relacio_familia_mare')
    
    # crea llista de correus
    correus_alumnes=[item for sublist in list(correus_alumnes) for item in sublist]
    # elimina repetits
    correus_alumnes=list(dict.fromkeys(correus_alumnes))
    # elimina buit
    correus_alumnes.remove('')

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
