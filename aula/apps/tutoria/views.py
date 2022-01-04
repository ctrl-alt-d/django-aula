# This Python file uses the following encoding: utf-8
import itertools

from django.utils.html import escape
from django.utils.safestring import mark_safe

from aula.apps.incidencies.business_rules.expulsio import expulsio_despres_de_posar
from aula.apps.incidencies.table2_models import Table2_ExpulsionsPendentsTramitar, \
    Table2_ExpulsionsPendentsPerAcumulacio, Table2_ExpulsionsIIncidenciesPerAlumne
from aula.utils.widgets import DateTimeTextImput,DateTextImput
#templates
from django.template import RequestContext
from django.http import HttpResponse

#workflow
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseRedirect

#auth
from django.contrib.auth.decorators import login_required
from aula.apps.usuaris.models import User2Professor, User2Professional, Accio, LoginUsuari, Professional, Professor
from aula.utils.decorators import group_required

#forms
from aula.apps.tutoria.forms import  justificaFaltesW1Form, informeSetmanalForm,\
    seguimentTutorialForm, elsMeusAlumnesTutoratsEntreDatesForm

#helpers
from aula.utils import tools
from aula.apps.presencia.models import  ControlAssistencia, EstatControlAssistencia,\
    Impartir
from django.utils.datetime_safe import  date, datetime
from datetime import timedelta
from aula.apps.tutoria.models import Actuacio, Tutor, SeguimentTutorialPreguntes,\
    SeguimentTutorial, SeguimentTutorialRespostes, ResumAnualAlumne,\
    CartaAbsentisme
from aula.apps.alumnes.models import Alumne, Grup, AlumneGrupNom, AlumneGrup
from django.forms.models import modelform_factory, modelformset_factory
from django import forms
from django.db.models import Min, Max, Q
from .views_data import justificadorMKTable

#exceptions
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS,\
    ObjectDoesNotExist
from django.http import Http404
from aula.apps.horaris.models import FranjaHoraria, Horari
from aula.apps.incidencies.models import Incidencia, Expulsio
from aula.utils.tools import llista, unicode
from aula.apps.avaluacioQualitativa.forms import alumnesGrupForm
from aula.utils.forms import dataForm, ckbxForm, choiceForm
from aula.apps.avaluacioQualitativa.models import RespostaAvaluacioQualitativa
import json as simplejson
from django.core import serializers
from aula.apps.tutoria.reports import reportCalendariCursEscolarTutor
from aula.apps.tutoria.rpt_elsMeusAlumnesTutorats import elsMeusAlumnesTutoratsRpt
from aula.apps.tutoria.others import calculaResumAnualProcess
from aula.apps.tutoria.rpt_gestioCartes import gestioCartesRpt
from aula.apps.tutoria import report_carta_absentisme
from aula.apps.tutoria.report_carta_absentisme import report_cartaAbsentisme
from aula.apps.tutoria.rpt_totesLesCartes import totesLesCartesRpt
from django.urls import reverse
from aula.apps.sortides.models import Sortida
from aula.apps.sortides.table2_models import Table2_Sortides
from django_tables2.config import RequestConfig
from aula.utils.my_paginator import DiggPaginator
from aula.apps.tutoria.table2_models import Table2_Actuacions

from django.contrib import messages
from django.conf import settings

@login_required
@group_required(['professors'] )
def incidenciesGestionadesPelTutor(request):


    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    professor = get_object_or_404(Professor, pk=user.pk)

    alumnes_grup = Q( grup__tutor__professor = professor )
    alumnes_tutor_individualitzat = Q( tutorindividualitzat__professor = professor )

    alumnes_tutoritzats = list( Alumne.objects.filter( alumnes_grup | alumnes_tutor_individualitzat ) )


    if user != professor.getUser():
        return HttpResponseRedirect('/')

    # Expulsions pendents:
    expulsionsPendentsPerAcumulacio = []

    # alumne -> incidencies i expulsions
    alumnes = {}
    incidencies_gestionades_pel_tutor = ( Incidencia
                                          .objects
                                          .filter(alumne__in=alumnes_tutoritzats)
                                          .filter(gestionada_pel_tutor=True)
                                          .filter(tipus__es_informativa=False)
                                          .all())
    for incidencia in incidencies_gestionades_pel_tutor:
        alumne_str = unicode(incidencia.alumne)
        incidenciesAlumne = incidencia.alumne.incidencia_set.filter(
            gestionada_pel_tutor=True,
            es_vigent=True,
            tipus__es_informativa=False,
        )
        calTramitarExpulsioPerAcumulacio = ( settings.CUSTOM_INCIDENCIES_PROVOQUEN_EXPULSIO and
                                             incidenciesAlumne.count() >= 3 )
        exempleIncidenciaPerAcumulacio = ( incidenciesAlumne.order_by('dia_incidencia').reverse()[0]
                                           if calTramitarExpulsioPerAcumulacio
                                           else None )
        if calTramitarExpulsioPerAcumulacio and alumne_str not in alumnes:
            exempleIncidenciaPerAcumulacio.aux_origen = "tutoria"
            expulsionsPendentsPerAcumulacio.append(exempleIncidenciaPerAcumulacio)

        alumnes.setdefault(alumne_str, {
            'calTramitarExpulsioPerAcumulacio': calTramitarExpulsioPerAcumulacio,
            'exempleIncidenciaPerAcumulacio': exempleIncidenciaPerAcumulacio,
            'alumne': incidencia.alumne,
            'grup': incidencia.alumne.grup,
            'incidencies': [],
            'expulsions': []})
        alumnes[alumne_str]['incidencies'].append(incidencia)

    alumnesOrdenats = [ (alumneKey, alumnes[alumneKey],) for alumneKey in sorted(iter(alumnes.keys())) ]

    hi_ha_expulsions_per_acumulacio = bool(len(expulsionsPendentsPerAcumulacio))

    table2_expulsionsPendentsPerAcumulacio = Table2_ExpulsionsPendentsPerAcumulacio(expulsionsPendentsPerAcumulacio)

    diccionariTables = dict()
    for alumne_key, alumne_dades in alumnesOrdenats:
        expulsionsPerAlumne = alumne_dades.get('expulsions',[])
        incidenciesPerAlumne = alumne_dades.get('incidencies', [])
        expulsionsIIncidenciesPerAlumne = Table2_ExpulsionsIIncidenciesPerAlumne(expulsionsPerAlumne
                                                                                 + incidenciesPerAlumne)
        expulsionsIIncidenciesPerAlumne.columns.hide('Eliminar')

        diccionariTables[alumne_key + ' - ' + unicode(alumne_dades['grup'])] = expulsionsIIncidenciesPerAlumne

    # RequestConfig(request).configure(table)
    # RequestConfig(request).configure(table2)

    return render(
        request,
        'incidenciesProfessional.html',
        {
         'expulsionsPendentsPerAcumulacioBooelan': hi_ha_expulsions_per_acumulacio,
         'expulsionsPendentsPerAcumulacio': table2_expulsionsPendentsPerAcumulacio,
         'expulsionsIIncidenciesPerAlumne': diccionariTables,
         },
    )


@login_required
@group_required(['professors'])
def tutorPosaExpulsioPerAcumulacio(request, pk):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    incidencia = get_object_or_404(Incidencia, pk=pk)

    professional = incidencia.professional
    professor = User2Professor(professional.getUser())
    alumne = incidencia.alumne

    # seg---------
    te_permis = (l4 or professor in alumne.tutorsDeLAlumne() )
    if not te_permis:
        raise Http404()

    # si l'expulsió ja ha estat generada abans l'envio a l'expulsió
    # seria el cas que seguissin l'enllaç d'un Missatge:

    if incidencia.provoca_expulsio:
        url_next = '/incidencies/editaExpulsio/{0}/'.format(incidencia.provoca_expulsio.pk)
        return HttpResponseRedirect(url_next)

    incidencies = alumne.incidencia_set.filter(
        es_vigent=True,
        tipus__es_informativa=False,
        gestionada_pel_tutor=True,
    )
    enTe3oMes = incidencies.count() >= 3
    url_next = '/tutoria/incidenciesGestionadesPelTutor/'  # todo: a la pantalla d''incidencies

    if enTe3oMes:

        str_incidencies = u", ".join(
            [u"{descripcio} ({dia})".format(descripcio=i.descripcio_incidencia, dia=i.dia_incidencia)
             for i in incidencies])
        professor_recull = User2Professor(user)
        motiu_san = u'''Expulsió per acumulació d'incidències gestionada pel tutor Sr(a) {0}: {1}'''.format(
            professor_recull, str_incidencies)

        try:
            expulsio = Expulsio.objects.create(
                estat='AS',
                professor_recull=professor_recull,
                professor=professor,
                alumne=alumne,
                dia_expulsio=incidencia.dia_incidencia,
                franja_expulsio=incidencia.franja_incidencia,
                motiu=motiu_san,
                es_expulsio_per_acumulacio_incidencies=True
            )

            # LOGGING
            Accio.objects.create(
                tipus='EE',
                usuari=user,
                l4=l4,
                impersonated_from=request.user if request.user != user else None,
                text=u"""Creada expulsió d'alumne {0} per acumulació d'incidències. Gestionada pel tutor.""".format(expulsio.alumne)
            )

            expulsio_despres_de_posar(expulsio)
            incidencies.update(es_vigent=False, provoca_expulsio=expulsio)
            missatge = u"""Generada expulsió per acumulació d'incidències. Alumne/a: {0}. 
                           Pots gestionar l'expulsió des de menú incidències""".format(expulsio.alumne)
            url_expulsio = r"/incidencies/editaExpulsio/{0}/".format(expulsio.pk)
            missatge = mark_safe( escape( missatge ) +
                                  r"<a href='{url}'>o accedir-hi directament a l'expulsió</a>".format(url=url_expulsio ) )
            messages.info(request, missatge)
        except ValidationError as e:
            missatge =  u"""Error en generar l'expulsió: {errors}""".format( u" - ".join(itertools.chain(*e.message_dict.values()) ) )
            messages.error(request, missatge)

    return HttpResponseRedirect(url_next)


@login_required
@group_required(['professors','professional'])
def lesMevesActuacions(request):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professional = User2Professional( user )     
    
    actuacions = ( Actuacio
                   .objects
                   .filter( professional = professional )
                   .distinct()
                  )

    table = Table2_Actuacions( list( actuacions ) ) 
    table.order_by = '-moment_actuacio' 
    
    RequestConfig(request, paginate={"paginator_class":DiggPaginator , "per_page": 20}).configure(table)
        
    return render(
                  request, 
                  'lesMevesActuacions.html', 
                  {'table': table,
                   }
                 )       
#     
#     -----------------------------###  OBSOLET ###-----------------------------
#
#
#
#     report = []
#     for alumne in  Alumne.objects.filter( actuacio__professional = professional ).distinct():
#             taula = tools.classebuida()
# 
#             taula.titol = tools.classebuida()
#             taula.titol.contingut = ''
#             taula.titol.enllac = None
# 
#             taula.capceleres = []
#             
#             capcelera = tools.classebuida()
#             capcelera.amplade = 200
#             capcelera.contingut = u'{0} ({1})'.format(unicode( alumne ) , unicode( alumne.grup ) )
#             capcelera.enllac = reverse('tutoria__alumne__detall', args=[ alumne.pk , 'all' ])
#             taula.capceleres.append(capcelera)
# 
#             capcelera = tools.classebuida()
#             capcelera.amplade = 70
#             capcelera.contingut = u'Qui?'
#             taula.capceleres.append(capcelera)
# 
#             capcelera = tools.classebuida()
#             capcelera.amplade = 70
#             capcelera.contingut = u'Amb qui?'
#             taula.capceleres.append(capcelera)
#             
#             capcelera = tools.classebuida()
#             capcelera.amplade = 200
#             capcelera.contingut = u'Assumpte'
#             taula.capceleres.append(capcelera)
#             
#             capcelera = tools.classebuida()
#             capcelera.amplade = ''
#             capcelera.contingut = u'Esborra'
#             taula.capceleres.append(capcelera)
#             
#             taula.fileres = []
#             for actuacio in alumne.actuacio_set.filter( professional = professional).order_by('moment_actuacio').reverse():
#                 
#                 filera = []
#                 
#                 #-moment--------------------------------------------
#                 camp = tools.classebuida()
#                 camp.enllac = None
#                 camp.contingut = unicode(actuacio.moment_actuacio)
#                 camp.enllac = "/tutoria/editaActuacio/{0}".format( actuacio.pk )
#                 filera.append(camp)
# 
#                 #-qui--------------------------------------------
#                 camp = tools.classebuida()
#                 camp.enllac = None
#                 camp.contingut = u'''{0} ({1})'''.format(
#                                              unicode( actuacio.professional ),
#                                              unicode(actuacio.get_qui_fa_actuacio_display() ) )
#                 filera.append(camp)
# 
#                 #-amb qui--------------------------------------------
#                 camp = tools.classebuida()
#                 camp.enllac = None
#                 camp.contingut = unicode(actuacio.get_amb_qui_es_actuacio_display() )
#                 filera.append(camp)
# 
#                 #-assumpte--------------------------------------------
#                 camp = tools.classebuida()
#                 camp.enllac = None
#                 camp.contingut = unicode(actuacio.assumpte )
#                 filera.append(camp)
# 
#                 #-delete--------------------------------------------
#                 camp = tools.classebuida()
#                 camp.enllac = '/tutoria/esborraActuacio/{0}'.format(actuacio.pk )
#                 camp.contingut = '[ X ]'
#                 filera.append(camp)
# 
# 
#                 #--
#                 taula.fileres.append( filera )
#             
#             report.append(taula)
#         
#     return render(
#                 request,
#                 'actuacions.html',
#                     {'report': report,
#                      'head': 'Informació actuacions' ,
#                     },
#                   )
#         

from aula.apps.alumnes.forms import triaAlumneForm, triaAlumneSelect2Form

@login_required
@group_required(['professors','professional'])
def novaActuacio(request):

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
    formset = []
    if request.method == 'POST':
        
        actuacio = Actuacio()
        actuacio.professional = User2Professional( user)
        actuacio.credentials = credentials
        formAlumne = triaAlumneSelect2Form(request.POST ) #todo: multiple=True (multiples alumnes de cop)  
        widgets = { 'moment_actuacio': DateTimeTextImput()}      
        formActuacioF = modelform_factory(Actuacio, exclude=['alumne','professional'], widgets = widgets)
        formActuacio = formActuacioF(request.POST, instance = actuacio ) 
        if formAlumne.is_valid():
            
            alumne = formAlumne.cleaned_data['alumne']
            #actuacio = formActuacio.save(commit=False)
            actuacio.alumne = alumne
            if formActuacio.is_valid():
                actuacio.save()

                #LOGGING
                Accio.objects.create( 
                        tipus = 'AC',
                        usuari = user,
                        l4 = l4,
                        impersonated_from = request.user if request.user != user else None,
                        text = u"""Enregistrada actuació a l'alumne {0}. """.format( actuacio.alumne )
                    )          
                
                messages.success(request, u"Actuació desada correctament")
                
                url = '/tutoria/lesMevesActuacions/'
                return HttpResponseRedirect( url )    

        formset.append( formAlumne )
        formset.append( formActuacio )
        
    else:

        formAlumne = triaAlumneSelect2Form( ) #todo: multiple=True (multiples alumnes de cop)       
        widgets = { 'moment_actuacio': DateTimeTextImput()} 
        formActuacio = modelform_factory(Actuacio, exclude=['alumne','professional'],widgets = widgets) 

        formset.append( formAlumne )
        formset.append( formActuacio )
    
    
        
    return render(
                request,
                'formset.html',
                    {'formset': formset,
                     'head': 'Actuació' ,
                     'titol_formulari': u"Alta d'una nova actuació",                     
                    },
                )


@login_required
@group_required(['professors','professional'])
def editaActuacio(request, pk):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    
    actuacio = Actuacio.objects.get( pk = pk)
    
    professor = User2Professor(user)
    
    #seg-------------------
    te_permis = (l4 or 
                actuacio.professional.pk == user.pk or  
                professor in actuacio.alumne.tutorsDeLAlumne() or
                user.groups.filter(name__in= [u'direcció', u'psicopedagog'] ).exists() 
                )
    if  not te_permis:
        raise Http404() 
    
    
    actuacio.credentials = credentials

    infoForm = [
          ('Alumne',unicode( actuacio.alumne) ),
          ('Professional', unicode( actuacio.professional ) )      
                ]
    
    widgets = { 'moment_actuacio': DateTimeTextImput()}      
    formActuacioF = modelform_factory(Actuacio, exclude=['alumne','professional'], widgets = widgets)
    #formActuacioF.base_fields['moment_actuacio'].widget = forms.DateTimeInput(attrs={'class':'DateTimeAnyTime'} )
    formset = []
    if request.method == 'POST':
        
        formActuacio = formActuacioF(request.POST, instance = actuacio ) 
        if formActuacio.is_valid():
            actuacio.save()

            #LOGGING
            Accio.objects.create( 
                    tipus = 'AC',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Editada actuació a l'alumne {0}. """.format( actuacio.alumne )
                )     
            
            messages.success(request, u"Actuació desada correctament")
                            
            url = '/tutoria/lesMevesActuacions/'
            
            return HttpResponseRedirect( url )    

        formset.append( formActuacio )
        
    else:

        formActuacio = formActuacioF( instance = actuacio ) 

        formset.append( formActuacio )
        
    return render(
                request,
                'formset.html',
                    {'formset': formset,
                     'infoForm': infoForm,
                     'head': 'Actuació' ,
                     'titol_formulari': u"Edició d'una actuació",
                    },
                )

@login_required
@group_required(['professors','professional'])
def esborraActuacio(request, pk):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    
    actuacio = Actuacio.objects.get( pk = pk )
    
    #seg-------------------
    te_permis = l4 or actuacio.professional.pk == user.pk 
    if  not te_permis:
        raise Http404()
            
    actuacio.credentials = credentials
    url_next = '/tutoria/lesMevesActuacions/'
    try:
        actuacio.delete()
        messages.success(request, u"Actuació esborrada")

        #LOGGING
        Accio.objects.create( 
                tipus = 'AC',
                usuari = user,
                l4 = l4,
                impersonated_from = request.user if request.user != user else None,
                text = u"""Esborrada actuació a l'alumne {0}. """.format( actuacio.alumne )
            )     
                        
    except ValidationError as e:
        import itertools
        resultat = { 'errors': list( itertools.chain( *e.message_dict.values() ) ), 
                    'warnings':  [], 'infos':  [], 'url_next': url_next }
        return render(
                       request,
                       'resultat.html', 
                       {'head': u'Error a l\'esborrar actuació.' ,
                        'msgs': resultat },
                     )
            
    return HttpResponseRedirect( url_next )  

@login_required
@group_required(['professors'])
def justificaFaltes(request, pk, year, month, day):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)

    formset = []    
    head='Justificar faltes'
    missatge = ''
    
    alumne = get_object_or_404( Alumne, pk = int(pk) )
    
    #---seg-----
    esAlumneTutorat = professor in alumne.tutorsDeLAlumne() 
    te_permis = l4 or esAlumneTutorat
    if  not te_permis:
        raise Http404()     
    
    algunDeBe = False
    
    dia_impartir = date( year = int(year), month = int(month), day = int(day) )

    ControlAssistenciaFormF = modelformset_factory(ControlAssistencia, fields=( 'estat',), extra = 0 )
 
    controls = ControlAssistencia.objects.filter(
                            alumne = alumne,                            
                            impartir__dia_impartir = dia_impartir                           
                        ).order_by( 'alumne', '-impartir__dia_impartir', 'impartir__horari__hora'  )
       
    if request.method == 'POST':
        
        formCA=ControlAssistenciaFormF(request.POST, prefix='ca',queryset  = controls )

        for form in formCA: 
            control_a = form.instance
            form.fields['estat'].label = u'{0} {1} {2}'.format( control_a.alumne, control_a.impartir.dia_impartir, control_a.impartir.horari.hora )
            form.instance.credentials = credentials
            if 'estat' in form.changed_data and form.is_valid():
                ca=form.save(commit=False)
                ca.credentials = credentials
                algunDeBe = True
                ca=form.save()
        
        if algunDeBe:
            missatge = u'Les faltes han estat justificades.' 
            #LOGGING
            Accio.objects.create( 
                    tipus = 'JF',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Justificades faltes de l'alumne {0} del dia {1}. """.format( alumne, dia_impartir )
                )                 
        else: 
            missatge = u'''No s'ha justificat cap falta.'''        
        
    else:    
        controls = ControlAssistencia.objects.filter(
                            alumne = alumne,                            
                            impartir__dia_impartir = dia_impartir                          
                        ).order_by( 'alumne', '-impartir__dia_impartir', 'impartir__horari__hora'  )
                        
        formCA=ControlAssistenciaFormF( prefix='ca',queryset  = controls )
        
        for form in formCA: 
            control_a = form.instance
            form.fields['estat'].label = u'{0} {1} {2}'.format( control_a.alumne, control_a.impartir.dia_impartir, control_a.impartir.horari.hora )


        
    return render(
                  request,
                  "formset.html", 
                  {"formset": formCA,
                   "head": head,
                   "missatge": missatge,
                   },
                 )

@login_required
@group_required(['professors'])
def informeSetmanalMKTable(request, pk, year, month, day, inclouControls = True, inclouIncidencies = True):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
    
    data = date( year = int(year), month= int(month), day = int(day) )
    
    alumnes = None
    if pk == 'all':
        q_tutors_individualitat = Q( tutorindividualitzat__professor = professor )
        q_tutors_grup = Q( grup__tutor__professor = professor )
        alumnes = Alumne.objects.filter(q_tutors_individualitat | q_tutors_grup   ).distinct()
        grup = "Tots els alumnes"
    else:
        grup = Grup.objects.get( pk = int(pk) )
        alumnes = grup.alumne_set.all()
    
    pk_alumnes = [ a.pk for a in alumnes ]
    
    #busco el dilluns i el divendres
    dia_de_la_setmana = data.weekday()
     
    delta = timedelta( days = (-1 * dia_de_la_setmana ) )
    dilluns = data + delta
    
    #named instances
    estatPresent = EstatControlAssistencia.objects.get( codi_estat = 'P' )
    estatFalta = EstatControlAssistencia.objects.get( codi_estat = 'F' )
    estatJustificada = EstatControlAssistencia.objects.get( codi_estat = 'J' )
    estatRetras = EstatControlAssistencia.objects.get( codi_estat = 'R' )
    
    #marc horari per cada dia
    dades = tools.classebuida()
    dades.grup = grup
    dades.alumnes = alumnes.order_by( 'cognoms', 'nom' )
    dades.f = []
    dades.r = []
    dades.j = []
    dades.I = []
    dades.i = []
    dades.E = []
    dades.e = [] 
    dades.c = []    #controls

    
    dades.dia_hores = tools.diccionari()
    dades.marc_horari = {}
    for delta in [0,1,2,3,4]:
        dia = dilluns + timedelta( days = delta )
        
        forquilla = Horari.objects.filter( 
                                    impartir__controlassistencia__alumne__in = pk_alumnes,
                                    impartir__dia_impartir = dia                                            
                                ).aggregate( desde=Min( 'hora__hora_inici' ), finsa=Max( 'hora__hora_inici' )  )
        if forquilla['desde'] and forquilla['finsa']:
            dades.marc_horari[dia] = { 'desde':forquilla['desde'],'finsa':forquilla['finsa']}
            dades.dia_hores[dia] = llista()
            for hora in FranjaHoraria.objects.filter( hora_inici__gte = forquilla['desde'],
                                                      hora_inici__lte = forquilla['finsa'] ).order_by('hora_inici'):
                dades.dia_hores[dia].append(hora)            
        
    dades.quadre = tools.diccionari()
    
    for alumne in dades.alumnes:

        dades.quadre[unicode(alumne)] = []

        for dia, hores in dades.dia_hores.itemsEnOrdre():
            
            hora_inici = FranjaHoraria.objects.filter( hora_inici = dades.marc_horari[dia]['desde'] ).first()
            hora_fi    = FranjaHoraria.objects.filter( hora_inici = dades.marc_horari[dia]['finsa'] ).last()

            q_controls = Q( impartir__dia_impartir = dia ) & \
                         Q( impartir__horari__hora__gte = hora_inici) & \
                         Q( impartir__horari__hora__lte = hora_fi) & \
                         Q( alumne = alumne )

            controls = [ c for c in ControlAssistencia.objects.filter( q_controls ) ]

            q_incidencia = Q(dia_incidencia = dia) & \
                            Q(franja_incidencia__gte = hora_inici) & \
                            Q(franja_incidencia__lte = hora_fi) & \
                            Q(alumne = alumne)

            incidencies = [ i for i in  Incidencia.objects.filter( q_incidencia ) ]                                   

            q_expulsio = Q(dia_expulsio = dia) & \
                         Q(franja_expulsio__gte = hora_inici) & \
                         Q(franja_expulsio__lte = hora_fi) & \
                         Q(alumne = alumne) & \
                         ~Q(estat = 'ES') 

            expulsions = [ e for e in Expulsio.objects.filter( q_expulsio ) ]                    

            for hora in hores:
     
                cella = tools.classebuida()
                cella.txt = ''
                #present = estatPresent in [ c.estat for c in controls]
                hiHaControls = len( [ c for c in controls if c.impartir.horari.hora == hora] )>0
                haPassatLlista = hiHaControls and len( [ c for c in controls if c.estat is not None and c.impartir.horari.hora == hora] )>0
                
                if inclouIncidencies:
                    cella.f = [ c for c in controls if c.estat == estatFalta and c.impartir.horari.hora == hora]
                    cella.r = [ c for c in controls if c.estat == estatRetras and c.impartir.horari.hora == hora] 
                    cella.j = [ c for c in controls if c.estat == estatJustificada and c.impartir.horari.hora == hora ]
                    cella.I = [ i for i in incidencies if not i.tipus.es_informativa and i.franja_incidencia == hora ]
                    cella.i = [ i for i in incidencies if i.tipus.es_informativa and i.franja_incidencia == hora]
                    cella.E = [e for e in expulsions if not e.es_expulsio_per_acumulacio_incidencies and e.franja_expulsio == hora ] 
                    cella.e = [e for e in expulsions if  e.es_expulsio_per_acumulacio_incidencies and e.franja_expulsio == hora ] 
                else:
                    cella.f = []
                    cella.r = []
                    cella.j = []
                    cella.I = []
                    cella.i = []
                    cella.E = []
                    cella.e = []

                if inclouControls:
                    cella.c = [ c for c in controls if c.impartir.horari.hora == hora]
                else:
                    cella.c = [ ]
                    
                dades.f.extend(cella.f)
                dades.r.extend(cella.r)
                dades.j.extend(cella.j)
                dades.I.extend(cella.I)
                dades.i.extend(cella.i)
                dades.E.extend(cella.E)
                dades.e.extend(cella.e)
                dades.c.extend(cella.c)

                if not hiHaControls:
                    cella.color = '#505050'
                else:
                    if not haPassatLlista:
                        cella.color = '#E0E0E0'
                    else:
                        cella.color = 'white'
                
                if hora == hora_inici:
                    cella.primera_hora = True
                else:
                    cella.primera_hora = False
                
                dades.quadre[unicode(alumne)].append( cella )
                
    return dades

@login_required
@group_required(['professors'])
def informeSetmanalPrint(request, pk, year, month, day, suport):
    #pk és el grup. Per tots els alumnes tutorats marcar pk = All.
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)

    #--seg----
    grup = Grup.objects.get( pk = int(pk) ) if pk != 'all' else 'Tots els alumnes'
    esTutorDelGrup = pk != 'all' and grup in Grup.objects.filter( tutor__professor = professor )
    teAlumnesTutoratsIndividuals = pk == 'all' and professor.tutorindividualitzat_set.count() > 0
    tePermis = l4 or esTutorDelGrup or teAlumnesTutoratsIndividuals
    if not tePermis:
        raise Http404()

    errorsTrobats = None

    try:
        dades = informeSetmanalMKTable(request, pk, year, month, day)
 
    except Exception as e:
        errorsTrobats = e
                                              
    if errorsTrobats:
        url_next = 'javascript:window.close();'
        resultat = { 'errors': [ errorsTrobats ], 
                'warnings':  [], 'infos':  [], 'url_next': url_next }
        return render(
                   request,
                   'resultat.html', 
                   {'head': u'Error preparant el llistat:' ,
                    'msgs': resultat },
                   )
    else:
        return render(
              request,
              "informeSetmanal.html", 
              {"head": u'Informe setmanal grup {0}'.format( grup ),
               "dades": dades
               },
              )

        

@login_required
@group_required(['professors'])
def informeSetmanal(request):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
        
    head='Informe setmanal'
    
    grups = Grup.objects.filter( tutor__professor = professor )

    
    if request.method == "POST":
        form = informeSetmanalForm( data = request.POST, queryset = grups )
        if form.is_valid():
            grup = form.cleaned_data['grup']
            data = form.cleaned_data['data']
            url_next = '/tutoria/informeSetmanalPrint/{0}/{1}/{2}/{3}/{4}'.format( grup.pk if grup else 'all', data.year, data.month, data.day,'html' )
            return HttpResponseRedirect(  url_next)
        else:
            msg = u"Comprova que has seleccionat correctament el grup i la data."
            url_next = 'javascript:window.close();'
            resultat = { 'errors': [ msg ], 
                    'warnings':  [], 'infos':  [], 'url_next': url_next }
            return render(
                       request,
                       'resultat.html', 
                       {'head': u'Error preparant el llistat:' ,
                        'msgs': resultat },
                       )


    else:
        

        grupInicial = { 'grup': grups[0]} if grups else {}
        if not grups and professor.tutorindividualitzat_set.count()  == 0:
            return render(
                        request,
                        'resultat.html', 
                        {'head': u'Justificador de faltes' ,
                         'msgs': { 'errors': [], 'warnings':  [u'Sembla ser que no tens grups assignats'], 'infos':  [] } },
                        )
        
        form = informeSetmanalForm(  queryset = grups, initial = grupInicial )
        
        
    return render(
                  request,
                  "form.html", 
                  {"form": form,
                   "head": head,
                   "target":"blank_"
                   },
                  )
    

@login_required
@group_required(['professors'])
def justificaNext(request, pk):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
    
    #--seg----
    control = ControlAssistencia.objects.get( pk = int(pk) )
    esTutor = professor in  control.alumne.tutorsDeLAlumne() 
    tePermis = l4 or esTutor
    if not tePermis:
        raise Http404()
        pass

    justificada = EstatControlAssistencia.objects.get( codi_estat = 'J' )
    
    ok = True
    errors = []
    jaEstaJustifiada = control.estat and control.estat == justificada
    if not jaEstaJustifiada or control.swaped:
        if control.swaped:
            control.estat, control.estat_backup = control.estat_backup, None
            control.professor, control.professor_backup = control.professor_backup, None
        else:
            control.estat_backup, control.estat = control.estat, justificada
            control.professor_backup, control.professor = control.professor, professor

        try:
            control.swaped = not control.swaped
            control.credentials = credentials
            control.save()

            #LOGGING
            Accio.objects.create( 
                    tipus = 'JF',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Justificades faltes de l'alumne {0} del dia {1}. """.format( control.alumne, control.impartir.dia_impartir )
                )                
        except ValidationError as e:
            ok=False
            import itertools
            errors = list( itertools.chain( *e.message_dict.values() )  )        

    resposta = {
        'ok' :  ok,
        'codi': control.estat.codi_estat if control.estat else ' ',
        'missatge': control.descripcio,
        'errors':  errors,
        'swaped' : (control.swaped)
    }
    
    return HttpResponse( simplejson.dumps(resposta, ensure_ascii=False ) ,content_type= 'application/json')


    
@login_required
@group_required(['professors'])
def faltaNext(request, pk):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
    
    #--seg----
    control = ControlAssistencia.objects.get( pk = int(pk) )
    esTutor = professor in  control.alumne.tutorsDeLAlumne() 
    tePermis = l4 or esTutor
    if not tePermis:
        raise Http404()
        pass

    justificada = EstatControlAssistencia.objects.get( codi_estat = 'J' )
    falta = EstatControlAssistencia.objects.get( codi_estat = 'F' )
    
    ok = True
    errors = []
    jaEstaFalta = control.estat and control.estat == falta
    if not jaEstaFalta or control.swaped:
        if control.swaped:
            control.estat, control.estat_backup = control.estat_backup, None
            control.professor, control.professor_backup = control.professor_backup, None
        else:
            control.estat_backup, control.estat = control.estat, falta
            control.professor_backup, control.professor = control.professor, professor

        try:
            control.swaped = not control.swaped
            control.credentials = credentials
            control.save()

            #LOGGING
            Accio.objects.create( 
                    tipus = 'JF',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Correcció de presència de l'alumne {0} del dia {1}. """.format( control.alumne, control.impartir.dia_impartir )
                )                
        except ValidationError as e:
            ok=False
            import itertools
            errors = list( itertools.chain( *e.message_dict.values() )  )        

    resposta = {
        'ok' :  ok,
        'codi': control.estat.codi_estat if control.estat else ' ',
        'missatge': control.descripcio,
        'errors':  errors,
        'swaped' : (control.swaped)
    }
    
    return HttpResponse( simplejson.dumps(resposta, ensure_ascii=False ) ,content_type= 'application/json')



@login_required
@group_required(['professors'])
def justificador(request, year, month, day):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
        
    errorsTrobats = None
    
    dades = justificadorMKTable(request, year, month, day)

    #navegacio pel calencari:
    import datetime as t

    data = t.date(  int(year), int(month), int(day) )
    altres_moments = [
           [ professor.username, '<< mes passat'    , data + t.timedelta( days = -30 )],
           [ professor.username, '< setmana passada' , data + t.timedelta( days = -7 )],
           [ professor.username, '< avui >'    , t.date.today ],
           [ professor.username, 'setmana vinent >'  , data + t.timedelta( days = +7 ) ],
           [ professor.username, 'mes vinent >>'      , data + t.timedelta( days = +30 ) ],
        ]        
                                              
    return render(
              request,
              "justificator.html", 
              {"head": u'Justificar faltes de tutorats de {0}'.format( professor ),
               "dades": dades,
               "altres_moments": altres_moments
               },
              )
    
@login_required
@group_required(['professors'])
def justificaFaltesPre(request):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
    
    #prefixes:
    #https://docs.djangoproject.com/en/dev/ref/forms/api/#prefixes-for-forms    
    formset = []
    
    head='Justificar faltes'

    #---------------------------------Passar llista -------------------------------

    q_grups_tutorats = Q( grup__in =  [ t.grup for t in professor.tutor_set.all() ] )
    q_alumnes_tutorats = Q( pk__in = [ti.alumne.pk for ti in professor.tutorindividualitzat_set.all() ]  )
    query = AlumneGrup.objects.filter( q_grups_tutorats | q_alumnes_tutorats )
    
    if request.method == "POST":

        formPas1=justificaFaltesW1Form( request.POST, queryset = query )
        if formPas1.is_valid():            
            alumne = formPas1.cleaned_data['alumne']
            dia_impartir = formPas1.cleaned_data['data']
            if alumne:
                url_next = '/tutoria/justificaFaltes/{0}/{1}/{2}/{3}'.format( alumne.pk, dia_impartir.year, dia_impartir.month, dia_impartir.day  )
            else: 
                url_next = '/tutoria/justificador/{0}/{1}/{2}'.format( dia_impartir.year, dia_impartir.month, dia_impartir.day  )
            return HttpResponseRedirect( url_next )
        else:
            formset.append( formPas1 )
    else:
        form=justificaFaltesW1Form( queryset = query )
        formset.append( form )
            
    return render(
                  request,
                  "formset.html", 
                  {"formset": formset,
                   "head": head,
                   },
                 )
    
    



@login_required
@group_required(['professors'])
def elsMeusAlumnesTutorats(request):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    report = elsMeusAlumnesTutoratsRpt( professor )
        
    return render(
                request,
                'report.html',
                    {'report': report,
                     'head': 'Els meus alumnes tutorats' ,
                    },
                )


@login_required
@group_required(['professors'])
def gestioCartes(request):
    
    #TODO: Vaig per aquí cartes absència

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
    professor = User2Professor( user )     
    
    report = gestioCartesRpt( professor, l4 )
        
    return render(
                request,
                'report.html',
                    {'report': report,
                     'head': 'Els meus alumnes tutorats' ,
                    },
                )

@login_required
@group_required(['professors'])
def novaCarta(request, pk_alumne ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
    alumne = get_object_or_404(Alumne,  pk = pk_alumne )
                
    #seg-------------------
    te_permis = (l4 or 
                professor in alumne.tutorsDeLAlumne() )
    if  not te_permis:
        raise Http404() 

    carta = CartaAbsentisme( alumne = alumne , professor = professor )
    frmFact = modelform_factory(CartaAbsentisme, fields=('data_carta', ))
    if request.method == 'POST':
        form = frmFact( request.POST, instance = carta )
        if form.is_valid():
            form.save()
            url_next = r'/tutoria/gestioCartes/#{0}'.format( carta.pk )   
            return HttpResponseRedirect( url_next )
    else:
        form = frmFact(  instance = carta )
    
    form.fields['data_carta'].widget = DateTextImput()
    
    return render(
                request,
                'form.html', 
                {'form': form, 
                 'head': u'Carta absentisme'},
                )

@login_required
@group_required(['professors'])        
def imprimirCarta(request, pk_carta, flag  ):        
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
    carta = get_object_or_404(CartaAbsentisme,  pk = pk_carta )
    carta.impresa = flag
    carta.save()
                
    #seg-------------------
    te_permis = (l4 or 
                professor in carta.alumne.tutorsDeLAlumne()
                or
                user.groups.filter(name__in= [u'direcció', ] ).exists()
                )
    if  not te_permis:
        raise Http404() 
    
    return report_cartaAbsentisme(   request, carta )
    
@login_required
@group_required(['direcció'])        
def esborraCarta(request, pk_carta ):        
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
    carta = get_object_or_404(CartaAbsentisme,  pk = pk_carta )
    carta.delete()
                
    #seg-------------------
    te_permis = (l4 or 
                professor in carta.alumne.tutorsDeLAlumne() and 1==2   #potser deixar-los esborrar cartes durant uns minuts ??
                )
    if  not te_permis:
        raise Http404() 
    
    url_next = r'/tutoria/gestioCartes/'
    return HttpResponseRedirect( url_next )
    

@login_required
@group_required(['direcció'])
def totesLesCartes(request):
    
    #TODO: Vaig per aquí cartes absència

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
    professor = User2Professor( user )     
    
    report = totesLesCartesRpt(  )
        
    return render(
                request,
                'report.html',
                    {'report': report,
                     'head': 'Els meus alumnes tutorats' ,
                    },
                )



@login_required
@group_required(['professors'])
def elsMeusAlumnesTutoratsEntreDates(request):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    if user.groups.filter(name='direcció'):
        possibles_grups = [ ( t.pk, unicode( t) ) for t in Grup.objects.filter(alumne__isnull = False).distinct().order_by("descripcio_grup") ]
    else:
        possibles_grups = [ ( t.grup.pk, unicode( t.grup) ) for t in  Tutor.objects.filter( professor = professor )]
        
    possibles_grups.append( ( 'ElsMeusAlumnes', 'Els Meus Alumnes', ) )
    
    if request.method == 'POST':
        form = elsMeusAlumnesTutoratsEntreDatesForm( request.POST, grups = possibles_grups ) 
        
        if form.is_valid():
            parm_professor = None
            parm_grup = None
            if form.cleaned_data['grup'] == 'ElsMeusAlumnes':
                parm_professor = professor
            else:
                parm_grup = form.cleaned_data['grup']
            parm_dataDesDe = form.cleaned_data['dataDesDe']
            parm_dataFinsA = form.cleaned_data['dataFinsA']
            
            report = elsMeusAlumnesTutoratsRpt( parm_professor, parm_grup, parm_dataDesDe, parm_dataFinsA )
                
            return render(
                        request,
                        'report.html',
                            {'report': report,
                             'head': 'Consulta Assistència Entre Dates' ,
                            },
                        )
    else:
        form = elsMeusAlumnesTutoratsEntreDatesForm( grups = possibles_grups )
        
    return render(
                request,
                'form.html', 
                {'form': form, 
                 'head': 'Consulta Assistència Entre Dates'},
                )



#---------------------  --------------------------------------------#

    
@login_required
@group_required(['professors',])
def detallTutoriaAlumne( request, pk , detall = 'all'):

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
    professor = User2Professor( user )     
    
    alumne = get_object_or_404(Alumne, pk = pk )
    
    esTutorat = l4 or \
                professor in alumne.tutorsDeLAlumne() or \
                user.groups.filter(name__in= [u'direcció', u'psicopedagog'] ).exists()  
    
    if not esTutorat:
        raise Http404 
    
    head = u'{0} ({1})'.format(alumne , unicode( alumne.grup ) )
    
    report = []

    #---dades alumne---------------------------------------------------------------------
    if detall in ['all','dades']:
        taula = tools.classebuida()
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Dades Alumne'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 85
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
        
        taula.fileres = []

            #----nom alumne------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Nom'        
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}, {1}'.format( alumne.cognoms, alumne.nom )        
        filera.append(camp)
    
        taula.fileres.append( filera )
    
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
        camp.contingut = u'Data Naixement (Edat)'
        filera.append(camp)

        edatAlumne = alumne.edat()
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0} ({1} anys)'.format( alumne.data_neixement.strftime( '%d/%m/%Y' ) , edatAlumne)
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
        camp.contingut = u'{0} - {1}'.format( alumne.adreca , localitat_i_o_municipi )
        filera.append(camp)
    
        taula.fileres.append( filera )

            # ----email------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'e-mail'
        filera.append(camp)

        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format(alumne.correu)
        filera.append(camp)

        taula.fileres.append(filera)





        report.append(taula)

        #----Resonsable 1 (Principal)---------------------------------------------
        taula = tools.classebuida()

        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None

        taula.capceleres = []

        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Dades Responsable Preferent'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 85
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)



        taula.fileres = []

            # ----nom------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Nom'
        filera.append(camp)

        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format(alumne.rp1_nom) if alumne.primer_responsable == 0 else u'{0}'.format(alumne.rp2_nom)
        filera.append(camp)

        taula.fileres.append(filera)

            # ----Telèfons------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Telèfon/Mòbil'
        filera.append(camp)

        camp = tools.classebuida()
        camp.enllac = None
        telefons = ', '.join(
            filter(None, [alumne.rp1_telefon, alumne.rp1_mobil])) if alumne.primer_responsable == 0 else '/ '.join(
            filter(None, [alumne.rp2_telefon, alumne.rp2_mobil]))
        camp.contingut = u'{0}'.format(telefons)
        filera.append(camp)

        taula.fileres.append(filera)

            # ----E-mail------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'e-mail'
        filera.append(camp)

        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format(alumne.rp1_correu) if alumne.primer_responsable == 0 else u'{0}'.format(alumne.rp2_correu)
        filera.append(camp)

        taula.fileres.append(filera)

        report.append(taula)

        # ----Resonsable 2 ---------------------------------------------
        taula = tools.classebuida()

        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None

        taula.capceleres = []

        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Dades Responsable (altre)'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 85
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)

        taula.fileres = []

            # ----nom------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Nom'
        filera.append(camp)

        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format(alumne.rp2_nom) if alumne.primer_responsable == 0 else u'{0}'.format(alumne.rp1_nom)
        filera.append(camp)

        taula.fileres.append(filera)

            # ----Telèfons------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Telèfon/Mòbil'
        filera.append(camp)

        camp = tools.classebuida()
        camp.enllac = None
        telefons = ', '.join(
            filter(None, [alumne.rp2_telefon, alumne.rp2_mobil])) if alumne.primer_responsable == 0 else '/ '.join(
            filter(None, [alumne.rp1_telefon, alumne.rp1_mobil]))
        camp.contingut = u'{0}'.format(telefons)
        filera.append(camp)

        taula.fileres.append(filera)

            # ----E-mail------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'e-mail'
        filera.append(camp)

        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format(alumne.rp2_correu) if alumne.primer_responsable == 0 else u'{0}'.format(alumne.rp1_correu)
        filera.append(camp)

        taula.fileres.append(filera)

        report.append(taula)

        # ----Altres Telèfons ---------------------------------------------
        taula = tools.classebuida()

        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None

        taula.capceleres = []

        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Altres telèfons'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 85
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)

        taula.fileres = []

        # ----telèfons------------------------------------------
        filera = []

        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u''
        filera.append(camp)

        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format(alumne.altres_telefons)
        filera.append(camp)

        taula.fileres.append(filera)

        report.append(taula)

    #----Sancions  --------------------------------------------------------------------
    if detall in ['all', 'incidencies']:
        taula = tools.classebuida()
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Sancions'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 85
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
                
        taula.fileres = []
            
        for sancio in alumne.sancio_set.all().order_by( '-data_inici' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( sancio.data_inici.strftime( '%d/%m/%Y' ) )          
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( sancio.motiu )        
            filera.append(camp)
            #--
            taula.fileres.append( filera )
    
        report.append(taula)

    #----Expulsions --------------------------------------------------------------------
        taula = tools.classebuida()
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Expulsions'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 10
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
            
        capcelera = tools.classebuida()
        capcelera.amplade = 75
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
        
        taula.fileres = []
        
        for expulsio in alumne.expulsio_set.exclude( estat = 'ES' ).order_by( '-dia_expulsio', '-franja_expulsio' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1}'.format( expulsio.dia_expulsio.strftime( '%d/%m/%Y' ),
                                                u'''(per acumulació d'incidències)''' if expulsio.es_expulsio_per_acumulacio_incidencies else '')         
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}, {1}'.format( u'No tramitada.' if expulsio.estat != 'TR' else u'Sí tramitada', 
                                                u'Sí vigent.' if expulsio.es_vigent else u'No vigent',)         
            filera.append(camp)            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'Sr(a): {0} - {1}'.format(                                                
                                               expulsio.professor , 
                                               expulsio.motiu )        
            filera.append(camp)
            #--
            taula.fileres.append( filera )
            
        report.append(taula)
        
            
    #----incidències --------------------------------------------------------------------
        taula = tools.classebuida()
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Incidències'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 85
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
        
        taula.fileres = []
    
        for incidencia in alumne.incidencia_set.filter( tipus__es_informativa = False ).order_by( '-dia_incidencia', '-franja_incidencia' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1}'.format( incidencia.dia_incidencia.strftime( '%d/%m/%Y' ), 
                                                'Vigent' if incidencia.es_vigent else '')        
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'Sr(a): {0} - {1} - {2}'.format(incidencia.professional,
                                                        incidencia.tipus,
                                                        incidencia.descripcio_incidencia )        
            filera.append(camp)
    
            #--
            taula.fileres.append( filera )            
    
        report.append(taula)
        
        
        

    #----observacions --------------------------------------------------------------------
        taula = tools.classebuida()
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Observacions'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 85
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
        
        taula.fileres = []

        for incidencia in alumne.incidencia_set.filter( tipus__es_informativa = True ).order_by( '-dia_incidencia', '-franja_incidencia' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( incidencia.dia_incidencia.strftime( '%d/%m/%Y' ) )        
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'Sr(a): {0} - {1} - {2}'.format(incidencia.professional,
                                                        incidencia.tipus,
                                                        incidencia.descripcio_incidencia )       
            filera.append(camp)
    
            #--
            taula.fileres.append( filera )
        
        report.append(taula)

    #----Assistencia --------------------------------------------------------------------
    if detall in ['all', 'assistencia']:
        taula = tools.classebuida()
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        taula.fileres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Faltes i retards' 
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 85
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
        
        for control in alumne.controlassistencia_set.exclude( estat__codi_estat__in = ['P','O']
                                                              ).filter(  
                                                        estat__isnull=False                                                          
                                                            ).order_by( '-impartir__dia_impartir' , '-impartir__horari__hora'):
            
            filera = []
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = unicode(control.impartir.dia_impartir)        
            filera.append(camp)
    
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} a {1} ({2})'.format(
                                                 control.estat,
                                                 control.impartir.horari.assignatura,
                                                 control.impartir.horari.hora 
                                    )        
            filera.append(camp)
    
            #--
            taula.fileres.append( filera )
    
        report.append(taula)    

    #----Actuacions --------------------------------------------------------------------
    if detall in ['all', 'actuacions']:
        taula = tools.classebuida()
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        taula.fileres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Actuacions' 
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 85
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
        
        for actuacio in alumne.actuacio_set.order_by('-moment_actuacio' ):
            
            filera = []
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = unicode(actuacio.moment_actuacio)        
            filera.append(camp)
    
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = '/tutoria/editaActuacio/{0}'.format(actuacio.pk)
            camp.contingut = u'{0} fa actuació amb {1}: '.format( 
                                    actuacio.get_qui_fa_actuacio_display(),
                                    actuacio.get_amb_qui_es_actuacio_display(),
                                    actuacio.assumpte
                                    )        
            filera.append(camp)
    
            #--
            taula.fileres.append( filera )
    
        report.append(taula)    

    #----Seguiment tutorial--------------------------------------------------------------------
    if detall in ['all', 'seguiment']:
        taula = tools.classebuida()
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Següiment tutorial' 
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
        
        anys_seguiment_tutorial =  []
        txt_preguntes = []
        try:
                anys_seguiment_tutorial = SeguimentTutorialRespostes.objects.filter( 
                                                        seguiment_tutorial__alumne = alumne  
                                                                                   ).values_list('any_curs_academic', flat=True).distinct()
                txt_preguntes = SeguimentTutorialRespostes.objects.filter( 
                                                        seguiment_tutorial__alumne = alumne  
                                                                                   ).values_list('pregunta', flat=True).distinct()
        except:
                pass
    
        for un_any in anys_seguiment_tutorial:
            capcelera = tools.classebuida()
            capcelera.amplade = 85
            capcelera.contingut = u'{0}-{1}'.format( un_any, un_any+1 )
            taula.capceleres.append(capcelera)
        
        taula.fileres = []
    
        for txt_pregunta in txt_preguntes:
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = unicode(txt_pregunta)        
            filera.append(camp)            
            for un_any in anys_seguiment_tutorial:
                txt_resposta = ''
                try:
                        txt_resposta = SeguimentTutorialRespostes.objects.get( 
                                                                seguiment_tutorial__alumne = alumne,
                                                                pregunta = txt_pregunta,
                                                                any_curs_academic = un_any,
                                                                              ).resposta
                except:
                        pass                            
        
                #----------------------------------------------
                camp = tools.classebuida()
                camp.enllac = None
                camp.contingut = unicode(txt_resposta)        
                filera.append(camp)
    
            #--
            taula.fileres.append( filera )
    
        report.append(taula)    
        
        
    #----Històric --------------------------------------------------------------------
    if detall in ['all', 'historic']:
        taula = tools.classebuida()
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        taula.fileres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Històric' 
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)

        
        for h in ResumAnualAlumne.objects.filter(seguiment_tutorial__alumne = alumne  ).order_by( '-curs_any_inici' ):
            
            filera = []
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u"""\n-----------------------------{0}------------------------------------
            \n
            {1}
            """.format(  unicode(h.curs_any_inici) + '-' + unicode(h.curs_any_inici+1)  , h.text_resum)        
            filera.append(camp)
    
            #--
            taula.fileres.append( filera )
    
        report.append(taula)          

    #----Qualitatives--------------------------------------------------------------------
    if detall in ['all', 'qualitativa']:
        taula = tools.classebuida()
    
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
        capcelera.amplade = 85
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
        
        taula.fileres = []
    
        for resposta in alumne.respostaavaluacioqualitativa_set.all().order_by( 'qualitativa', 'assignatura' ) :
            
            filera = []
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1}'.format( resposta.qualitativa.data_tancar_avaluacio.strftime( '%d/%m/%Y' ) ,
                                                resposta.assignatura )        
            filera.append(camp)
    
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = unicode(resposta.item if resposta.item is not None else resposta.frase_oberta)
            filera.append(camp)
    
            #--
            taula.fileres.append( filera )
    
        report.append(taula)    

    #----------------
    
    return render(
                request,
                'report.html',
                    {'report': report,
                     'head': u'Informació alumne {0}'.format( head ) ,
                    },
                )




@login_required
@group_required(['direcció', 'professors'])        
def informeCompletFaltesIncidencies(request):
    
    formset = []
    totBe = True
    head = u"Tria alumnes i dates"
    
    OPCIONS = (
        ('s', u'Imprimir Informe'),
        ('n', u'No Imprimir'),
        ('r', u'Imprimir Recordatori')
    )

    grups_usuari = request.user.groups.values_list('name',flat=True)
    es_direccio = u'direcció' in grups_usuari

    # TODO: Fer que apareguin els alumnes dels tutors individualitzats

    if request.method == 'POST':
        
        form = dataForm( request.POST, prefix = 'data_ini', label = u'Data des de', help_text = u'Primer dia a incloure al llistat' )
        form.fields['data'].required = True
        formset.append( form )  
        dataInici = form.cleaned_data['data'] if form.is_valid() else None

        form = dataForm( request.POST, prefix = 'data_fi' , label = u'Data fins a', help_text = u'Darrer dia a incloure al llistat' )
        form.fields['data'].required = True
        formset.append( form )
        dataFi = form.cleaned_data['data'] if form.is_valid() else None
        
        alumnes_recordatori = []
        alumnes_informe = []
        grups = []
        if es_direccio:
            grups_a_mostrar = Grup.objects.filter( alumne__isnull = False ).distinct()
        else:
            grups_a_mostrar = [ t.grup for t in Tutor.objects.filter( professor = User2Professor(request.user) )]
        for grup in grups_a_mostrar:
            #http://www.ibm.com/developerworks/opensource/library/os-django-models/index.html?S_TACT=105AGX44&S_CMP=EDU
            formInclouGrup=ckbxForm(request.POST,
                                    prefix=str( grup.pk ),
                                    label = u'Incloure {0}'.format(grup),
                                    help_text = u"Marca aquesta casella per incloure al llistat els alumnes d'aquest grup",
                                    defecte = not es_direccio                
                                     )
            formInclouGrup.formSetDelimited = True
            formset.append( formInclouGrup )
            if formInclouGrup.is_valid():
                if formInclouGrup.cleaned_data['ckbx']:
                    grups.append(grup)            
            else:
                totBe = False
            
            for alumne in grup.alumne_set.all():

                user_associat = alumne.get_user_associat()
                
                fa_15_dies = datetime.now() - timedelta( days = 15 )
                connexio_darrers_dies = LoginUsuari.objects.filter( exitos = True, usuari__pk = user_associat.pk, moment__gte =  fa_15_dies ).exists()
                
                darrera_connexio = LoginUsuari.objects.filter( exitos = True, usuari__pk = user_associat.pk ).order_by('-moment')[:1]
                darrera_notificacio = alumne.relacio_familia_darrera_notificacio 
                te_correus_associats = bool( alumne.get_correus_relacio_familia() )

                opcio = 's'
                help_text = u"No tenim els correus d'aquest alumne"
                if alumne.esBaixa() or connexio_darrers_dies or ( darrera_connexio and darrera_notificacio and darrera_connexio[0].moment > darrera_notificacio): 
                    opcio = 'n'
                    help_text = u'Aquest alumne és baixa' if alumne.esBaixa() else u"Els tutors d'aquest alumne no tenen dades pendents de revisar"
                elif te_correus_associats:
                    opcio = 'r'
                    help_text = u'Aquest alumne té correus associats: {0}'.format( ', '.join(alumne.get_correus_relacio_familia()) )

                    
                formAlumne = choiceForm( request.POST,
                                         prefix=str( 'almn-{0}'.format( alumne.pk ) ),
                                         label = u'{0}'.format(alumne),
                                         opcions = OPCIONS,
                                         help_text = help_text ,
                                         initial = { 'opcio':opcio}  )
                formset.append( formAlumne )
                
                if formAlumne.is_valid():
                    if formAlumne.cleaned_data['opcio'] == 's':
                        alumnes_informe.append(alumne)
                    elif formAlumne.cleaned_data['opcio'] == 'r':
                        alumnes_recordatori.append(alumne)
                else:
                    totBe = False
                
        if totBe and dataInici and dataFi:            
            from . import reports
            return reports.reportFaltesIncidencies(dataInici, dataFi, alumnes_informe, alumnes_recordatori, grups, request)
    else:

        form = dataForm( request.POST, prefix = 'data_ini' , label = u'Data des de', help_text = u'Primer dia a incloure al llistat' )       
        formset.append( form )

        form = dataForm( request.POST, prefix = 'data_fi' , label = u'Data fins a', help_text = u'Darrer dia a incloure al llistat' )       
        formset.append( form )
        
        if es_direccio:
            grups_a_mostrar = Grup.objects.filter( alumne__isnull = False ).distinct()
        else:
            grups_a_mostrar = [ t.grup for t in Tutor.objects.filter( professor = User2Professor(request.user) )]
        for grup in grups_a_mostrar:
            #http://www.ibm.com/developerworks/opensource/library/os-django-models/index.html?S_TACT=105AGX44&S_CMP=EDU
            formInclouGrup=ckbxForm(
                                    prefix=str( grup.pk ),
                                    label = u'Incloure {0}'.format(grup),
                                    help_text = u"Marca aquesta casella per incloure al llistat els alumnes d'aquest grup",
                                    defecte = not es_direccio                          
                                     )
            formInclouGrup.formSetDelimited = True
            formset.append( formInclouGrup )
            for alumne in grup.alumne_set.all():
                
                user_associat = alumne.get_user_associat()

                fa_15_dies = datetime.now() - timedelta( days = 15 )
                connexio_darrers_dies = LoginUsuari.objects.filter( exitos = True, usuari__pk = user_associat.pk, moment__gte =  fa_15_dies ).exists()
                
                darrera_connexio = LoginUsuari.objects.filter( exitos = True, usuari__pk = user_associat.pk ).order_by('-moment')[:1]
                darrera_notificacio = alumne.relacio_familia_darrera_notificacio 
                te_correus_associats = bool( alumne.get_correus_relacio_familia() )

                opcio = 's'
                help_text = u"No tenim els correus d'aquest alumne"
                if alumne.esBaixa() or connexio_darrers_dies or ( darrera_connexio and darrera_notificacio and darrera_connexio[0].moment > darrera_notificacio):
                    opcio = 'n'
                    help_text = u'Aquest alumne és baixa' if alumne.esBaixa() else u"Els tutors d'aquest alumne no tenen dades pendents de revisar"
                elif te_correus_associats:
                    opcio = 'r'
                    help_text = u'Aquest alumne té correus associats: {0}'.format( ', '.join(alumne.get_correus_relacio_familia()) )

                    
                formAlumne = choiceForm( prefix=str( 'almn-{0}'.format( alumne.pk ) ),
                                         label = u'{0}'.format(alumne),
                                         opcions = OPCIONS,
                                         help_text = help_text ,
                                         initial = { 'opcio':opcio}  )
                formset.append( formAlumne )
        
    return render(
                  request,
                  "informeCompletFaltesIncidencies.html", 
                  {"formset": formset,
                   "head": head,
                   "formSetDelimited": True,
                   },
                  )



    
@login_required
@group_required(['professors'])
def calendariCursEscolarTutor(request):    

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials

    professor = User2Professor( user ) 
    
    reports = reportCalendariCursEscolarTutor( professor )

    return render(
                request,
                'calendariCursEscolarTutor.html', 
                {'reports': reports},
                )
    
    
    
@login_required
@group_required(['direcció'])        
def seguimentTutorialPreguntes(request):

    head=u'Preguntes de Seguiment Tutorial' 
    
    formset_f = modelformset_factory( SeguimentTutorialPreguntes , exclude=(), extra=10, can_delete=True )
    missatge = ''

    if request.method == 'POST':
        formset = formset_f(request.POST)
        if formset.is_valid():            
            formset.save()
            for form in formset.deleted_forms:
                instancia = form.save()
                instancia.delete()
            missatge = u'''Actualització realitzada.'''
            url_next = '/tutoria/seguimentTutorialPreguntes' 
            return HttpResponseRedirect( url_next )
        else:
            missatge = u'''Actualització no realitzada.'''
                                   
    else:
        formset = formset_f()
    
    for form in formset:
        form.fields['pregunta'].widget.attrs['size'] = 70
        form.fields['ajuda_pregunta'].widget.attrs['size'] = 70
        
    missatge =  u"""Atenció! Per mantenir un històric de respostes 
                    és important no modificar el redactat de les preguntes.
                    Un petit canvi en el redactat de la pregunta es cosidera
                    una pregunta diferent."""
        
    return render(
                request,
                'formset.html', 
                {'formset': formset, 
                 'head': head,
                 'missatge': missatge,
                 'formSetDelimited':True},
                )


@login_required
@group_required(['professors'])        
def seguimentTutorialFormulari(request):
    
    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    any_curs_academic = date.today().year - ( 1 if date.today().month <=8 else 0 )
    missatge = u"Atenció! Deseu la feina sovint (amb el botó enviar dades del peu de la pàgina). Recordeu que hi ha un temps de desconnexió per innactivitat."
    head = u""
    formset = []
    
    grups = [ t.grup for t in  Tutor.objects.filter( professor = professor )]
    grups.append( 'Altres' )
    for grup in grups:

        if grup == 'Altres':
            consulta_alumnes = Q( pk__in = [ti.alumne.pk for ti in professor.tutorindividualitzat_set.all() ]  )
        else:
            consulta_alumnes = Q( grup =  grup ) 
            
        for alumne in Alumne.objects.filter( consulta_alumnes ):
            infoform_added = False
            
            if not hasattr( alumne, 'seguimenttutorial' ):
                s, is_new = SeguimentTutorial.objects.get_or_create(
                        nom = alumne.nom,
                        cognoms =   alumne.cognoms,
                        data_neixement = alumne.data_neixement     )
                if is_new:
                    s.datadarreraacttualitzacio = datetime.now()                
                s.alumne = alumne
                s.save()
                alumne = Alumne.objects.get( pk = alumne.pk )
                
                
            for pregunta in SeguimentTutorialPreguntes.objects.all():

                if request.method == 'POST':  #---------------------------------------------------------
                    form = seguimentTutorialForm(
                                request.POST,
                                prefix=str( alumne.pk )+'_'+str(  pregunta.pk ), 
                                pregunta = pregunta,
                                resposta_anterior = None,
                                tutor = professor,
                                alumne = alumne )  
                    if form.is_valid():
                        r, is_new = SeguimentTutorialRespostes.objects.get_or_create(
                                                                                any_curs_academic = any_curs_academic,
                                                                                pregunta = pregunta.pregunta,
                                                                                seguiment_tutorial = alumne.seguimenttutorial,
                                                                           )
                        r.resposta = form.cleaned_data[ form.q_valida ]
                        r.save()                                    
                              
                
                
                else:                         #---------------------------------------------------------                    
                    try:
                        resposta_anterior = SeguimentTutorialRespostes.objects.get(
                                                    seguiment_tutorial = alumne.seguimenttutorial ,
                                                    any_curs_academic = any_curs_academic ,
                                                    pregunta = pregunta.pregunta
                                                            )
                    except ObjectDoesNotExist:
                        resposta_anterior = None
                    form = seguimentTutorialForm(
                                prefix=str( alumne.pk )+'_'+str(  pregunta.pk ), 
                                pregunta = pregunta,
                                resposta_anterior = resposta_anterior,
                                tutor = professor,
                                alumne = alumne  )
                
#                if pregunta.es_pregunta_oberta:
#                    del form.fields['pregunta_select']
#                else:
#                    del form.fields['pregunta_oberta']

                if not infoform_added:
                    infoform_added = True
                    form.infoForm = [ (u'{0} - Alumne'.format(alumne.grup), u'{0} curs {1}'.format( alumne, any_curs_academic )  ) ]
                    form.formSetDelimited = True
                    
                formset.append(form)

                    
    return render(
                request,
                'formset.html', 
                {'formset': formset, 
                 'head': head,
                 'missatge': missatge,
                 'formSetDelimited':True},
                )
    
    
@login_required
@group_required(['direcció'])        
def calculaResumAnual(request):
    calculaResumAnualProcess()
    
    
@login_required
def blanc( request ):
    return render(
                request,
                'blanc.html',
                    {},
                )

# Sortides

@login_required
@group_required(['professors'])        
def justificarSortida(request):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    
    sortides = ( Sortida
                   .objects
                   .exclude( estat = 'E' )
                   .filter( data_inici__gte = datetime.now() )
                   .filter( tutors_alumnes_convocats = professor )
                   .distinct()
                  )    
    
    table = Table2_Sortides( data=list( sortides ), origen="Tutoria" ) 
    table.order_by = '-calendari_desde' 
    
    RequestConfig(request, paginate={"paginator_class":DiggPaginator , "per_page": 10}).configure(table)
        
    return render(
                  request, 
                  'table2.html', 
                  {'table': table
                   }
                 )       

@login_required
@group_required(['professors'])        
def justificarSortidaAlumne(request, pk ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    instance = get_object_or_404( Sortida, pk = pk )
    instance.flag_clean_nomes_toco_alumnes = True
    potEntrar = ( professor in instance.tutors_alumnes_convocats.all() or request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists() )
    if not potEntrar:
        raise Http404 
    
    instance.credentials = credentials
   
    formIncidenciaF = modelform_factory(Sortida, fields=( 'alumnes_justificacio',  ) )

    if request.method == "POST":
        form = formIncidenciaF(request.POST, instance = instance)
        
        if form.is_valid(): 
            try:

                nous=set([ x.pk for x in form.cleaned_data['alumnes_justificacio'] ] )
                ante=set([ x.pk for x in instance.alumnes_justificacio.all() ] )
                #afegir
                for alumne in nous - ante:
                    instance.alumnes_justificacio.add( alumne )
                #treure
                for alumne in ante - nous:
                    instance.alumnes_justificacio.remove( alumne )
                    
                nexturl =  r'/tutoria/justificarSortida/'
                return HttpResponseRedirect( nexturl )
            except ValidationError as e:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  e.messages )


    else:

        form = formIncidenciaF( instance = instance  )
        
    #ids_alumnes_no_vindran = [ a.id for a in instance.alumnes_que_no_vindran.all()  ]
    ids_alumnes_que_venen = [ a.id for a in instance.alumnes_convocats.all()  ]
    form.fields['alumnes_justificacio'].queryset = AlumneGrupNom.objects.filter( id__in = ids_alumnes_que_venen ) 

    for f in form.fields:
        form.fields[f].widget.attrs['class'] = ' form-control ' + form.fields[f].widget.attrs.get('class',"") 

    #form.fields['alumnes_que_no_vindran'].widget.attrs['style'] = "height: 500px;"
        
    return render(
                request,
                'formSortidesAlumnesFallen.html',
                    {'form': form,
                     'head': 'Sortides' ,
                     'missatge': 'Sortides'
                    },
                )


    

        
