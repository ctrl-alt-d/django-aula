# This Python file uses the following encoding: utf-8
from itertools import groupby

from django.conf import settings

#templates
from django.forms import FileInput
from django.template import RequestContext
from django.templatetags.static import static

#workflow
from django.shortcuts import render, get_object_or_404

#auth
from django.contrib.auth.decorators import login_required

#helpers
from aula.apps.avaluacioQualitativa.models import RespostaAvaluacioQualitativa
from aula.apps.incidencies.models import Incidencia, Sancio, Expulsio
from aula.apps.presencia.models import ControlAssistencia, EstatControlAssistencia
from aula.apps.relacioFamilies.forms import AlumneModelForm
from aula.apps.sortides.models import Sortida, NotificaSortida
from aula.utils import tools
from aula.utils.tools import unicode
from aula.apps.alumnes.models import Alumne

#qualitativa


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
from django.contrib.humanize.templatetags.humanize import naturalday
import json
from django.utils.html import escapejs

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
#    return render(
#                request,
#                'formsetgrid.html',
#                    {'formset': formset,
#                     'head': u'Gestió relació familia amb empreses' ,
#                     'formSetDelimited':True},
#                   )


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
    except Exception as e:
        cosMissatge = {'errors': [ e ], 'infos':[], 'warnings':[] }
    
    cosMissatge['url_next']=url_next
        
    return render(
                request,
                'resultat.html',
                    {'msgs': cosMissatge ,
                     'head': u"Acció Envia Benviguda a {0}".format( alumne ) ,
                    },
                )


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
    
    return render(
                request,
                'resultat.html',
                    {'msgs': resultat ,
                     'head': 'Canvi configuració accés família de {0}'.format( alumne ) ,
                    },
                )

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
        edatAlumne = alumne.edat()
    except:
        pass

    imageUrl = alumne.get_foto_or_default

    infoForm = [
          ('Alumne',unicode( alumne) ),
          #( 'Telèfon Alumne', alumne.telefons),
          ('Telèfon Alumne', alumne.rp1_telefon + u', ' + alumne.rp2_telefon + u', ' + alumne.altres_telefons),
          #( 'Nom tutors', alumne.tutors),
          ('Nom tutors', alumne.rp1_nom +  u', ' + alumne.rp2_nom),
          #('Correu tutors (Saga)', alumne.correu_tutors),
          ('Correu tutors (Saga)', alumne.rp1_correu + u', ' + alumne.rp2_correu),
          ( 'Edat alumne', edatAlumne ),
                ]
    
    AlumneFormSet = modelform_factory(Alumne,
                                      form=AlumneModelForm,
                                      widgets={
                                          'foto': FileInput,}
                                         )

    if request.method == 'POST':
        form = AlumneFormSet(  request.POST , request.FILES, instance=alumne )
        if form.is_valid(  ):
            form.save()
            url_next = '/open/dadesRelacioFamilies#{0}'.format(alumne.pk  ) 
            return HttpResponseRedirect( url_next )            

    else:
        form = AlumneFormSet(instance=alumne)                
        
    return render(
                request,
                'configuraConnexio.html',
                    {'form': form,
                     'image': imageUrl,
                     'infoForm': infoForm,
                     'head': u'Gestió relació familia amb empreses' ,
                     'formSetDelimited':True},
                )

    
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
            capcelera.amplade = 25
            capcelera.contingut = grup if grup == 'Altres' else u'{0} ({1})'.format(unicode( grup ) , unicode( grup.curs ) ) 
            capcelera.enllac = ""
            taula.capceleres.append(capcelera)
            
            capcelera = tools.classebuida()
            capcelera.amplade = 35
            capcelera.contingut = u'Correus Contacte'
            taula.capceleres.append(capcelera)
                        
            capcelera = tools.classebuida()
            capcelera.amplade = 25
            capcelera.contingut = u'Estat'
            taula.capceleres.append(capcelera)

            capcelera = tools.classebuida()
            capcelera.amplade = 15
            capcelera.contingut = u'Acció'
            taula.capceleres.append(capcelera)
                        
            taula.fileres = []
            
            if grup == 'Altres':
                consulta_alumnes = Q( pk__in = [ti.alumne.pk for ti in professor.tutorindividualitzat_set.all() ]  )
            else:
                consulta_alumnes = Q( grup =  grup )

            alumnes = Alumne.objects.filter(consulta_alumnes )

            familia_pendent_de_mirar_models = [
                (u'qualitativa', RespostaAvaluacioQualitativa,),
                (u'sortida(es)', NotificaSortida,),
                (u'incidencies o observacions', Incidencia,),
                (u'sanció(ns)', Sancio,),
                (u'expulsió(ns)', Expulsio,),
                (u'faltes assistència', ControlAssistencia,),
            ]

            familia_pendent_de_mirar = {}

            for codi, model in familia_pendent_de_mirar_models:
                familia_pendent_de_mirar[codi]= ( model
                                                    .objects
                                                    .filter( alumne__in = alumnes )
                                                    .filter( relacio_familia_revisada__isnull = True )
                                                    .filter( relacio_familia_notificada__isnull = False )
                                                    .values_list( 'alumne__pk', flat=True )
                                                  )

            for alumne in alumnes:
                
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
                bloquejat_text =  [ ( alumne.motiu_bloqueig, None ), ] if  alumne.motiu_bloqueig else []
                nConnexions = alumne.user_associat.LoginUsuari.filter(exitos=True).count()
                camp.multipleContingut = bloquejat_text + [ ( u'( {0} connexs. )'.format(nConnexions) , None, ), ]
                if nConnexions > 0:
                    dataDarreraConnexio = alumne.user_associat.LoginUsuari.filter(exitos=True).order_by( '-moment' )[0].moment
                    camp.multipleContingut.append( ( u'Darrera Connx: {0}'.format(  dataDarreraConnexio.strftime( '%d/%m/%Y' ) ), None, ) )
                for ambit in familia_pendent_de_mirar:
                    if alumne.pk in familia_pendent_de_mirar[ambit]:
                        camp.multipleContingut.append( (u"{} x revisar".format(ambit), None,) )
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
        
    return render(
                request,
                'report.html',
                    {'report': report,
                     'head': 'Els meus alumnes tutorats' ,
                    },
                )


                
#--------------------------------------------------------------------------------------------------------    
@login_required
def canviParametres( request ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
               
    alumne = Alumne.objects.get( user_associat = user )

    edatAlumne = None
    try:
        edatAlumne = alumne.edat()
    except:
        pass

    infoForm = [
        ('Alumne', unicode(alumne)),
        # ( 'Telèfon Alumne', alumne.telefons),
        ('Telèfon Alumne', alumne.rp1_telefon + u', ' + alumne.rp2_telefon + u', ' + alumne.altres_telefons),
        # ( 'Nom tutors', alumne.tutors),
        ('Nom tutors', alumne.rp1_nom + u', ' + alumne.rp2_nom),
        # ('Correu tutors (Saga)', alumne.correu_tutors),
        ('Correu tutors (Saga)', alumne.rp1_correu + u', ' + alumne.rp2_correu),
        ('Edat alumne', edatAlumne),
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

    return render(
                request,
                'form.html',
                    {'form': form,
                     'infoForm': infoForm,
                     'head': u'Canvi de paràmetres' ,
                     'formSetDelimited':True},
                )


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
        try:
            alumne = Alumne.objects.get( user_associat = user )
        except Exception as e:
            alumne = None
    
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
        capcelera.amplade = 25
        capcelera.contingut = u'Dia' 
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 75
        capcelera.contingut = u'Falta, assignatura i franja horària.'
        taula.capceleres.append(capcelera)
        
        tots_els_controls = list( controls.select_related('impartir', 'estat').order_by( '-impartir__dia_impartir' , '-impartir__horari__hora') )
        
        assistencia_calendari = []  #{"date":"2016-04-02","badge":true,"title":"Example 2"}
        from itertools import groupby
        for k, g in groupby(tots_els_controls, lambda x: x.impartir.dia_impartir ):
            gs= list(g)
            gs.reverse()
            assistencia_calendari.append(   { 'date': k.strftime( '%Y-%m-%d' ),
                                              'badge': any( [ c.estat.codi_estat == 'F' for c in gs ] ),
                                              'title':  u'\n'.join(  [  escapejs(u'{0} a {1} ({2})'.format(
                                                                                     c.estat,
                                                                                     c.impartir.horari.assignatura,
                                                                                     c.impartir.horari.hora 
                                                                                                            )
                                                                                   )   
                                                                            for c in gs
                                                                        ] )      # Store group iterator as a list
                                             }
                                         )
        
        
        for control in tots_els_controls:
            
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
#             assistencia_calendari.append(  { 'date': control.impartir.dia_impartir.strftime( '%Y-%m-%d' ) , 
#                                              'badge': control.estat.codi_estat == 'F', 
#                                              'title': escapejs( camp.contingut )
#                                             } )
    
            #--
            taula.fileres.append( filera )
    
        report.append(taula)    
        if not semiImpersonat:
            controlsNous = controls.update( relacio_familia_notificada = ara, relacio_familia_revisada = ara )
    

        
    #----observacions --------------------------------------------------------------------
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
        capcelera.amplade = 25
        capcelera.contingut = u'Dia'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 75
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
        capcelera.amplade = 30
        capcelera.contingut = u'Dia i estat'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 70
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
        capcelera.amplade = 20
        capcelera.contingut = u'Dia'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Data comunicació'
        taula.capceleres.append(capcelera)
            
        capcelera = tools.classebuida()
        capcelera.amplade = 60
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
                                               expulsio.motiu if expulsio.motiu else u'Pendent redactar motiu.')        
            camp.negreta = False if expulsio.relacio_familia_revisada else True                      
            filera.append(camp)
            #--
            taula.fileres.append( filera )
            
        report.append(taula)        
        if not semiImpersonat:
            expulsionsNoves.update( relacio_familia_notificada =  ara , relacio_familia_revisada = ara)

    #----Sancions -----------------------------------------------------------------------------   
    if detall in ['all', 'incidencies']:
        sancions = alumne.sancio_set.filter( impres = True )
        sancionsNoves = sancions.filter(  relacio_familia_revisada__isnull = True )
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Sancions {0}'.format( pintaNoves( sancionsNoves.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 25
        capcelera.contingut = u'Dates'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 75
        capcelera.contingut = u'Detall'
        taula.capceleres.append(capcelera)
                
        taula.fileres = []
            
        for sancio in sancions.order_by( '-data_inici' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} a {1}'.format( sancio.data_inici.strftime( '%d/%m/%Y' ) ,  sancio.data_fi.strftime( '%d/%m/%Y' ))       
            camp.negreta = False if sancio.relacio_familia_revisada else True                
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1} {2}'.format( sancio.tipus , ' - ' if sancio.motiu else '', sancio.motiu )        
            camp.negreta = False if sancio.relacio_familia_revisada else True                
            filera.append(camp)
            #--
            taula.fileres.append( filera )
    
        report.append(taula)
        if not semiImpersonat:
            sancionsNoves.update( relacio_familia_notificada = ara, relacio_familia_revisada = ara)

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
        capcelera.amplade = 25
        capcelera.contingut = u'Dades Alumne'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 75
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
        camp.contingut = u'{0}'.format( alumne.altres_telefons )
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

        camp.multipleContingut = [(u'{0} ({1} , {2})'.format(alumne.rp1_nom,
                                                             alumne.rp1_telefon,
                                                             alumne.rp1_mobil), None),
                                  (u'{0} ({1} , {2})'.format(alumne.rp2_nom,
                                                             alumne.rp2_telefon,
                                                             alumne.rp2_mobil),None),
                                  ]
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
        localitat_i_o_municipi = alumne.localitat if not alumne.municipi \
            else (alumne.municipi if not alumne.localitat
                  else (alumne.localitat + '-' + alumne.municipi if alumne.localitat != alumne.municipi
                        else alumne.localitat))
        camp.contingut = u'{0} - {1}'.format(alumne.adreca, localitat_i_o_municipi)
        filera.append(camp)
    
        taula.fileres.append( filera )
    
        report.append(taula)

    #----Sortides -----------------------------------------------------------------------------   
    if detall in ['all', 'sortides'] and settings.CUSTOM_MODUL_SORTIDES_ACTIU:
        sortides = alumne.notificasortida_set.all()
        sortidesNoves = sortides.filter(  relacio_familia_revisada__isnull = True )
        sortides_on_no_assistira = alumne.sortides_on_ha_faltat.values_list( 'id', flat=True ).distinct()           
        sortides_justificades = alumne.sortides_falta_justificat.values_list( 'id', flat=True ).distinct()           
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Activitats/Sortides {0}'.format( pintaNoves( sortidesNoves.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Dates'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 35
        capcelera.contingut = u' '
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 35
        capcelera.contingut = u'Detall'
        taula.capceleres.append(capcelera)
                
        capcelera = tools.classebuida()
        capcelera.amplade = 10
        capcelera.contingut = u' '
        taula.capceleres.append(capcelera)
                
        taula.fileres = []
            
        for sortida in sortides.order_by( '-sortida__calendari_desde' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = naturalday(sortida.sortida.calendari_desde)       
            camp.negreta = False if bool( sortida.relacio_familia_revisada ) else True                
            filera.append(camp)
            
            #----------------------------------------------
            #  NO INSCRIT A L’ACTIVITAT. L'alumne ha d'assistir al centre excepte si són de viatge de final de curs. 
            comentari_no_ve = u""            
            if sortida.sortida.pk in sortides_on_no_assistira:
                comentari_no_ve = u"NO INSCRIT A L’ACTIVITAT."
                if sortida.sortida.pk in sortides_justificades:
                    comentari_no_ve += u"NO INSCRIT A L’ACTIVITAT. Té justificada l'absència."

            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = comentari_no_ve       
            camp.negreta = False if bool( sortida.relacio_familia_revisada ) else True                
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( sortida.sortida.titol_de_la_sortida )        
            camp.negreta = False if sortida.relacio_familia_revisada else True                
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.modal = {}
            camp.modal['id'] = sortida.id 
            camp.modal['txtboto'] = u'Detalls' 
            camp.modal['tittle'] =  u"{0} ({1})".format( 
                                        sortida.sortida.titol_de_la_sortida,
                                        naturalday(sortida.sortida.calendari_desde),
                                        )
            camp.modal['body'] =  u'{0} a {1} \n\n{2}\n'.format( 
                                        sortida.sortida.calendari_desde.strftime( '%d/%m/%Y %H:%M' ),  
                                        sortida.sortida.calendari_finsa.strftime( '%d/%m/%Y %H:%M' ),                                        
                                        sortida.sortida.programa_de_la_sortida,
                                        ) 
            filera.append(camp)
            #--
            taula.fileres.append( filera )
    
        report.append(taula)
        if not semiImpersonat:
            sortidesNoves.update( relacio_familia_notificada = ara, relacio_familia_revisada = ara)


    #----Qualitativa -----------------------------------------------------------------------------
    qualitatives_alumne= { r.qualitativa for r in alumne.respostaavaluacioqualitativa_set.all() }
    avui = datetime.now().date()
    qualitatives_en_curs = [ q for q in qualitatives_alumne
                               if ( bool(q.data_obrir_portal_families) and
                                    bool( q.data_tancar_tancar_portal_families ) and 
                                    q.data_obrir_portal_families <= avui <= q.data_tancar_tancar_portal_families
                                   )
                           ]

    if detall in ['all', 'qualitativa'] and qualitatives_en_curs:
        
        respostes = alumne.respostaavaluacioqualitativa_set.filter( qualitativa__in = qualitatives_en_curs )
        respostesNoves = respostes.filter( relacio_familia_revisada__isnull = True )

        assignatures = list(set( [r.assignatura for r in respostes] ))
        hi_ha_tipus_assignatura = ( bool(assignatures)
                                    and assignatures[0]
                                    and assignatures[0].tipus_assignatura is not None
                                    and assignatures[0].tipus_assignatura.capcelera
                                    )
        asignatura_label = assignatures[0].tipus_assignatura.capcelera if hi_ha_tipus_assignatura else u"Matèria"

        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = u"Avaluació qualitativa {0}".format( u"!" if respostesNoves.exists() else "" )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Qualitativa'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = asignatura_label
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 65
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
                
        taula.fileres = []

        respostes_pre = ( respostes
                          .order_by( 'qualitativa__data_obrir_avaluacio','assignatura' )
                         )
        
        keyf = lambda x: (x.qualitativa.nom_avaluacio + x.assignatura.nom_assignatura)
        respostes_sort=sorted( respostes_pre, key=keyf )
        from itertools import groupby
             
        for _ , respostes in groupby( respostes_sort, keyf ):
            respostes=list(respostes)
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = respostes[0].qualitativa.nom_avaluacio       
            camp.negreta = False if bool( respostes[0].relacio_familia_revisada ) else True                
            filera.append(camp)

            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = respostes[0].assignatura.nom_assignatura or respostes[0].assignatura
            camp.negreta = False if bool( respostes[0].relacio_familia_revisada ) else True                
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.multipleContingut = []
            for resposta in respostes:
                camp.multipleContingut.append( ( u'{0}'.format( resposta.get_resposta_display() ), None, ) )        
            camp.negreta = False if respostes[0].relacio_familia_revisada else True                
            filera.append(camp)
            
            #--
            taula.fileres.append( filera )
    
        report.append(taula)
        if not semiImpersonat:
            respostesNoves.update( relacio_familia_notificada = ara, relacio_familia_revisada = ara)

    return render(
                request,
                'report_detall_families.html',
                    {'report': report,
                     'head': u'Informació alumne {0}'.format( head ) ,
                     'assistencia_calendari': json.dumps(  assistencia_calendari ),
                    },
                )



def pintaNoves( numero ):
    txt = ''
    if numero == 1:
        txt = u'({0} nova)'.format( numero ) 
    elif numero > 1:
        txt = u'({0} noves)'.format( numero )
    return txt


    
    
    
    
