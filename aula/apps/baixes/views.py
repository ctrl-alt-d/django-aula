# This Python file uses the following encoding: utf-8
from django import forms
from django.contrib.auth.decorators import login_required
from django_select2.forms import ModelSelect2Widget
from aula.utils.decorators import group_required
from aula.utils import tools
from aula.utils.tools import unicode
from aula.apps.usuaris.models import User2Professor, Professor
from django.forms.models import modelform_factory, modelformset_factory
from aula.apps.baixes.models import Feina
from aula.apps.presencia.models import Impartir
from django.shortcuts import get_object_or_404, render
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from aula.apps.baixes.forms import complementFormulariTriaForm,\
    complementFormulariImpresioTriaForm
from datetime import date
from aula.utils.forms import dataForm
from aula.apps.baixes.rpt_carpeta import reportBaixaCarpeta

@login_required
@group_required(['professors'])
def feina( request, pk_imparticio  ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user ) 
    
    imparticio = get_object_or_404( Impartir, pk = pk_imparticio )
    
    try:
        feina = Feina.objects.get( impartir =  imparticio)  
    except Feina.DoesNotExist:    
        feina = Feina()
        feina.impartir = imparticio

    head = u"Feina per a {0}".format( imparticio )
    
    frmFact = modelform_factory( Feina, fields = ( 'feina_a_fer', 'comentaris_professor_guardia', )  )    
    
    if request.method == "POST":
        form = frmFact( request.POST, instance = feina )
        if form.is_valid():
            feina = form.save(commit =False )
            feina.professor_darrera_modificacio = professor
            feina.save()
            return HttpResponseRedirect( r'/presencia/passaLlista/{0}'.format( imparticio.pk ) )
    else:
        form = frmFact(  instance = feina )
        
    return render(
                request,
                'form.html', 
                {'form': form, 
                 'head': head},
                )



@login_required
@group_required(['direcció'])
def complementFormulariTria( request  ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    head = u"Selecciona professor i dia"
    
    if request.method == "POST":
        form = complementFormulariTriaForm( request.POST )
        if form.is_valid():
            professor = form.cleaned_data['professor']
            dia = form.cleaned_data['dia']
            return HttpResponseRedirect( r'/baixes/complementFormulariOmple/{0}/{1}'.format( professor.pk, dia.strftime('%d/%m/%Y') ) )
    else:
        form = complementFormulariTriaForm(  )

       
    return render(
                request,
                'form.html', 
                {'form': form, 
                 'head': head},
                )

@login_required
@group_required(['direcció'])
def complementFormulariOmple( request, pk_professor, dia, mes, year  ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user ) 
    
    data = date( int(year), int(mes), int(dia) )
    
    head = u"Feina professor absent {0} {1}".format( professor, data )
    
    imparticions = Impartir.objects.filter( dia_impartir = data, horari__professor__pk = pk_professor   )
    
    
    formsetFac = modelformset_factory(model = Feina, extra=0, can_delete=False,  
                                      fields=('professor_fa_guardia','feina_a_fer','comentaris_per_al_professor_guardia',),
                                      widgets = {
                                            'professor_fa_guardia': ModelSelect2Widget(
                                                queryset=Professor.objects.all(),
                                                search_fields=('last_name__icontains', 'first_name__icontains',),
                                                attrs={'style': "'width': '100%'"}
                                            )
                                      }
                                      )

    if request.method == "POST":
        formset = formsetFac( request.POST, queryset=Feina.objects.filter( impartir__in = imparticions ) )
        if formset.is_valid():
            formset.save()
            for form in formset:
                if (form.instance.professor_fa_guardia):
                    form.instance.impartir.professor_guardia = form.instance.professor_fa_guardia
                    form.instance.impartir.save()                    
            return HttpResponseRedirect( r'/' )
    else:
        #crear els que no existeixin:
        for i in imparticions:
            feina, _ = Feina.objects.get_or_create( impartir = i , 
                                         defaults = {'professor_darrera_modificacio':professor, } )
            if bool( i.professor_guardia ):
                feina.professor_fa_guardia = i.professor_guardia
                feina.save()
                
        formset = formsetFac( queryset=Feina.objects.filter( impartir__in = imparticions ) )

    for form in formset:
        instance = form.instance
        form.formSetDelimited = True
        guardies = Impartir.objects.filter( 
                                horari__assignatura__nom_assignatura = 'G',
                                horari__hora = instance.impartir.horari.hora,
                                dia_impartir = instance.impartir.dia_impartir
                                            ).distinct()
                                            
        form.infoForm = (
                           ( u'Hora', instance.impartir.horari.hora),
                           ( u'Assignatura', instance.impartir.horari.assignatura),
                           ( u'Grup', instance.impartir.horari.grup),
                           ( u'Aula', instance.impartir.horari.nom_aula),
                           ( u'Professors de Guardia', u', '.join( [ unicode(p) for p in Professor.objects.filter( horari__impartir__in = guardies ).distinct() ] )  )
                         )

    return render(
                request,
                'formset.html', 
                {'formset': formset, 
                 'head': head},
                )




@login_required
@group_required(['direcció'])
def complementFormulariImpresioTria( request  ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    head = u"Selecciona dia a imprimir"
    
    if request.method == "POST":
        form = complementFormulariImpresioTriaForm( request.POST )
        if form.is_valid():
            dia = form.cleaned_data['dia']
            professors = form.cleaned_data['professors']
            return reportBaixaCarpeta( request, dia, professors )
    else:
        form = complementFormulariImpresioTriaForm(  )
       
    return render(
                request,
                'form.html', 
                {'form': form, 
                 'head': head},
                )



    
        