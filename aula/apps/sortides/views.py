# This Python file uses the following encoding: utf-8
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

#helpers
from aula.utils import tools
from aula.apps.usuaris.models import User2Professor
from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext
from aula.apps.sortides.rpt_sortidesList import sortidesListRpt
from aula.apps.sortides.models import Sortida
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django import forms

@login_required
@group_required(['professors'])
def sortidesList( request ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    report = sortidesListRpt(  )
    
    menuCTX = [  ( r'/sortides/sortidaEdit', 'Nova Sortida',), ]
        
    return render_to_response(
                'report.html',
                    {'report': report,
                     'head': 'Totes les sortides' ,
                     'menuCTX': menuCTX,
                    },
                    context_instance=RequestContext(request))       
    
    
    
@login_required
@group_required(['professors'])
def sortidaEdit( request, pk = None ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    if bool( pk ):
        instance = get_object_or_404( Sortida, pk = pk )
    else:
        instance = Sortida()
    
    instance.credentials = credentials
   
    formIncidenciaF = modelform_factory(Sortida )

    if request.method == "POST":
        form = formIncidenciaF(request.POST, instance = instance )
        
        if form.is_valid():            
            form.save()
            return HttpResponseRedirect( r'/sortides/sortidesList' )
            
    else:

        form = formIncidenciaF( instance = instance )
        
    form.fields['data_inici'].widget = forms.DateInput(attrs={'class':'datepicker'} )
    form.fields['data_fi'].widget = forms.DateInput(attrs={'class':'datepicker'} )
    form.fields['estat'].widget = forms.RadioSelect( choices = form.fields['estat'].widget.choices )

        
    return render_to_response(
                'form.html',
                    {'form': form,
                     'head': 'Sortides' ,
                     'missatge': 'Sortides'
                    },
                    context_instance=RequestContext(request))    
    
    
        
