# This Python file uses the following encoding: utf-8

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

from . import sincronitza as s

from aula.apps.extPreinscripcio.forms import PreinscripcioForm

from aula.utils import tools
#---------------------------------------------------------------------------------

@login_required
@group_required(['direcció'])
def importaFitxer(request):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials   
    
    if request.method == 'POST':
        form = PreinscripcioForm(request.POST, request.FILES)
        if form.is_valid():

            f = request.FILES['fitxer_Preinscripcio']
            resultat = s.sincronitza(f, user)
            
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
                        'importa.html', 
                        {'form': form},
                 )
