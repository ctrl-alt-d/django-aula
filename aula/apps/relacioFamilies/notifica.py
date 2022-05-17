# This Python file uses the following encoding: utf-8

import os
import sys
from django.conf import settings

from aula.apps.avaluacioQualitativa.models import AvaluacioQualitativa
from aula.apps.sortides.models import NotificaSortida, QuotaPagament
from aula.apps.sortides.utils_sortides import notifica_sortides
from django.core.mail import EmailMessage
from aula.apps.usuaris.tools import informaNoCorreus, geturlconf
from aula.apps.relacioFamilies.models import EmailPendent

def notifica_pendents():
    for ep in EmailPendent.objects.all():
        r=0
        try:
            email = EmailMessage(subject=ep.subject, body=ep.message, from_email=ep.fromemail, reply_to=[ep.fromemail], bcc=eval(ep.toemail))
            r=email.send(fail_silently=False)
        except Exception as e:
            print (u'Error {0} enviant missatge pendent a {1}'.format(e, eval(ep.toemail)))
            continue
        if r==1: ep.delete()

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
        
    urlDjangoAula = settings.URL_DJANGO_AULA
    textTutorial = settings.CUSTOM_PORTAL_FAMILIES_TUTORIAL
    
    #with transaction.autocommit():  #deprecated on 1.8. Now is the default behaviuor.
        
    #actualitzo notificacions sortides:
    notifica_sortides()
    
    #Missatges pendents
    notifica_pendents()

    #Notificacions        
    ara = datetime.now()
    
    fa_2_setmanes = ara - timedelta(  days = 14 )
    presencies_notificar = EstatControlAssistencia.objects.filter( codi_estat__in = ['F','R','J']  )
    q_no_es_baixa = Q(data_baixa__gte = ara ) | Q(data_baixa__isnull = True )
    q_no_informat_adreca = Q( correu_relacio_familia_pare = '' ) & Q( correu_relacio_familia_mare = '' )
    
    llista_alumnes = Alumne.objects.filter(q_no_es_baixa).exclude( q_no_informat_adreca ).values_list('pk', flat=True)

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
                                                                          impartir__dia_impartir__gte = fa_2_setmanes,
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
            if hiHaNovetats:
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
                    #cal enviar msg a tutor que no s'ha pogut enviar correu a un seu alumne.
                    if settings.DEBUG:
                        print (u'Error enviant missatge a {0}'.format( alumne ))
                    enviatOK = False

                    # actualitzo info per a l'app mòbil
                    if hiHaNovetats:
                        alumne.modificacions_portal_set.novetats_detectades_moment=ara
                        n_tokens = alumne.modificacions_portal_set.save()

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

def enviaEmailFamilies(assumpte, missatge, fitxers=None):
    '''Envia email a tots els correus d'alumnes
    
    Envia a tots el mateix assumpte, missatge i fitxers adjunts.
    Utilitza la configuració dels settings per al remitent
    Retorna la quantitat de correus als que s'ha enviat el missatge i la quantitat als que no
    '''
    
    from aula.apps.alumnes.models import Alumne
    from django.db.models import Q
    from django.utils.datetime_safe import datetime
    from django.core import mail
      
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
        'correu_relacio_familia_pare','correu_relacio_familia_mare') # ,'correu_tutors', 'rp1_correu', 'rp2_correu', 'correu')
    
    # crea llista de correus
    correus_alumnes=[item for sublist in list(correus_alumnes) for item in sublist]
    # elimina repetits
    correus_alumnes=list(dict.fromkeys(correus_alumnes))
    # elimina buit
    correus_alumnes.remove('')

    connection = mail.get_connection()
    # Obre la connexió
    connection.open()
    
    cont=0
    total=len(correus_alumnes)
    correctes=0
    errors=0
    maxdest=settings.CUSTOM_MAX_EMAIL_RECIPIENTS
    if maxdest<=0: maxdest=1
    
    subject = u"{0} - {1}".format(assumpte, settings.NOM_CENTRE )
    body = [u"{0}".format( missatge ),
                u"",
                u"",
                u"Aquest missatge ha estat enviat per un sistema automàtic. No responguis  a aquest e-mail, el missatge no serà llegit per ningú.",
                u"Per qualsevol dubte/notificació posa't en contacte amb el tutor/a.",
                u"",
                ]
                   
    fromuser = settings.DEFAULT_FROM_EMAIL

    email = EmailMessage(subject, u'\n'.join( body ),fromuser, 
                             reply_to=[fromuser], connection=connection)
    
    if fitxers:
        for f in fitxers:
            f.seek(0) 
            email.attach(f.name, f.read(), f.content_type)

    while cont<total:
        if cont+maxdest<=total:
            destinataris=correus_alumnes[cont:cont+maxdest]
        else:
            destinataris=correus_alumnes[cont:total]
        cont=cont+maxdest
        
        try:          
            if settings.DEBUG:
                print (u'Enviant mail famílies a {0} adreces'.format(len(destinataris)))
            email.to=[]
            email.cc=[]
            email.bcc=destinataris
            email.send()
                 
            correctes=correctes + len(destinataris)
        except:
            errors=errors + len(destinataris)
    
    if settings.DEBUG:
        # Enviament per a verificació si DEBUG
        print (u'Enviant còpia mail famílies als administradors')
        email.to=[x[1] for x in settings.ADMINS]
        email.cc=[]
        email.bcc=[]
        email.send()

    # tanca la connexió
    connection.close()
    
    return correctes, errors
