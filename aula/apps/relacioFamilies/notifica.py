# This Python file uses the following encoding: utf-8

import os
import sys
from django.conf import settings

def notifica():
    print u'Notificant ...'
    from aula.apps.alumnes.models import Alumne
    from django.db import transaction
    from django.core.exceptions import ObjectDoesNotExist
    from django.db.models import Q
    from datetime import timedelta
    from django.utils.datetime_safe import datetime
    from aula.apps.presencia.models import EstatControlAssistencia
    from aula.apps.presencia.models import ControlAssistencia
    from django.core.mail import send_mail
    from aula.apps.usuaris.models import Accio
    
    
    urlDjangoAula = settings.URL_DJANGO_AULA
    urlVideoTutorial = "- No disponible -"
    
    with transaction.autocommit():
        ara = datetime.now()
        
        fa_2_setmanes = ara - timedelta(  days = 14 )
        presencies_notificar = EstatControlAssistencia.objects.filter( codi_estat__in = ['F','R','J']  )
        q_no_es_baixa = Q(data_baixa__gte = ara ) | Q(data_baixa__isnull = True )
        q_no_informat_adreca = Q( correu_relacio_familia_pare = '' ) & Q( correu_relacio_familia_mare = '' )
        #q_primer = Q( grup__descripcio_grup = '1r CFGS Inform A' )
        #q_segon = Q( grup__descripcio_grup = '2n CFGS Inform A' )
        #filter( q_primer | q_segon ).'
        
        llista_alumnes = Alumne.objects.filter(q_no_es_baixa).exclude( q_no_informat_adreca ).values_list('pk', flat=True)
        
        for alumne_id in llista_alumnes:
            try:
                alumne = Alumne.objects.get( pk = alumne_id )
                fa_n_dies = ara - timedelta(  days = alumne.periodicitat_faltes )
                noves_incidencies = alumne.incidencia_set.filter( relacio_familia_notificada__isnull = True  )
                noves_expulsions = alumne.expulsio_set.exclude( estat = 'ES').filter(    relacio_familia_notificada__isnull = True  )
                noves_expulsions_centre = alumne.expulsiodelcentre_set.filter( impres=True, relacio_familia_notificada__isnull = True  )
                noves_faltes_assistencia = ControlAssistencia.objects.filter( alumne = alumne, 
                                                                              impartir__dia_impartir__gte = fa_2_setmanes,
                                                                              relacio_familia_notificada__isnull = True,
                                                                              estat__pk__in = presencies_notificar )
                hiHaNovetatsPresencia = False
                hiHaNovetats = False
                #comprovo si hi ha novetats de presencia i incidències
                fa_dies_que_no_notifiquem = alumne.relacio_familia_darrera_notificacio is None or \
                                            alumne.relacio_familia_darrera_notificacio < fa_n_dies
                hiHaNovetatsPresencia =  alumne.periodicitat_faltes > 0 and \
                                         fa_dies_que_no_notifiquem and \
                                         noves_faltes_assistencia.exists()
                hiHaNovetats =  hiHaNovetatsPresencia or \
                                ( alumne.periodicitat_incidencies and
                                ( noves_incidencies.exists() or noves_expulsions.exists() or noves_expulsions_centre.exists() )
                                )                  
                #print u'Avaluant a {0}'.format( alumne )
                enviatOK = False
                if hiHaNovetats:
                    #enviar correu i marcar novetats com a notificades:
                    missatge = [ 
                             u"Portal d'informació a les famílies de " + settings.NOM_CENTRE,
                             u"",
                             u"Teniu novetats de {0} al portal de relació famílies {1}".format(alumne.nom, urlDjangoAula),
                             u"",
                             u"Recordeu que el vostre nom d'usuari és: {0}".format( alumne.get_user_associat().username ),
                             u"",
                             u"Esperem que amb aquesta aplicació us poguem ajudar a fer un seguiment més exahustiu del treball dels vostres fills al centre.",
                             u"",
                             u"Cordialment",
                             u"",
                             settings.NOM_CENTRE,
                             u"",
                             u"",
                             u"Video Tutorial d'ajuda a {0}".format( urlVideoTutorial ),
                            ]
                    try:                        
                        fromuser = settings.EMAIL_HOST_USER
                        if settings.DEBUG:
                            print u'Enviant missatge a {0}'.format( alumne )
                        send_mail(u'Novetats al portal de relació famílies', 
                                      u'\n'.join( missatge ), 
                                      fromuser,
                                      alumne.get_correus_relacio_familia(), 
                                      fail_silently=False)
                        enviatOK = True
                    except:
                        #cal enviar msg a tutor que no s'ha pogut enviar correu a un seu alumne.
                        enviatOK = False

                if enviatOK:
                    noves_incidencies.update( relacio_familia_notificada = ara )
                    noves_expulsions.update( relacio_familia_notificada = ara )
                    noves_expulsions_centre.update( relacio_familia_notificada = ara )
                    noves_faltes_assistencia.update( relacio_familia_notificada = ara )
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

    print u"Fi procés notificacions ..."

#             
# if __name__ == '__main__':
#     # Setup environ
#     sys.path.append( os.path.join(os.path.dirname(__file__), '..' ) )
#     os.environ['DJANGO_SETTINGS_MODULE'] = "settings"
#     try:
#         notifica()
#     except Exception, e:
#         errors = [unicode(e)]
#     
#         #Deixar missatge a la base de dades (utilitzar self.user )
#         from aula.apps.missatgeria.models import Missatge
#         from django.contrib.auth.models import User, Group
# 
#         usuari_notificacions, new = User.objects.get_or_create( username = 'TP')
#         if new:
#             usuari_notificacions.is_active = False
#             usuari_notificacions.first_name = u'Usuari Tasques Programades'
#             usuari_notificacions.save()
#         msg = Missatge( 
#                     remitent= usuari_notificacions, 
#                     text_missatge = u"Error enviant notificacions relació famílies.")    
#         msg.afegeix_errors( errors.sort() )
#         importancia = 'VI' 
#         
#         grupDireccio =  Group.objects.get( name = 'direcció' )
#         msg.envia_a_grup( grupDireccio , importancia=importancia)
#         
#         
#     
#     

