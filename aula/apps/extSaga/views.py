# This Python file uses the following encoding: utf-8
import os

from django.conf import settings
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required
from aula.utils import tools
from aula.apps.usuaris.models import User2Professor
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.shortcuts import render
from django.template.context import RequestContext
from aula.apps.extSaga.forms import sincronitzaSagaForm
from aula.apps.extSaga.models import Grup2Aula
from django.forms.models import modelformset_factory
from django.http.response import HttpResponseRedirect


@login_required
@group_required(['direcció'])
def sincronitzaSaga(request):

    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor( user )     
    
    from aula.apps.extSaga.sincronitzaSaga import sincronitza

    if request.method == 'POST':
        
        form = sincronitzaSagaForm(request.POST, request.FILES)
        
        if form.is_valid():
            f = request.FILES['fitxerSaga']
            path = default_storage.save('tmp/saga.csv', ContentFile(f.read()))
            tmp_file = os.path.join(settings.MEDIA_ROOT, path)
            with open(tmp_file, 'r', encoding="latin1") as f1:
                resultat=sincronitza(f1, user)
            default_storage.delete(path)
            return render(
                    request,
                    'resultat.html', 
                    {'head': 'Resultat importació SAGA' ,
                     'msgs': resultat },
                    )
        
    else:
        form = sincronitzaSagaForm()
        
    return render(
                    request,
                    'sincronitzaSaga.html', 
                    {'form': form },
                )
    
    
    

#---------------------------------------------------------------------------------

@login_required
@group_required(['direcció','administradors'])
def assignaGrups( request ):
        
    #prefixes:
    #https://docs.djangoproject.com/en/dev/ref/forms/api/#prefixes-for-forms    
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
                    "head": "Manteniment de grups Saga",
                   },
                 )
    