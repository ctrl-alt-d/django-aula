
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
from aula.utils.tools import unicode
from aula.apps.presencia.models import  ControlAssistencia, EstatControlAssistencia,\
    Impartir
from datetime import  date, datetime
from datetime import timedelta
from aula.apps.tutoria.models import Actuacio, Tutor, SeguimentTutorialPreguntes,\
    SeguimentTutorial, SeguimentTutorialRespostes, ResumAnualAlumne,\
    CartaAbsentisme
from aula.apps.alumnes.models import Alumne, Grup, AlumneGrupNom
from django.forms.models import modelform_factory, modelformset_factory
from django import forms
from django.db.models import Min, Max, Q

#exceptions
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS,\
    ObjectDoesNotExist
from django.http import Http404
from aula.apps.horaris.models import FranjaHoraria, Horari
from aula.apps.incidencies.models import Incidencia, Expulsio
from aula.utils.tools import llista
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
@group_required(['professors'])
def justificadorMKTable(request, year, month, day ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
    professor = User2Professor(user)
    
    data = date( year = int(year), month= int(month), day = int(day) )
    grups = Grup.objects.filter( tutor__professor = professor )

    q_grups_tutorats = Q( grup__in =  [ t.grup for t in professor.tutor_set.all() ] )
    q_alumnes_tutorats = Q( pk__in = [ti.alumne.pk for ti in professor.tutorindividualitzat_set.all() ]  )
    alumnes = Alumne.objects.filter( q_grups_tutorats | q_alumnes_tutorats )
    
    #busco el dilluns i el divendres
    dia_de_la_setmana = data.weekday()
     
    delta = timedelta( days = (-1 * dia_de_la_setmana ) )
    dilluns = data + delta
        
    #marc horari per cada dia
    dades = tools.classebuida()
    dades.alumnes = alumnes.order_by('grup', 'cognoms', 'nom' )
    dades.c = []    #controls
    
    dades.dia_hores = tools.diccionari()
    dades.marc_horari = {}
    for delta in [0,1,2,3,4]:
        dia = dilluns + timedelta( days = delta )
        q_grups = Q(grup__in = grups )
        q_alumnes = Q(grup__alumne__in = alumnes )
        q_impartir = Q( impartir__controlassistencia__alumne__in = alumnes )
        q_dies = Q(impartir__dia_impartir = dia)
        
        #forquilla = Horari.objects.filter( ( q_grups | q_alumnes ) & q_dies                                               
        forquilla = Horari.objects.filter( q_impartir & q_dies                                               
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
            
            hora_inici = FranjaHoraria.objects.get( hora_inici = dades.marc_horari[dia]['desde'] )
            hora_fi    = FranjaHoraria.objects.get( hora_inici = dades.marc_horari[dia]['finsa'] )

            q_controls = Q( impartir__dia_impartir = dia ) & \
                         Q( impartir__horari__hora__gte = hora_inici) & \
                         Q( impartir__horari__hora__lte = hora_fi) & \
                         Q( alumne = alumne )

            controls = [ c for c in ControlAssistencia.objects.select_related(
                                'estat', 'impartir__horari__assignatura','professor','estat_backup','professor_backup'
                                ).filter( q_controls ) ]

            for hora in hores:
     
                cella = tools.classebuida()
                cella.txt = ''
                hiHaControls = len( [ c for c in controls if c.impartir.horari.hora == hora] )>0
                haPassatLlista = hiHaControls and len( [ c for c in controls if c.estat is not None and c.impartir.horari.hora == hora] )>0
                
                cella.c = [ c for c in controls if c.impartir.horari.hora == hora]
                for item in cella.c:
                    item.professor2show = item.professor or ( item.impartir.horari.professor if item.impartir.horari else ' ' ) 
                    item.estat2show= item.estat or " "
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
    