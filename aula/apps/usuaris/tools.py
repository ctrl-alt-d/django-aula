# This Python file uses the following encoding: utf-8
import random
from aula.apps.usuaris.models import OneTimePasswd, Professor
from django.utils.datetime_safe import datetime
from datetime import timedelta
from django.db.models import Q
from django.conf import settings
from aula.apps.alumnes.models import Alumne

def enviaOneTimePasswd( email ):
    q_correu_pare = Q( correu_relacio_familia_pare = email )
    q_correu_mare = Q( correu_relacio_familia_mare = email )    
    nUsuaris = 0
    nErrors = 0
    errors = []
    alumnes = Alumne.objects.filter( q_correu_pare | q_correu_mare )
    for alumne in alumnes:
        resultat = enviaOneTimePasswdAlumne( alumne )
        nUsuaris += 1
        if resultat['errors']:
            nErrors += 1 
            errors.append( ', '.join( resultat['errors'] ) )

    professors = Professor.objects.filter( email = email )
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

def enviaOneTimePasswdAlumne( alumne, force = False ):
    
    usuari = alumne.get_user_associat().username
    actiu =  alumne.esta_relacio_familia_actiu()     
    correusFamilia = alumne.get_correus_relacio_familia()
        
    infos = []
    warnings = []
    errors = []
    
    #comprovo que no s'hagi enviat més de 2 recuperacions en un dia:
    fa_24h = datetime.now() - timedelta( days = 1 )
    total_enviats = OneTimePasswd.objects.filter( usuari =alumne.user_associat, moment_expedicio__gte = fa_24h  ).count()
    if total_enviats >= 3:
        errors.append( u'Màxim número de missatges enviats a aquest correu durant les darrers 24h.' )
    elif not correusFamilia:
        warnings.append( u"Comprova que l'adreça electrònica d'almenys un dels pares estigui informada")
        errors.append( u"Error enviant codi de recuperació d'accés" )
    elif alumne.esBaixa():
        warnings.append( u"Aquest alumne és baixa. No se li pot enviar codi d'accés.")
        errors.append( u"Error enviant codi de recuperació d'accés")
    else:
        #preparo el codi a la bdd:
        clau = str( random.randint( 100000, 999999) ) + str( random.randint( 100000, 999999) )
        OneTimePasswd.objects.create(usuari = alumne.user_associat, clau = clau)
        
        #envio missatge:
        urlDjangoAula = settings.URL_DJANGO_AULA
        url = "{0}/usuaris/recoverPasswd/{1}/{2}".format( urlDjangoAula, usuari, clau )
        txtCapcelera = u"Enviat missatge a {0} .".format( 
                                u", ".join( correusFamilia )
                                                                )
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
                     u"i us preguntarà quina contrasenya voleu. Com a mesura suplementària de seguretat us demanarà també alguna altre dada.",
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
                      [ x for x in [ alumne.correu_relacio_familia_pare, alumne.correu_relacio_familia_mare] if x is not None ], 
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
                     u"i us preguntarà quina contrasenya voleu. Com a mesura suplementària de seguretat us demanarà també alguna altre dada.",
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
        warnings.append( u"Comprova que l'adreça electrònica d'almenys un dels pares estigui informada")
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

        missatge = [ u"Benvolgut/da,",
                     u"",
                     u"El motiu d'aquest correu és el de donar-vos les instruccions d'alta de l'aplicació Djau del nostre centre.",
                     u"Aquesta aplicació us permetrà fer un seguiment diari del rendiment acadèmic del vostre fill/a.",
                     u"Per tant, hi trobareu les faltes d'assistència, de disciplina, les observacions del professorat , les sortides que afectaran al vostre fill/a entre altres informacions.",
                     u"",
                     u"Per a donar-vos d'alta:",
                     u"",
                     u" * Entreu a {0} on podeu obtenir o recuperar les claus d'accés a l'aplicació.".format(urlDjangoAula),
                     u" * Cliqueu l'enllaç 'Obtenir o recuperar accés'. ",
                     u" * Escriviu la vostra adreça de correu electrònic.",
                     u" * Cliqueu el botó  Enviar.",
                     u" * Consulteu el vostre correu electrònic on hi trobareu un missatge amb les instruccions per completar el procés d'accés al Djau.",
                     u"",
                     u"Com bé sabeu és molt important que hi hagi una comunicació molt fluida entre el centre i les famílies.",
                     u"És per això que us recomanem que us doneu d'alta a aquesta aplicació i per qualsevol dubte que tingueu al respecte, poseu-vos en contacte amb el tutor/a del vostre fill/a.",
                     u"",
                     u"Restem a la vostra disposició per a qualsevol aclariment.",
                     u"",
                     u"Cordialment,",
                     u"",
                     settings.NOM_CENTRE,
                     u"",
                     u"{0}".format( textTutorial ), 
                     ]        
        
      
    
        from django.core.mail import send_mail
        enviatOK = True
        try:
            fromuser = settings.DEFAULT_FROM_EMAIL
            send_mail(assumpte, 
                      u'\n'.join( missatge ), 
                      fromuser,
                      [ x for x in [ alumne.correu_relacio_familia_pare, alumne.correu_relacio_familia_mare] if x is not None ], 
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


