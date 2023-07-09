# This Python file uses the following encoding: utf-8

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect
from django.urls import reverse_lazy
from aula.utils.decorators import group_required
from aula.utils import tools
from . import sincronitza as s
from aula.apps.extPreinscripcio.forms import PreinscripcioForm
from aula.apps.extPreinscripcio.models import Nivell2Aula
from aula.apps.extPreinscripcio.sincronitza import actualitzaPreinscripcio
#---------------------------------------------------------------------------------

@login_required
@group_required(['direcció'])
def importaFitxer(request):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials   
    
    if request.method == 'POST':
        form = PreinscripcioForm(request.POST, request.FILES)
        if form.is_valid():
            f = form.cleaned_data.get('fitxer_Preinscripcio')
            resetPrevious = form.cleaned_data.get('resetPrevious')
            resultat = s.sincronitza(f, resetPrevious, user)
            if Nivell2Aula.objects.filter(nivellDjau__isnull=True):
                return HttpResponseRedirect(reverse_lazy('administracio__configuracio__preinscripcio'))
            return render(
                            request,
                            'resultat.html', 
                            {'head': u'Resultat importació preinscripció' ,
                             'msgs': resultat },
                         )
    else:
        form = PreinscripcioForm()
    return render(
                        request,
                        'form.html', 
                        {'form': form},
                 )

@login_required
@group_required(['direcció','administradors'])
def assignaNivells( request ):

    formset = []
    
    factoria = modelformset_factory( Nivell2Aula, extra = 0, exclude=(), can_delete=False )
    
    if request.method == "POST":
        #un formulari per cada grup
        totBe = True
        formset= factoria( request.POST )
        for f in formset:
            if f.is_valid():
                f.save()
            else:
                totBe = False
        
        actualitzaPreinscripcio()
        if totBe:
            return HttpResponseRedirect( '/' )
    
    else:
        formset= factoria( )
            
    return render(
                  request,
                  "formsetgrid.html", 
                  { "formset": formset,
                    "head": "Manteniment de nivells preinscripció",
                   },
                 )
