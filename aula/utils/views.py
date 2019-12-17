# This Python file uses the following encoding: utf-8

#templates
from django.http.response import HttpResponse, JsonResponse, Http404
from django.template import RequestContext
from django.shortcuts import render
from aula.apps.extKronowin.models import ParametreKronowin
from django.contrib.auth.hashers import check_password

from django.http import HttpResponseRedirect
from django.contrib.auth import logout

from django.contrib.auth.models import Group

#auth
from django.contrib.auth.decorators import login_required

from aula.settings import CUSTOM_SORTIDES_PAGAMENT_ONLINE
from aula.settings import CUSTOM_GRUPS_PODEN_VEURE_FOTOS
from aula.utils.decorators import group_required
from aula.utils import tools
from aula.apps.usuaris.models import User2Professor
from aula.apps.presencia.models import Impartir
from django.utils.datetime_safe import datetime
from django.db.models import Q

from django.conf import settings
from django.urls import reverse

from aula.utils.tools import calculate_my_time_off

from django.views.decorators.csrf import ensure_csrf_cookie


def keepalive(request):
    if request.user.is_authenticated:
        my_timeoff = calculate_my_time_off(request.user)
        return JsonResponse({'my_timeoff': my_timeoff ,
                             'my_safe_timeoff': my_timeoff -10 ,
                             'Im_authenticate': True, })
    else:
        return JsonResponse({'timeout': 0, 'safetimeout': 0, 'authenticate': False, })

def logout_page(request):
    try:
        del request.session['impersonacio']
    except KeyError:
        pass
    
    logout(request)
    return HttpResponseRedirect('/')

@ensure_csrf_cookie
def menu(request):
    #How do I make a variable available to all my templates?
    #http://readthedocs.org/docs/django/1.2.4/faq/usage.html#how-do-i-make-a-variable-available-to-all-my-templates
    
    if request.user.is_anonymous:      
        return HttpResponseRedirect( settings.LOGIN_URL )         
    else:
        #si és un alumne l'envio a mirar el seu informe
        try:
            if Group.objects.get(name='alumne') in request.user.groups.all():
                return HttpResponseRedirect( '/open/elMeuInforme/')
            
            #comprova que no té passwd per defecte:
            defaultPasswd, _ = ParametreKronowin.objects.get_or_create( nom_parametre = 'passwd', defaults={'valor_parametre':'1234'}  )
            if check_password( defaultPasswd.valor_parametre, request.user.password ):
                return HttpResponseRedirect( reverse( 'usuari__dades__canvi_passwd' ) )
            
            #si no té les dades informades:
            if not request.user.first_name or not request.user.last_name:
                return HttpResponseRedirect( '/usuaris/canviDadesUsuari/')
        
        except:
            pass  
          
        #prenc impersonate user:
        (user, _) = tools.getImpersonateUser(request)    
        
        #si és professor ves a mostra impartir:
        professor = User2Professor( user ) 
        if professor is not None:
            return HttpResponseRedirect( '/presencia/mostraImpartir/' )    

    
    return render(
            request,
            'main_page.html', 
            { },
            )

        

@login_required
@group_required(['direcció'])
def carregaInicial(request):
    
    return render(
            request,
            'carregaInicial.html', 
            { },
            )

@login_required    
def about(request):
    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    report = []
    taula = tools.classebuida()

    taula.titol = tools.classebuida()
    taula.titol.contingut = ''
    taula.titol.enllac = None

    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = u'Informació' 
    capcelera.enllac = None
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 80
    capcelera.contingut = u''
    taula.capceleres.append(capcelera)

    
    taula.fileres = []
        
    filera = []
    
    #-by--------------------------------------------
    camp = tools.classebuida()
    camp.enllac = None
    camp.contingut = u'Llicència'
    camp.enllac = ''
    filera.append(camp)

    #-tip--------------------------------------------

    licenseFile = open (settings.LICENSE_FILE, "r")
    tip=licenseFile.read()
    
    camp = tools.classebuida()
    camp.enllac = ''
    camp.contingut = tip
    filera.append(camp)
    
    taula.fileres.append( filera )

#-1--------------------------------------------
    filera = []
    
    camp = tools.classebuida()
    camp.enllac = None
    camp.contingut = u'Codi'
    camp.enllac = ''
    filera.append(camp)

    #-tip--------------------------------------------
    
    tip = u'''Pots revisar aquí el codi i les actualitzacions del programa.
    '''
    camp = tools.classebuida()
    camp.enllac = r'https://github.com/ctrl-alt-d/django-aula'
    camp.contingut = tip
    filera.append(camp)
    
    taula.fileres.append( filera )
    
    report.append(taula)
    
    #--Estadistiques Professor.....................
    if professor:
        taula = tools.classebuida()
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
            
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Estadístiques' 
        capcelera.enllac = None
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 80
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
            
        taula.fileres = []
            
        filera = []
        
        camp = tools.classebuida()
        camp.contingut = u'Percentatge de passar llista:'
        filera.append(camp) 
        
        camp = tools.classebuida()
        camp.enllac = None
        qProfessor = Q(  horari__professor = professor )
       
        qAvui = Q( dia_impartir = datetime.today() ) & Q( horari__hora__hora_fi__lt = datetime.now()  )
        qFinsAhir = Q( dia_impartir__lt = datetime.today() )
        qFinsAra  = qFinsAhir | qAvui
        qTeGrup = Q( horari__grup__isnull = False)
        imparticions = Impartir.objects.filter(qProfessor & qFinsAra & qTeGrup )    
        nImparticios = imparticions.count()
        nImparticionsLlistaPassada = imparticions.filter( professor_passa_llista__isnull = False ).count()

        pct = ('{0:.0f}'.format(nImparticionsLlistaPassada * 100 / nImparticios) if nImparticios > 0 else 'N/A')
        estadistica1 = u'{0}% ({1} classes impartides, {2} controls)'.format(pct, nImparticios, nImparticionsLlistaPassada)

            #---hores de classe
        nProfessor = Impartir.objects.filter( horari__professor = professor, horari__grup__isnull = False ).count()
        nTotal = Impartir.objects.filter( horari__grup__isnull = False).count()
        import re
        nProfessor = re.sub(r'(\d{3})(?=\d)', r'\1,', str(nProfessor)[::-1])[::-1]
        nTotal = re.sub(r'(\d{3})(?=\d)', r'\1,', str(nTotal)[::-1])[::-1]
        estadistica2 = u'''Aquest curs impartirem {0} hores de classe, d'aquestes, {1} les imparteixes tu.'''.format(
                                    nTotal,
                                    nProfessor
                                     )
        
        
        camp.contingut = u'{0}. {1}'.format(estadistica1, estadistica2)
        filera.append(camp)    
        
        taula.fileres.append( filera )
        
        report.append(taula)
        
    return render(
                request,
                'report.html',
                    {'report': report,
                     'head': 'About' ,
                    },
                )


@login_required
def pagamentOnLine(request):

    if not CUSTOM_SORTIDES_PAGAMENT_ONLINE:
        raise Http404()

    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials


    report = []
    taula = tools.classebuida()

    taula.titol = tools.classebuida()
    taula.titol.contingut = ''
    taula.titol.enllac = None

    taula.capceleres = []

    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = u'Informació'
    capcelera.enllac = None
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 80
    capcelera.contingut = u''
    taula.capceleres.append(capcelera)

    taula.fileres = []

    filera = []

    # -by--------------------------------------------
    camp = tools.classebuida()
    camp.enllac = None
    camp.contingut = u'Dades Fiscals'
    camp.enllac = ''
    filera.append(camp)

    # -tip--------------------------------------------

    dadesFiscalsFile = open(settings.DADES_FISCALS_FILE, "r")
    tip = dadesFiscalsFile.read()

    camp = tools.classebuida()
    camp.enllac = ''
    camp.contingut = tip
    filera.append(camp)

    taula.fileres.append(filera)

    # -1--------------------------------------------
    filera = []

    camp = tools.classebuida()
    camp.enllac = None
    camp.contingut = u'Política de vendes/devolucions'
    camp.enllac = ''
    filera.append(camp)

    # -tip--------------------------------------------

    politicaVendesFile = open(settings.POLITICA_VENDA_FILE, "r")
    tip = politicaVendesFile.read()

    camp = tools.classebuida()
    camp.enllac = ''
    camp.contingut = tip
    filera.append(camp)

    taula.fileres.append(filera)


    report.append(taula)

    return render(
        request,
        'report.html',
        {'report': report,
         'head': 'Pagament Online',
         },
    )


@login_required    
def calendariDevelop(request):
    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials

    return render(
                request,
                'calendariDevelop.html',
                    {
                     'head': 'Calendari desenvolupament.' ,
                    },
                )
    

def blanc( request ):
    return render(
                request,
                'blanc.html',
                    {},
                )
    
    
def allow_foto(private_file):
    request = private_file.request
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials
    pertany_al_grup_permes = (user
                              .groups
                              .filter(name__in=CUSTOM_GRUPS_PODEN_VEURE_FOTOS)
                              .exists()
                              )
    return (request.user.is_authenticated and pertany_al_grup_permes)