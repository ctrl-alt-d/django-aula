
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
from django.core.urlresolvers import reverse
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
    q_alumnes_tutorats = Q( pk__in = [ti.alumne.pk 
                                    for ti in professor.tutorindividualitzat_set.all() ]  )
    alumnes = list( Alumne
                   .objects
                   .filter( q_grups_tutorats | q_alumnes_tutorats )
                   .order_by('grup', 'cognoms', 'nom' ) )
    
    #busco el dilluns i el divendres
    dia_de_la_setmana = data.weekday()
    delta = timedelta( days = (-1 * dia_de_la_setmana ) )
    dilluns = data + delta
    dies = [ dilluns + timedelta( days = delta ) for delta in  [0,1,2,3,4] ]
    q_controls = ( Q( impartir__dia_impartir__in = dies ) &
                  Q( alumne__in = alumnes ) )
    controls = list ( ControlAssistencia
                           .objects
                           .select_related(
                                'alumne',
                                'estat', 
                                'estat_backup',
                                'impartir__horari',
                                'impartir__horari__assignatura',
                                'impartir__horari__hora',
                                'professor',
                                'professor_backup',
                             )
                           .filter( q_controls ) )
        
    #marc horari per cada dia
    dades = tools.classebuida()
    dades.alumnes =  alumnes
    dades.c = []    #controls
    
    dades.dia_hores = tools.diccionari()
    dades.marc_horari = {}
    for delta in [0,1,2,3,4]:
        dia = dilluns + timedelta( days = delta )

        diferents_hores = { control.impartir.horari.hora 
                            for control in controls
                            if control.impartir.dia_impartir == dia  }
        if (diferents_hores):
            diferents_hores_ordenat = sorted( list(diferents_hores) , key = lambda x: x.hora_inici )
            dades.dia_hores[dia] = tools.llista( diferents_hores_ordenat )
            dades.marc_horari[dia] = { 'desde':diferents_hores_ordenat[0],'finsa':diferents_hores_ordenat[-1]}        
        
    dades.quadre = tools.diccionari()
    
    for alumne in dades.alumnes:

        dades.quadre[alumne] = []

        for dia, hores in dades.dia_hores.itemsEnOrdre():
            
            hora_inici = dades.marc_horari[dia]['desde']

            controls_alumne = [ control for control in controls
                           if control.impartir.dia_impartir == dia  and
                              control.alumne == alumne ]

            for hora in hores:
     
                cella = tools.classebuida()
                cella.txt = ''
                hiHaControls = len( [ c for c in controls_alumne if c.impartir.horari.hora == hora] )>0
                haPassatLlista = hiHaControls and len( [ c for c in controls_alumne 
                                                         if c.estat is not None and c.impartir.horari.hora == hora] )>0
                
                cella.c = [ c for c in controls_alumne if c.impartir.horari.hora == hora]
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
                
                dades.quadre[alumne].append( cella )
                
    return dades    
    