# This Python file uses the following encoding: utf-8

#templates
from django.template import RequestContext

#workflow
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

import sincronitzaKronowin as s

from aula.apps.extKronowin.forms import sincronitzaKronowinForm, Kronowin2DjangoAulaFranjaForm, Kronowin2DjangoAulaGrupForm
from aula.apps.extKronowin.models import Franja2Aula, Grup2Aula
from aula.apps.usuaris.models import Accio

from aula.utils import tools
#---------------------------------------------------------------------------------

@login_required
@group_required(['direcció','administradors'])
def assignaFranges( request ):
        
    #prefixes:
    #https://docs.djangoproject.com/en/dev/ref/forms/api/#prefixes-for-forms    
    formset = []
    if request.method == "POST":
        #un formulari per cada franja
        totBe = True
        for grup in Franja2Aula.objects.all():
            form=Kronowin2DjangoAulaFranjaForm(
                                    request.POST,
                                    prefix=str( grup.pk ),
                                    instance=grup )
            formset.append( form )
            if form.is_valid():
                form.save()
            else:
                totBe = False
                
        if totBe:
            return HttpResponseRedirect( '/' )

                
    else:
        for grup in Franja2Aula.objects.all():
            form=Kronowin2DjangoAulaFranjaForm(
                                    prefix=str( grup.pk ),
                                    instance=grup )            
            formset.append( form )
            
    return render_to_response(
                  "formsetgrid.html", 
                  { "formset": formset,
                    "head": "Manteniment de grups Krownowin",
                   },
                  context_instance=RequestContext(request))

#---------------------------------------------------------------------------------

@login_required
@group_required(['direcció','administradors'])
def assignaGrups( request ):
        
    #prefixes:
    #https://docs.djangoproject.com/en/dev/ref/forms/api/#prefixes-for-forms    
    formset = []
    if request.method == "POST":
        #un formulari per cada grup
        totBe = True
        for grup in Grup2Aula.objects.all():
            form=Kronowin2DjangoAulaGrupForm(
                                    request.POST,
                                    prefix=str( grup.pk ),
                                    instance=grup )
            formset.append( form )
            if form.is_valid():
                form.save()
            else:
                totBe = False
                
        if totBe:
            return HttpResponseRedirect( '/' )

                
    else:
        for grup in Grup2Aula.objects.all():
            form=Kronowin2DjangoAulaGrupForm(
                                    prefix=str( grup.pk ),
                                    instance=grup )            
            formset.append( form )
            
    return render_to_response(
                  "formsetgrid.html", 
                  { "formset": formset,
                    "head": "Manteniment de grups Krownowin",
                   },
                  context_instance=RequestContext(request))

#---------------------------------------------------------------------------------
@login_required
@group_required(['direcció'])
def sincronitzaKronowin(request):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials   
    
    if request.method == 'POST':
        form = sincronitzaKronowinForm(request.POST, request.FILES)
        if form.is_valid():
            resultat=s.sincronitza(request.FILES['fitxer_kronowin'], request.user)

            #LOGGING
            Accio.objects.create( 
                    tipus = 'SK',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Sincronitzar horaris des d'arxiu Kronowin."""
                )
            
        return render_to_response(
                        'resultat.html', 
                        {'head': u'Resultat sincronització Kronowin' ,
                         'msgs': resultat },
                        context_instance=RequestContext(request))    
    else:
        form = sincronitzaKronowinForm()
    return render_to_response(
                        'sincronitzaKronowin.html', 
                        {'form': form},
                        context_instance=RequestContext(request))
        

    

