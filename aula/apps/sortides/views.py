# This Python file uses the following encoding: utf-8
from aula.utils.widgets import DateTextImput, bootStrapButtonSelect
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
from aula.apps.sortides.table2_models import Table2_Sortides
from django_tables2.config import RequestConfig
from aula.utils.my_paginator import DiggPaginator
from django.shortcuts import render

@login_required
@group_required(['professors'])
def sortidesMevesList( request ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    sortides = ( Sortida
                   .objects
                   .filter( professor_que_proposa = professor )
                  )

    table = Table2_Sortides( list( sortides ) ) 
    table.order_by = 'total_expulsions_vigents' 
    
    RequestConfig(request, paginate={"klass":DiggPaginator , "per_page": 10}).configure(table)
        
    return render(
                  request, 
                  'table2.html', 
                  {'table': table,
                   }
                 )       


@login_required
@group_required(['professors'])
def sortidesGestioList( request ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    sortides = ( Sortida
                   .objects
                   .exclude( estat = 'E' )
                  )

    table = Table2_Sortides( list( sortides ) ) 
    table.order_by = 'total_expulsions_vigents' 
    
    RequestConfig(request, paginate={"klass":DiggPaginator , "per_page": 10}).configure(table)
        
    return render(
                  request, 
                  'table2.html', 
                  {'table': table,
                   }
                 )       
        
    
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
        instance.professor_que_proposa = professor
    
    instance.credentials = credentials
   
    formIncidenciaF = modelform_factory(Sortida )

    if request.method == "POST":
        form = formIncidenciaF(request.POST, instance = instance )
        
        if form.is_valid():            
            form.save()
            return HttpResponseRedirect( r'/sortides/sortidesList' )
            
    else:

        form = formIncidenciaF( instance = instance )
        
    form.fields['data_inici'].widget = DateTextImput()
    form.fields['data_fi'].widget = DateTextImput()
    #form.fields['estat'].widget = forms.RadioSelect( choices = form.fields['estat'].widget.choices )
    w= bootStrapButtonSelect( )
    w.choices = form.fields['estat'].widget.choices 
    form.fields['estat'].widget = w

    for f in form.fields:
        form.fields[f].widget.attrs['class'] = ' form-control' + form.fields[f].widget.attrs.get('class',"") 
        
    return render_to_response(
                'form.html',
                    {'form': form,
                     'head': 'Sortides' ,
                     'missatge': 'Sortides'
                    },
                    context_instance=RequestContext(request))    
    
    
        
