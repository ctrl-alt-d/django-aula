# This Python file uses the following encoding: utf-8

#templates
from django.template import RequestContext

#workflow
from django.shortcuts import render_to_response, get_object_or_404

#auth
from django.contrib.auth.decorators import login_required

#helpers
from aula.utils import tools
from aula.apps.alumnes.models import Alumne

#dates
from datetime import date

#exceptions
from django.http import Http404, HttpResponseRedirect
from aula.apps.usuaris.models import User2Professor, AlumneUser
from aula.apps.tutoria.models import Tutor
from aula.utils.decorators import group_required

from django.db.models import Q
from django.forms.models import modelform_factory, modelformset_factory
from django.utils.datetime_safe import datetime

from aula.apps.usuaris.tools import enviaBenvingudaAlumne, bloqueja, desbloqueja

import random

#@login_required
#@group_required(['professors'])
#def dadesRelacioFamilies_old( request ):
#    credentials = tools.getImpersonateUser(request) 
#    (user, l4 ) = credentials
#
#    professor = User2Professor( user )     
#    
#    grups = [ t.grup for t in  Tutor.objects.filter( professor = professor )]
#    consulta_alumnes_grups = Q( grup__in =  grups )           
#    consulta_alumnes_individuals = Q( pk__in = [ti.alumne.pk for ti in professor.tutorindividualitzat_set.all() ]  )
#            
#    alumnes =  Alumne.objects.filter( consulta_alumnes_individuals | consulta_alumnes_grups )
#    
#    AlumneFormSet = modelformset_factory(Alumne, 
#                                         fields = ( 'nom',  'correu_relacio_familia_pare', 'correu_relacio_familia_mare', 'compte_bloquejat'  ), 
#                                         extra =0)
#    
#    formset = AlumneFormSet(queryset=alumnes)
#    
#    if request.method == 'POST':
#        form = formset(  request.POST  )
#        if form.is_valid(  ):
#            form.save()
#
#    else:
#        pass  
#        #form.base_fields['data'].widget = forms.DateTimeInput(attrs={'class':'DateTimeAnyTime'} )                
#        
#    return render_to_response(
#                'formsetgrid.html',
#                    {'formset': formset,
#                     'head': u'Gestió relació familia amb empreses' ,
#                     'formSetDelimited':True},
#                    context_instance=RequestContext(request))    


#--------------------------------------------


@login_required
@group_required(['professors'])
def enviaBenvinguda( request , pk ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    professor = User2Professor( user )     
            
    alumne =  Alumne.objects.get( pk = int(pk) )
    
    url_next = '/open/dadesRelacioFamilies/#{0}'.format(alumne.pk)
            
    #seg-------------------
    te_permis = l4 or  professor in alumne.tutorsDeLAlumne() 
    if  not te_permis:
        raise Http404()     
    
    filera = []                
        
    try:
        cosMissatge = enviaBenvingudaAlumne( alumne ) 
    except Exception, e:
        cosMissatge = {'errors': [ e ], 'infos':[], 'warnings':[] }
    
    cosMissatge['url_next']=url_next
        
    return render_to_response(
                'resultat.html',
                    {'msgs': cosMissatge ,
                     'head': u"Acció Envia Benviguda a {0}".format( alumne ) ,
                    },
                    context_instance=RequestContext(request))        


#--------------------------------------------

@login_required
@group_required(['professors'])
def bloquejaDesbloqueja( request , pk ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    professor = User2Professor( user )     
            
    alumne =  Alumne.objects.get( pk = int(pk) )
    
    url_next = '/open/dadesRelacioFamilies/#{0}'.format(alumne.pk)

    #seg-------------------
    te_permis = l4 or  professor in alumne.tutorsDeLAlumne() 
    if  not te_permis:
        raise Http404()
        
    actiu =  alumne.esta_relacio_familia_actiu() 
    
    if actiu:
        resultat = bloqueja( alumne, u'Bloquejat per {0} amb data {1}'.format( professor, datetime.now() ) )
    else:
        resultat = desbloqueja( alumne )
    resultat['url_next'] = url_next
    
    return render_to_response(
                'resultat.html',
                    {'msgs': resultat ,
                     'head': 'Canvi configuració accés família de {0}'.format( alumne ) ,
                    },
                    context_instance=RequestContext(request)) 

@login_required
@group_required(['professors'])
def configuraConnexio( request , pk ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    professor = User2Professor( user )     
            
    alumne =  Alumne.objects.get( pk = int(pk) )
    
    #seg-------------------
    te_permis = l4 or  professor in alumne.tutorsDeLAlumne() 
    if  not te_permis:
        raise Http404() 

    edatAlumne = None
    try:
        edatAlumne = (date.today() - alumne.data_neixement).days / 365 
    except:
        pass
        
    infoForm = [
          ('Alumne',unicode( alumne) ),
          ( 'Telèfon Alumne', alumne.telefons),                     
          ( 'Nom tutors', alumne.tutors),                     
          ( 'Correu tutors (Saga)', alumne.correu_tutors),                     
          ( 'Edat alumne', edatAlumne ),                     
                ]
    
    AlumneFormSet = modelform_factory(Alumne,
                                      fields = ( 'correu_relacio_familia_pare', 'correu_relacio_familia_mare' ,
                                                    'periodicitat_faltes', 'periodicitat_incidencies'), 
                                         )    
    
    if request.method == 'POST':
        form = AlumneFormSet(  request.POST , instance=alumne )
        if form.is_valid(  ):
            form.save()
            url_next = '/open/dadesRelacioFamilies#{0}'.format(alumne.pk  ) 
            return HttpResponseRedirect( url_next )            

    else:
        form = AlumneFormSet(instance=alumne)                
        
    return render_to_response(
                'form.html',
                    {'form': form,
                     'infoForm': infoForm,
                     'head': u'Gestió relació familia amb empreses' ,
                     'formSetDelimited':True},
                    context_instance=RequestContext(request)) 

    
#--------------------------------------------------------------------------------------------------------

@login_required
@group_required(['professors'])
def dadesRelacioFamilies( request ):
    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    report = []
    grups = [ t.grup for t in  Tutor.objects.filter( professor = professor )]
    grups.append( 'Altres' )
    for grup in grups:
            taula = tools.classebuida()

            taula.titol = tools.classebuida()
            taula.titol.contingut = ''
            taula.titol.enllac = None

            taula.capceleres = []
            
            capcelera = tools.classebuida()
            capcelera.amplade = 100
            capcelera.contingut = grup if grup == 'Altres' else u'{0} ({1})'.format(unicode( grup ) , unicode( grup.curs ) ) 
            capcelera.enllac = ""
            taula.capceleres.append(capcelera)
            
            capcelera = tools.classebuida()
            capcelera.amplade = 70
            capcelera.contingut = u'Correus Contacte'
            taula.capceleres.append(capcelera)
                        
            capcelera = tools.classebuida()
            capcelera.amplade = 70
            capcelera.contingut = u'Actiu'
            taula.capceleres.append(capcelera)

            capcelera = tools.classebuida()
            capcelera.amplade = 70
            capcelera.contingut = u'Acció'
            taula.capceleres.append(capcelera)
                        
            taula.fileres = []
            
            if grup == 'Altres':
                consulta_alumnes = Q( pk__in = [ti.alumne.pk for ti in professor.tutorindividualitzat_set.all() ]  )
            else:
                consulta_alumnes = Q( grup =  grup )           
            
            for alumne in Alumne.objects.filter(consulta_alumnes ):
                
                filera = []
                
                #-Alumne--------------------------------------------
                camp = tools.classebuida()
                camp.codi = alumne.pk
                camp.enllac = None
                camp.contingut = unicode(alumne)
                filera.append(camp)

                #-Correus Contacte--------------------------------------------
                camp = tools.classebuida()
                camp.enllac = None
                camp.contingut = unicode( ', '.join( alumne.get_correus_relacio_familia() ) )
                filera.append(camp)


                #-Bloquejat--------------------------------------------           
                camp = tools.classebuida()
                camp.codi = alumne.pk
                camp.enllac = None
                nConnexions = 0
                contingut = u'{0} {1}'.format(u'Sí' if alumne.esta_relacio_familia_actiu() else u'No', 
                                                   u'({0})'.format(alumne.motiu_bloqueig) if alumne.motiu_bloqueig else '') #TODO
                try:
                    nConnexions = alumne.user_associat.LoginUsuari.filter(exitos=True).count()
                    dataDarreraConnexio = alumne.user_associat.LoginUsuari.filter(exitos=True).order_by( '-moment' )[0].moment
                except:
                    pass                
                camp.multipleContingut = [ ( contingut, None,), ( u'( {0} connexs. )'.format(nConnexions) , None, ), ] 
                if nConnexions > 0:
                    camp.multipleContingut.append( ( u'Darrera Connx: {0}'.format(  dataDarreraConnexio.strftime( '%d/%m/%Y' ) ), None, ) )
                filera.append(camp)
                
                #-Acció--------------------------------------------
                camp = tools.classebuida()
                camp.enllac = None
                accio_list = [ (u'Configura', '/open/configuraConnexio/{0}'.format(alumne.pk) ), 
                               #(u'Bloquejar' if alumne.esta_relacio_familia_actiu() else u'Desbloquejar', '/open/bloquejaDesbloqueja/{0}'.format(alumne.pk)),
                               (u'Envia benvinguda' , '/open/enviaBenvinguda/{0}'.format(alumne.pk)),  
                               (u'Veure Portal' , '/open/elMeuInforme/{0}'.format(alumne.pk)),] 
                camp.multipleContingut = accio_list
                filera.append(camp)
                
                #--
                taula.fileres.append( filera )            
            report.append(taula)
        
    return render_to_response(
                'report.html',
                    {'report': report,
                     'head': 'Els meus alumnes tutorats' ,
                    },
                    context_instance=RequestContext(request))            


                
#--------------------------------------------------------------------------------------------------------    
@login_required
def canviParametres( request ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
               
    alumne = Alumne.objects.get( user_associat = user )

    edatAlumne = None
    try:
        edatAlumne = (date.today() - alumne.data_neixement).days / 365 
    except:
        pass
        
    infoForm = [
          ('Alumne',unicode( alumne) ),
          ( 'Telèfon Alumne', alumne.telefons),                     
          ( 'Nom tutors', alumne.tutors),                     
          ( 'Correu tutors (Saga)', alumne.correu_tutors),                     
          ( 'Edat alumne', edatAlumne ),                     
                ]
    
    AlumneFormSet = modelform_factory(Alumne,
                                         fields = ( 'correu_relacio_familia_pare', 'correu_relacio_familia_mare' ,
                                                    'periodicitat_faltes', 'periodicitat_incidencies'), 
                                         )    
    
    if request.method == 'POST':
        form = AlumneFormSet(  request.POST , instance=alumne )
        if form.is_valid(  ):
            form.save()
            url_next = '/open/elMeuInforme/'
            return HttpResponseRedirect( url_next )            

    else:
        form = AlumneFormSet(instance=alumne)                
        
    return render_to_response(
                'form.html',
                    {'form': form,
                     'infoForm': infoForm,
                     'head': u'Canvi de paràmetres' ,
                     'formSetDelimited':True},
                    context_instance=RequestContext(request)) 


@login_required
def elMeuInforme( request, pk = None ):
    """Dades que veurà l'alumne"""
    
    detall = 'all'

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
    nTaula = 0
    
    tePermis = True
    semiImpersonat = False
    if pk:
        professor = User2Professor( user )
        alumne =  Alumne.objects.get( pk = pk )   
        tePermis = professor in alumne.tutorsDeLAlumne() 
        semiImpersonat = True
    else:
        alumne = Alumne.objects.get( user_associat = user )
    
    if not alumne or not tePermis:
        raise Http404 
    
    head = u'{0} ({1})'.format(alumne , unicode( alumne.grup ) )
    
    ara = datetime.now()
    
    report = []

    #----Assistencia --------------------------------------------------------------------
    if detall in ['all', 'assistencia']:
        controls = alumne.controlassistencia_set.exclude( estat__codi_estat = 'P' 
                                                              ).filter(  
                                                        estat__isnull=False                                                          
                                                            )
        controlsNous = controls.filter( relacio_familia_revisada__isnull = True )
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Faltes i retards {0}'.format( pintaNoves( controlsNous.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        taula.fileres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 200
        capcelera.contingut = u'Dia' 
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 400
        capcelera.contingut = u'Falta, assignatura i franja horària.'
        taula.capceleres.append(capcelera)
        
        for control in controls.order_by( '-impartir__dia_impartir' , '-impartir__horari__hora'):
            
            filera = []
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = unicode(control.impartir.dia_impartir.strftime( '%d/%m/%Y' ))  
            camp.negreta = False if control.relacio_familia_revisada else True      
            filera.append(camp)
    
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} a {1} ({2})'.format(
                                                 control.estat,
                                                 control.impartir.horari.assignatura,
                                                 control.impartir.horari.hora 
                                    )        
            camp.negreta = False if control.relacio_familia_revisada else True      
            filera.append(camp)
    
            #--
            taula.fileres.append( filera )
    
        report.append(taula)    
        if not semiImpersonat:
            controlsNous = controls.update( relacio_familia_notificada = ara, relacio_familia_revisada = ara )
    

        
    #----observacions --------------------------------------------------------------------
#tipusIncidencia
        observacions = alumne.incidencia_set.filter( tipus__es_informativa = True)
        observacionsNoves = observacions.filter(  relacio_familia_revisada__isnull = True)
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Observacions {0}'.format( pintaNoves( observacionsNoves.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 200
        capcelera.contingut = u'Dia'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 400
        capcelera.contingut = u'Professor i observació.'
        taula.capceleres.append(capcelera)
        
        taula.fileres = []
    
        for incidencia in observacions.order_by( '-dia_incidencia', '-franja_incidencia' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( incidencia.dia_incidencia.strftime( '%d/%m/%Y' ))  
            camp.negreta = False if incidencia.relacio_familia_notificada else True
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.negreta = False if incidencia.relacio_familia_revisada else True
            camp.contingut = u'Sr(a): {0} - {1}'.format(incidencia.professional , 
                                                        incidencia.descripcio_incidencia )        
            camp.negreta = False if incidencia.relacio_familia_revisada else True
            filera.append(camp)
    
            #--
            taula.fileres.append( filera )
        
        report.append(taula)
        if not semiImpersonat:
            observacionsNoves = observacions.update(  relacio_familia_notificada = ara, relacio_familia_revisada = ara)
                    
    #----incidències --------------------------------------------------------------------
#tipusIncidencia
        incidencies = alumne.incidencia_set.filter( tipus__es_informativa = False )
        incidenciesNoves = incidencies.filter( relacio_familia_revisada__isnull = True )
    
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Incidències {0}'.format( pintaNoves(  incidenciesNoves.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 200
        capcelera.contingut = u'Dia i estat'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 400
        capcelera.contingut = u'Professor i Incidència'
        taula.capceleres.append(capcelera)
        
        taula.fileres = []
    
        for incidencia in incidencies.order_by( '-dia_incidencia', '-franja_incidencia' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1}'.format( incidencia.dia_incidencia.strftime( '%d/%m/%Y' ), 
                                                'Vigent' if incidencia.es_vigent else '')   
            camp.negreta = False if incidencia.relacio_familia_revisada else True      
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'Sr(a): {0} - {1}'.format(incidencia.professional , 
                                                        incidencia.descripcio_incidencia )        
            camp.negreta = False if incidencia.relacio_familia_revisada else True      
            filera.append(camp)
    
            #--
            taula.fileres.append( filera )            
    
        report.append(taula)
        if not semiImpersonat:
            incidenciesNoves.update( relacio_familia_notificada =  ara, relacio_familia_revisada = ara )
        

    #----Expulsions --------------------------------------------------------------------
        expulsions = alumne.expulsio_set.exclude( estat = 'ES' )
        expulsionsNoves = expulsions.filter( relacio_familia_revisada__isnull = True )
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Expulsions {0}'.format( pintaNoves( expulsionsNoves.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 200
        capcelera.contingut = u'Dia'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 40
        capcelera.contingut = u'Data comunicació'
        taula.capceleres.append(capcelera)
            
        capcelera = tools.classebuida()
        capcelera.amplade = 400
        capcelera.contingut = u'Professor i motiu'
        taula.capceleres.append(capcelera)
        
        taula.fileres = []
        
        for expulsio in expulsions.order_by( '-dia_expulsio', '-franja_expulsio' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1}'.format( expulsio.dia_expulsio.strftime( '%d/%m/%Y' ),
                                                u'''(per acumulació d'incidències)''' if expulsio.es_expulsio_per_acumulacio_incidencies else '')
            camp.negreta = False if expulsio.relacio_familia_revisada else True                      
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( expulsio.moment_comunicacio_a_tutors.strftime( '%d/%m/%Y' ) 
                                                     if expulsio.moment_comunicacio_a_tutors 
                                                     else u'Pendent de comunicar.')         
            camp.negreta = False if expulsio.relacio_familia_revisada else True                      
            filera.append(camp)            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'Sr(a): {0} - {1}'.format(                                                
                                               expulsio.professor , 
                                               expulsio.motiu_expulsio if expulsio.motiu_expulsio else u'Pendent redactar motiu.')        
            camp.negreta = False if expulsio.relacio_familia_revisada else True                      
            filera.append(camp)
            #--
            taula.fileres.append( filera )
            
        report.append(taula)        
        if not semiImpersonat:
            expulsionsNoves.update( relacio_familia_notificada =  ara , relacio_familia_revisada = ara)

    #----Expulsions del centre --------------------------------------------------------------------   
    if detall in ['all', 'incidencies']:
        expulsionsDelCentre = alumne.expulsiodelcentre_set.filter( impres = True )
        expulsionsDelCentreNoves = expulsionsDelCentre.filter(  relacio_familia_revisada__isnull = True )
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Expulsions del Centre {0}'.format( pintaNoves( expulsionsDelCentreNoves.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 200
        capcelera.contingut = u'Dates'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 400
        capcelera.contingut = u'Motiu'
        taula.capceleres.append(capcelera)
                
        taula.fileres = []
            
        for expulsio in expulsionsDelCentre.order_by( '-data_inici' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} a {1}'.format( expulsio.data_inici.strftime( '%d/%m/%Y' ) ,  expulsio.data_fi.strftime( '%d/%m/%Y' ))       
            camp.negreta = False if expulsio.relacio_familia_revisada else True                
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( expulsio.motiu_expulsio )        
            camp.negreta = False if expulsio.relacio_familia_revisada else True                
            filera.append(camp)
            #--
            taula.fileres.append( filera )
    
        report.append(taula)
        if not semiImpersonat:
            expulsionsDelCentreNoves.update( relacio_familia_notificada = ara, relacio_familia_revisada = ara)

    #---dades alumne---------------------------------------------------------------------
    if detall in ['all','dades']:
        taula = tools.classebuida()
        taula.tabTitle = 'Dades personals'
    
        taula.codi = nTaula; nTaula+=1
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 200
        capcelera.contingut = u'Dades Alumne'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 400
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
        
        taula.fileres = []
    
            #----grup------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Grup'        
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format( alumne.grup )        
        filera.append(camp)
    
        taula.fileres.append( filera )
    
            #----data neix------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Data Neixement'        
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format( alumne.data_neixement )        
        filera.append(camp)
    
        taula.fileres.append( filera )
    
            #----telefons------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Telèfon'        
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format( alumne.telefons )        
        filera.append(camp)
    
        taula.fileres.append( filera )
    
            #----Pares------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Pares'        
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format( alumne.tutors )        
        filera.append(camp)
    
        taula.fileres.append( filera )
    
            #----adreça------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Adreça'        
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0} ({1})'.format( alumne.adreca, alumne.localitat )        
        filera.append(camp)
    
        taula.fileres.append( filera )
    
        report.append(taula)

    
    return render_to_response(
                'report_detall_families.html',
                    {'report': report,
                     'head': u'Informació alumne {0}'.format( head ) ,
                    },
                    context_instance=RequestContext(request))            



def pintaNoves( numero ):
    txt = ''
    if numero == 1:
        txt = u'({0} nova)'.format( numero ) 
    elif numero > 1:
        txt = u'({0} noves)'.format( numero )
    return txt


    
    
    
    