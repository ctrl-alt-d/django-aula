# This Python file uses the following encoding: utf-8

from aula.apps.todo.models import ToDo

from aula.utils import tools
from django import forms

#auth
from django.contrib.auth.decorators import login_required
from django.forms.formsets import formset_factory
from django.forms.models import modelform_factory
from django.shortcuts import render
from django.template.context import RequestContext
from django.http import HttpResponseRedirect
from aula.utils.decorators import group_required

@login_required
@group_required(['professors','professional','consergeria'])
def list( request ):

    (user, l4) = tools.getImpersonateUser(request)   
    
    report = []
 
    taula = tools.classebuida()
    taula.titol = tools.classebuida()
    taula.titol.contingut = ""
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = u'{0}'.format( u'Tasques importants pendents' )
    taula.capceleres.append(capcelera)
    
    capcelera = tools.classebuida()
    capcelera.amplade = 25
    capcelera.contingut = u'Tasca'
    taula.capceleres.append(capcelera)
    
    capcelera = tools.classebuida()
    capcelera.amplade = 50
    capcelera.contingut = u'Contingut'
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 5
    capcelera.contingut = u'Esborrar'
    taula.capceleres.append(capcelera)
    
    
    taula.fileres = []        
    
    for todo in ToDo.objects.filter( propietari = request.user, estat = 'P', prioritat = 'V' ):
        filera = []

        camp = tools.classebuida()
        camp.contingut = u'{0}'.format( todo.data )
        filera.append(camp)

        camp = tools.classebuida()
        camp.contingut = u'{0}'.format( todo.tasca )
        camp.enllac = todo.enllac
        filera.append(camp)

        camp = tools.classebuida()
        camp.contingut = u'{0}'.format( todo.informacio_adicional )
        filera.append(camp)

        camp = tools.classebuida()
        camp.contingut = u'[ X ]'
        camp.enllac = '/todo/esborra/{0}'.format( todo.pk )
        filera.append(camp)

        taula.fileres.append( filera )

    if taula.fileres: report.append(taula) #-----------------------------------------------------
        
 
    taula = tools.classebuida()
    taula.titol = tools.classebuida()
    taula.titol.contingut = ""
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = u'{0}'.format( u'Tasques Pendents' )
    taula.capceleres.append(capcelera)
    
    capcelera = tools.classebuida()
    capcelera.amplade = 25
    capcelera.contingut = u'Tasca'
    taula.capceleres.append(capcelera)
    
    capcelera = tools.classebuida()
    capcelera.amplade = 50
    capcelera.contingut = u'Contingut'
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 5
    capcelera.contingut = u'Esborrar'
    taula.capceleres.append(capcelera)
        
    taula.fileres = []        
    
    for todo in ToDo.objects.filter( propietari = request.user, estat = 'P' ).exclude( prioritat = 'V' ):
        filera = []

        camp = tools.classebuida()
        camp.contingut = u'{0}'.format( todo.data )
        filera.append(camp)

        camp = tools.classebuida()
        camp.contingut = u'{0}'.format( todo.tasca )
        camp.enllac = todo.enllac
        filera.append(camp)

        camp = tools.classebuida()
        camp.contingut = u'{0}'.format( todo.informacio_adicional )
        filera.append(camp)

        camp = tools.classebuida()
        camp.contingut = u'[ X ]'
        camp.enllac = '/todo/esborra/{0}'.format( todo.pk )
        filera.append(camp)

        taula.fileres.append( filera )

    report.append(taula)     #-----------------------------------------------------

        
 
    taula = tools.classebuida()
    taula.titol = tools.classebuida()
    taula.titol.contingut = ""
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = u'{0}'.format( u'Tasques Realitzades' )
    taula.capceleres.append(capcelera)
    
    capcelera = tools.classebuida()
    capcelera.amplade = 25
    capcelera.contingut = u'Tasca'
    taula.capceleres.append(capcelera)
    
    capcelera = tools.classebuida()
    capcelera.amplade = 50
    capcelera.contingut = u'Contingut'
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 5
    capcelera.contingut = u'Esborrar'
    taula.capceleres.append(capcelera)
        
    taula.fileres = []        
    
    for todo in ToDo.objects.filter( propietari = request.user, estat = 'R' ):
        filera = []

        camp = tools.classebuida()
        camp.contingut = u'{0}'.format( todo.data )
        filera.append(camp)

        camp = tools.classebuida()
        camp.contingut = u'{0}'.format( todo.tasca )
        camp.enllac = todo.enllac
        filera.append(camp)

        camp = tools.classebuida()
        camp.contingut = u'{0}'.format( todo.informacio_adicional )
        filera.append(camp)

        camp = tools.classebuida()
        camp.contingut = u'[ X ]'
        camp.enllac = '/todo/esborra/{0}'.format( todo.pk )
        filera.append(camp)

        taula.fileres.append( filera )

    if taula.fileres: report.append(taula) #-----------------------------------------------------
    
    return render(
                request,
                'reportToDo.html',
                    {'report': report,
                     'head': u'Tasques' ,
                    },
                )
        
@login_required
@group_required(['professors','professional','consergeria'])
def edita( request, pk = None ):

    (user, l4) = tools.getImpersonateUser(request)
        
    todo = ToDo.objects.get(pk = pk) if pk and user.todo_set.filter( pk = pk ).exists() else None
    
    if request.method == 'POST':
        formF = modelform_factory( ToDo, fields = ( 'data', 'tasca' , 'informacio_adicional', 'estat' , 'prioritat', 'enllac' ))
        form = formF(  request.POST  )
        if not form.instance.pk: 
            form.instance.propietari = user
        if form.is_valid(  ):
            form.save()
            return HttpResponseRedirect( '/todo/list/' )

    else:
        form = modelform_factory( ToDo, fields = ( 'data','tasca' , 'informacio_adicional', 'estat' , 'prioritat', 'enllac' ))
        
        if todo: form = form( instance = todo )
        
        form.base_fields['data'].widget = forms.DateTimeInput(attrs={'class':'DateTimeAnyTime'} )
           
        #form = formF(  )
        
    return render(
              request,
              "form.html", 
              {"form": form,
               "head": 'Edita tasca',
               },
              )
    
@login_required
@group_required(['professors','professional','consergeria'])
def esborra( request, pk = None ):

    (user, l4) = tools.getImpersonateUser(request)   
    
    if user.todo_set.filter( pk = pk).exists():
        ToDo.objects.get(pk = pk).delete()
    return HttpResponseRedirect( '/todo/list/' )
    
