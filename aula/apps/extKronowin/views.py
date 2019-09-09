# This Python file uses the following encoding: utf-8

#templates

#workflow
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

from . import sincronitzaKronowin as s

from aula.apps.extKronowin.forms import sincronitzaKronowinForm, Kronowin2DjangoAulaFranjaForm, Kronowin2DjangoAulaGrupForm,\
    creaNivellCursGrupDesDeKronowinForm
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
            
    return render(
                  request,
                  "formsetgrid.html", 
                  { "formset": formset,
                    "head": "Manteniment de grups Krownowin",
                   },
                 )

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
            
    return render(
                  request,
                  "formsetgrid.html", 
                  { "formset": formset,
                    "head": "Manteniment de grups Krownowin",
                   },
                 )

#---------------------------------------------------------------------------------
@login_required
@group_required(['direcció'])
def sincronitzaKronowin(request):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials   
    
    if request.method == 'POST':
        form = sincronitzaKronowinForm(request.POST, request.FILES)
        if form.is_valid():

            f = request.FILES['fitxer_kronowin']
            path = default_storage.save('tmp/kronowin.txt', ContentFile(f.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            with open(tmp_file, 'r', encoding="utf-8") as f1:
                resultat = s.sincronitza(f1, request.user)
            default_storage.delete(path)

            #LOGGING
            Accio.objects.create( 
                    tipus = 'SK',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Sincronitzar horaris des d'arxiu Kronowin."""
                )
            
        return render(
                        request,
                        'resultat.html', 
                        {'head': u'Resultat sincronització Kronowin' ,
                         'msgs': resultat },
                     )
    else:
        form = sincronitzaKronowinForm()
    return render(
                        request,
                        'sincronitzaKronowin.html', 
                        {'form': form},
                 )
        

    
#---------------------------------------------------------------------------------
@login_required
@group_required(['direcció'])
def creaNivellCursGrupDesDeKronowin(request):
    #credentials = tools.getImpersonateUser(request) 
    #(user, l4) = credentials   
    
    if request.method == 'POST':
        form = creaNivellCursGrupDesDeKronowinForm(request.POST, request.FILES)
        if form.is_valid():

            f = request.FILES['fitxer_kronowin']
            path = default_storage.save('tmp/kronowin.txt', ContentFile(f.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            with open(tmp_file, 'r', encoding="utf-8") as f1:
                resultat = s.creaNivellCursGrupDesDeKronowin(f1,
                                                        form.cleaned_data["dia_inici_curs"],
                                                        form.cleaned_data["dia_fi_curs"])
            default_storage.delete(path)


        return render(
                        request,
                        'resultat.html', 
                        {'head': u'Resultat sincronització Kronowin' ,
                         'msgs': resultat },
                     )
    else:
        form = creaNivellCursGrupDesDeKronowinForm()
    return render(
                        request,
                        'sincronitzaKronowin.html', 
                        {'form': form},
                 )
        
