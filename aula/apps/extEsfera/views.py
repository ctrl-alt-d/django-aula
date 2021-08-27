# This Python file uses the following encoding: utf-8
from django.contrib.auth.decorators import login_required
from aula.settings import CUSTOM_DADES_ADDICIONALS_ALUMNE
from aula.utils.decorators import group_required
from aula.utils import tools
from aula.apps.usuaris.models import User2Professor
from django.shortcuts import render
from aula.apps.extEsfera.forms import sincronitzaEsferaForm, dadesAddicionalsForm
from aula.apps.extEsfera.models import Grup2Aula
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect


@login_required
@group_required(['direcció'])
def sincronitzaEsfera(request):

    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor( user )     
    
    from aula.apps.extEsfera.sincronitzaEsfera import sincronitza

    if request.method == 'POST':
        
        form = sincronitzaEsferaForm(request.POST, request.FILES)
        
        if form.is_valid():
            f=request.FILES['fitxerEsfera']
            resultat=sincronitza(f, user)
            
            return render(
                    request,
                    'resultat.html', 
                    {'head': 'Resultat importació Esfer@' ,
                     'msgs': resultat },
                    )
        
    else:
        form = sincronitzaEsferaForm()
        
    return render(
                    request,
                    'sincronitzaEsfera.html',
                    {'form': form },
                )
    
    
    

#---------------------------------------------------------------------------------

@login_required
@group_required(['direcció','administradors'])
def assignaGrups( request ):

    formset = []
    
    factoria = modelformset_factory( Grup2Aula, extra = 0, exclude=(), can_delete=False )
    
    if request.method == "POST":
        #un formulari per cada grup
        totBe = True
        formset= factoria( request.POST )
        for f in formset:
            if f.is_valid():
                f.save()
            else:
                totBe = False
                
        if totBe:
            return HttpResponseRedirect( '/' )

                
    else:
        formset= factoria( )
            
    return render(
                  request,
                  "formsetgrid.html", 
                  { "formset": formset,
                    "head": "Manteniment de grups Esfera",
                   },
                 )



@login_required
@group_required(['direcció'])
def dadesAddicionals(request):
    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor(user)

    from aula.apps.extEsfera.sincronitzaEsfera import dades_adiccionals
    camps_addicionals = [x['label'] for x in CUSTOM_DADES_ADDICIONALS_ALUMNE]
    if request.method == 'POST':
        form = dadesAddicionalsForm(request.POST, request.FILES)
        if form.is_valid():
            f = request.FILES['fitxerDadesAddicionals']
            resultat = dades_adiccionals(f, user)
            return render(
                request,
                'resultat.html',
                {'head': 'Resultat importació dades addicionals',
                 'msgs': resultat},
            )
    else:
        form = dadesAddicionalsForm()
    return render(
        request,
        'dadesAddicionals.html',
        {'form': form,
         'camps_addicionals': camps_addicionals},
    )
