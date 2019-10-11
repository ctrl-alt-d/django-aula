# This Python file uses the following encoding: utf-8

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

from . import sincronitzaUntis as s

from aula.apps.extUntis.forms import sincronitzaUntisForm
from aula.apps.usuaris.models import Accio

from aula.utils import tools
#---------------------------------------------------------------------------------

@login_required
@group_required(['direcció'])
def sincronitzaUntis(request):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials   
    
    if request.method == 'POST':
        form = sincronitzaUntisForm(request.POST, request.FILES)
        if form.is_valid():

            f = request.FILES['fitxer_Untis']
            resultat = s.sincronitza(f.read(), request.user)
            #LOGGING
            Accio.objects.create( 
                    tipus = 'SU',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Sincronitzar horaris des d'arxiu Untis."""
                )
            
        return render(
                        request,
                        'resultat.html', 
                        {'head': u'Resultat sincronització Untis' ,
                         'msgs': resultat },
                     )
    else:
        form = sincronitzaUntisForm()
    return render(
                        request,
                        'sincronitzaUntis.html', 
                        {'form': form},
                 )
