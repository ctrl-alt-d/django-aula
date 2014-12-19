# This Python file uses the following encoding: utf-8
from aula.utils.widgets import DateTextImput, bootStrapButtonSelect,\
    DateTimeTextImput
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
from aula.apps.sortides.table2_models import Table2_Sortides,Table2_SortidesGestio
from django_tables2.config import RequestConfig
from aula.utils.my_paginator import DiggPaginator
from django.shortcuts import render

from icalendar import Calendar, Event
from icalendar import vCalAddress, vText
from django.http.response import HttpResponse, Http404
from django.utils.datetime_safe import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from aula.apps.alumnes.models import Alumne, AlumneGrupNom
from django.contrib import messages
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS

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
    table.order_by = '-calendari_desde' 
    
    RequestConfig(request, paginate={"klass":DiggPaginator , "per_page": 10}).configure(table)
        
    return render(
                  request, 
                  'lesMevesSortides.html', 
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

    table = Table2_SortidesGestio( list( sortides ) ) 
    table.order_by = '-calendari_desde' 
    
    RequestConfig(request, paginate={"klass":DiggPaginator , "per_page": 10}).configure(table)
        
    url = r"{0}{1}".format( settings.URL_DJANGO_AULA, reverse( 'sortides__sortides__ical' ) )    
        
    return render(
                  request, 
                  'gestioDeSortides.html', 
                  {'table': table,
                   'url': url,
                   }
                 )       
        
    
@login_required
@group_required(['professors'])   #TODO: i grup sortides
def sortidaEdit( request, pk = None, esGestio=False ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    if bool( pk ):
        instance = get_object_or_404( Sortida, pk = pk )
        potEntrar = ( instance.professor_que_proposa == professor or request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists() )
        if not potEntrar:
            raise Http404
    else:
        instance = Sortida()
        instance.professor_que_proposa = professor
    
    instance.credentials = credentials
   
    formIncidenciaF = modelform_factory(Sortida, exclude=( 'alumnes_convocats', 'alumnes_que_no_vindran', ) )

    if request.method == "POST":
        form = formIncidenciaF(request.POST, instance = instance)
        
        if form.is_valid(): 
            form.save()
            nexturl =  r'/sortides/sortidesGestio' if esGestio else r'/sortides/sortidesMeves'
            return HttpResponseRedirect( nexturl )
            
    else:

        form = formIncidenciaF( instance = instance  )
        
    form.fields['data_inici'].widget = DateTextImput()
    form.fields['data_fi'].widget = DateTextImput()
    #form.fields['estat'].widget = forms.RadioSelect( choices = form.fields['estat'].widget.choices )
    widgetBootStrapButtonSelect= bootStrapButtonSelect( )
    widgetBootStrapButtonSelect.choices = form.fields['estat'].widget.choices 
    form.fields['estat'].widget = widgetBootStrapButtonSelect    
    
    form.fields["calendari_public"].widget.attrs['style'] = u"width: 3%"
    for f in form.fields:
        form.fields[f].widget.attrs['class'] = ' form-control' + form.fields[f].widget.attrs.get('class',"") 

    form.fields['calendari_desde'].widget = DateTimeTextImput()
    form.fields['calendari_finsa'].widget = DateTimeTextImput()
        
    return render_to_response(
                'formSortida.html',
                    {'form': form,
                     'head': 'Sortides' ,
                     'missatge': 'Sortides'
                    },
                    context_instance=RequestContext(request))    

#-------------------------------------------------------------------
    
@login_required
@group_required(['professors'])   
def alumnesConvocats( request, pk , esGestio=False ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    instance = get_object_or_404( Sortida, pk = pk )
    potEntrar = ( instance.professor_que_proposa == professor or request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists() )
    if not potEntrar:
        raise Http404
    
    instance.credentials = credentials
    instance.flag_clean_nomes_toco_alumnes = True
    formIncidenciaF = modelform_factory(Sortida, fields=( 'alumnes_convocats',  ) )

    if request.method == "POST":
        form = formIncidenciaF(request.POST, instance = instance)
        
        if form.is_valid():
            try: 
                form.save()
                nexturl =  r'/sortides/sortidesGestio' if esGestio else r'/sortides/sortidesMeves'
                return HttpResponseRedirect( nexturl )
            except ValidationError, e:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  e.messages )
            
    else:

        form = formIncidenciaF( instance = instance  )
        
    form.fields['alumnes_convocats'].queryset = AlumneGrupNom.objects.all() 

    for f in form.fields:
        form.fields[f].widget.attrs['class'] = ' form-control' + form.fields[f].widget.attrs.get('class',"") 

    form.fields['alumnes_convocats'].widget.attrs['style'] = "height: 500px;"
        
    return render_to_response(
                'form.html',
                    {'form': form,
                     'head': 'Sortides' ,
                     'missatge': 'Sortides'
                    },
                    context_instance=RequestContext(request))    




#-------------------------------------------------------------------
    
@login_required
@group_required(['professors'])   
def alumnesFallen( request, pk , esGestio=False ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    instance = get_object_or_404( Sortida, pk = pk )
    instance.flag_clean_nomes_toco_alumnes = True
    potEntrar = ( instance.professor_que_proposa == professor or request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists() )
    if not potEntrar:
        raise Http404
    
    instance.credentials = credentials
   
    formIncidenciaF = modelform_factory(Sortida, fields=( 'alumnes_que_no_vindran',  ) )

    if request.method == "POST":
        form = formIncidenciaF(request.POST, instance = instance)
        
        if form.is_valid(): 
            try:
                form.save()
                nexturl =  r'/sortides/sortidesGestio' if esGestio else r'/sortides/sortidesMeves'
                return HttpResponseRedirect( nexturl )
            except ValidationError, e:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  e.messages )


    else:

        form = formIncidenciaF( instance = instance  )
        
    ids_alumnes_que_venen = [ a.id for a in instance.alumnes_convocats.all()  ]
    form.fields['alumnes_que_no_vindran'].queryset = AlumneGrupNom.objects.filter( id__in = ids_alumnes_que_venen ) 

    for f in form.fields:
        form.fields[f].widget.attrs['class'] = ' form-control' + form.fields[f].widget.attrs.get('class',"") 

    form.fields['alumnes_que_no_vindran'].widget.attrs['style'] = "height: 500px;"
        
    return render_to_response(
                'form.html',
                    {'form': form,
                     'head': 'Sortides' ,
                     'missatge': 'Sortides'
                    },
                    context_instance=RequestContext(request))    

#-------------------------------------------------------------------
    
@login_required
@group_required(['professors'])   #TODO: i grup sortides
def esborrar( request, pk , esGestio=False ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    instance = get_object_or_404( Sortida, pk = pk )
    
    mortalPotEntrar = (  instance.professor_que_proposa == professor  and  not instance.estat in [ 'R', 'G' ] )
    direccio = ( request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists() )
    
    potEntrar = mortalPotEntrar or direccio
    if not potEntrar:
        messages.warning(request, u"No pots esborrar aquesta sortida." )
        return HttpResponseRedirect( request.META.get('HTTP_REFERER') )
    
    instance.credentials = credentials
   
    try:
        instance.delete()
    except:
        messages.warning(request, u"Error esborrant la sortida." )
    
    nexturl =  r'/sortides/sortidesGestio' if esGestio else r'/sortides/sortidesMeves'
    return HttpResponseRedirect( nexturl )

#-------------------------------------------------------------------
    
def sortidaiCal( request):

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    cal = Calendar()
    cal.add('method','PUBLISH' ) # IE/Outlook needs this

    for instance in Sortida.objects.filter( calendari_desde__isnull = False ).all():
        event = Event()
        
#         d=instance.data_inici
#         t=instance.franja_inici.hora_inici
#         dtstart = datetime( d.year, d.month, d.day, t.hour, t.minute  )
#         d=instance.data_fi
#         t=instance.franja_fi.hora_fi
#         dtend = datetime( d.year, d.month, d.day, t.hour, t.minute  )
        
        event.add('dtstart',instance.calendari_desde)
        event.add('dtend' ,instance.calendari_finsa)
        event.add('summary',instance.titol_de_la_sortida)
        event.add('uid', 'djau-ical-{0}'.format( instance.id ) )
        event['location'] = vText( instance.ciutat )
        
        cal.add_component(event)

#     response = HttpResponse( cal.to_ical() , mimetype='text/calendar')
#     response['Filename'] = 'shifts.ics'  # IE needs this
#     response['Content-Disposition'] = 'attachment; filename=shifts.ics'
#     return response

    return HttpResponse( cal.to_ical() )
    
    