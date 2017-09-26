# This Python file uses the following encoding: utf-8

#templates
from django.contrib import messages
from django.template import RequestContext

#tables
from django.utils.safestring import mark_safe

from .tables2_models import HorariAlumneTable
from django_tables2 import RequestConfig

#from django import forms as forms
from aula.apps.alumnes.models import Alumne,  Curs, Grup
from aula.apps.usuaris.models import Professor
from aula.apps.assignatures.models import Assignatura
from aula.apps.presencia.models import Impartir

#workflow
from django.http import HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect

#auth
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required
from aula.apps.usuaris.models import User2Professor

#forms
from aula.apps.alumnes.forms import  triaMultiplesAlumnesForm,\
    triaAlumneSelect2Form
from aula.apps.alumnes.forms import triaAlumneForm

#helpers
from aula.utils import tools
from aula.apps.presencia.models import Impartir
from django.utils.datetime_safe import  date, datetime
from django.db.models import Q
from django.forms.models import modelformset_factory
from aula.apps.alumnes.reports import reportLlistaTutorsIndividualitzats
from aula.apps.avaluacioQualitativa.forms import alumnesGrupForm
from aula.apps.tutoria.models import TutorIndividualitzat
from aula.apps.alumnes.rpt_duplicats import duplicats_rpt
from aula.apps.alumnes.tools import fusiona_alumnes_by_pk
from aula.apps.alumnes.forms import promoForm, newAlumne


#duplicats
@login_required
@group_required(['direcció'])
def duplicats(request):
    report = duplicats_rpt()
    
    return render_to_response(
            'report.html',
                {'report': report,
                 'head': 'Alumnes' ,
                },
                context_instance=RequestContext(request))     
    

#duplicats
@login_required
@group_required(['direcció'])
def fusiona(request,pk):

    credentials = tools.getImpersonateUser(request)
    resultat = { 'errors': [], 'warnings':  [], 'infos':  [ u'Procés realitzat correctament' ]  }
    try:
        fusiona_alumnes_by_pk( int( pk ) , credentials)
    except Exception, e:
        resultat = { 'errors': [ unicode(e), ], 'warnings':  [], 'infos':  []  }
        
    
    return render_to_response(
                   'resultat.html', 
                   {'head': u'Error a l\'esborrar actuació.' ,
                    'msgs': resultat },
                   context_instance=RequestContext(request))     
 

#vistes--------------------------------------------------------------------------------------

  

#vistes--------------------------------------------------------------------------------------

@login_required
@group_required(['direcció'])
def assignaTutors( request ):
    #FormSet: Una opció seria fer servir formSet, però em sembla que
    #com ho estic fent ara és més fàcil per l'usuari
    #https://docs.djangoproject.com/en/dev/topics/forms/formsets
    from aula.apps.tutoria.models import Tutor 
    from aula.apps.alumnes.forms import tutorsForm
    #prefixes:
    #https://docs.djangoproject.com/en/dev/ref/forms/api/#prefixes-for-forms    
    formset = []
    if request.method == "POST":
        #un formulari per cada grup
        #totBe = True
        parellesProfessorGrup=set()
        for grup in Grup.objects.all():
            form=tutorsForm(
                                    request.POST,
                                    prefix=str( grup.pk )
                            )
            formset.append( form )
            if form.is_valid():
                tutor1 = form.cleaned_data['tutor1']
                tutor2 = form.cleaned_data['tutor2']
                tutor3 = form.cleaned_data['tutor3']
                if tutor1:  parellesProfessorGrup.add( ( tutor1.pk, grup)  )
                if tutor2:  parellesProfessorGrup.add( (tutor2.pk, grup)  )
                if tutor3:  parellesProfessorGrup.add( (tutor3.pk, grup)  )
            else:
                pass
                #totBe = False
                
        Tutor.objects.all().delete()
        for tutor_pk, grup in   parellesProfessorGrup:
            professor = Professor.objects.get( pk = tutor_pk )
            nouTutor = Tutor( professor = professor, grup = grup )
            nouTutor.save()
            #return HttpResponseRedirect( '/' )

                
    else:
        for grup in Grup.objects.all():
            tutor1 = tutor2 = tutor3 = None
            if len( grup.tutor_set.all() ) > 0: tutor1 = grup.tutor_set.all()[0].professor
            if len( grup.tutor_set.all() ) > 1: tutor2 = grup.tutor_set.all()[1].professor
            if len( grup.tutor_set.all() ) > 2: tutor3 = grup.tutor_set.all()[2].professor
            form=tutorsForm(
                                    prefix=str( grup.pk ),
                                    initial={ 'grup':  grup ,
                                             'tutor1': tutor1,
                                             'tutor2': tutor2,
                                             'tutor3': tutor3
                                             } )            
            formset.append( form )
            
    return render_to_response(
                  "formsetgrid.html", 
                  { "formset": formset,
                    "head": "Gestió de tutors",
                   },
                  context_instance=RequestContext(request))


@login_required
@group_required(['direcció'])
def llistaTutorsIndividualitzats( request ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials

    professor = User2Professor( user ) 
        
    head=u'Tutors Individualitzats'
    infoForm = []
    
    report = reportLlistaTutorsIndividualitzats(  )
     
    return render_to_response(
            'report.html',
                {'report': report,
                 'head': head ,
                },
                context_instance=RequestContext(request)) 


@login_required
@group_required(['direcció','psicopedagog'])
def informePsicopedagoc( request  ):

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    if request.method == 'POST':
        
        formAlumne = triaAlumneSelect2Form(request.POST ) #todo: multiple=True (multiples alumnes de cop)        
        if formAlumne.is_valid():            
            alumne = formAlumne.cleaned_data['alumne']
            return HttpResponseRedirect( r'/tutoria/detallTutoriaAlumne/{0}/all/'.format( alumne.pk ) )
        
    else:

        formAlumne = triaAlumneSelect2Form( )         
        
    return render_to_response(
                'form.html',
                    {'form': formAlumne,
                     'head': 'Triar alumne'
                    },
                    context_instance=RequestContext(request))    


@login_required
@group_required(['direcció'])
def gestionaAlumnesTutor( request , pk ):
    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials

    professor = Professor.objects.get( pk = int(pk) )
        
    head=u'Tutors Individualitzats'
    infoForm = []    
    formset = []
    
    if request.method == 'POST':
        totBe = True
        nous_alumnes_tutor = []
        for grup in Grup.objects.filter( alumne__isnull = False ).distinct():
            #http://www.ibm.com/developerworks/opensource/library/os-django-models/index.html?S_TACT=105AGX44&S_CMP=EDU
            form=triaMultiplesAlumnesForm(
                                    request.POST,
                                    prefix=str( grup.pk ),
                                    queryset =  grup.alumne_set.all()  ,                                    
                                    etiqueta = unicode( grup )  
                                    )
            formset.append( form )        
            if form.is_valid():
                for alumne in form.cleaned_data['alumnes']:
                    nous_alumnes_tutor.append( alumne )
            else:
                totBe = False
        if totBe:
            professor.tutorindividualitzat_set.all().delete()
            for alumne in nous_alumnes_tutor:
                ti = TutorIndividualitzat( professor = professor, alumne = alumne  )
                ti.credentials = credentials
                ti.save()
               
            return HttpResponseRedirect( '/alumnes/llistaTutorsIndividualitzats/' )
    else:
        for grup in Grup.objects.filter( alumne__isnull = False ).distinct():
            #http://www.ibm.com/developerworks/opensource/library/os-django-models/index.html?S_TACT=105AGX44&S_CMP=EDU
            inicial= [c.pk for c in grup.alumne_set.filter( tutorindividualitzat__professor = professor ) ]
            form=triaMultiplesAlumnesForm(
                                    prefix=str( grup.pk ),
                                    queryset =  grup.alumne_set.all()  ,                                    
                                    etiqueta = unicode( grup )  ,
                                    initial =  {'alumnes': inicial }
                                    )
            formset.append( form )
        
    return render_to_response(
                  "formset.html", 
                  {"formset": formset,
                   "head": head,
                   "formSetDelimited": True,
                   },
                  context_instance=RequestContext(request))      

#--------------------------------------------------------------------------------------------

@login_required
@group_required(['consergeria','professors','professional'])
def triaAlumne( request ):
    if not request.user.is_authenticated():
        return render_to_response('/login')   

    if request.method == 'POST':
        
        form = triaAlumneForm(request.POST)        
        if form.is_valid():
            return HttpResponse( unicode( form.cleaned_data['alumne'] )  )
    else:
    
        form = triaAlumneForm()
        
    return render_to_response(
                'form.html',
                    {'form': form,
                     'head': 'Resultat importació SAGA' ,
                    },
                    context_instance=RequestContext(request))

#--------------------- AJAX per seleccionar un alumne --------------------------------------------#

@login_required
@group_required(['consergeria','professors','professional'])
def triaAlumneCursAjax( request, id_nivell ):
    if request.method == 'GET':  #request.is_ajax()
        id_nivell = int( id_nivell )
        cursos = Curs.objects.filter( nivell__pk = id_nivell )
        message = u'<option value="" selected>-- Tria --</option>' ;
        for c in cursos:
            message +=  u'<option value="%s">%s</option>'% (c.pk, unicode(c) )
        return HttpResponse(message)

@login_required
@group_required(['consergeria','professors','professional'])
def triaAlumneGrupAjax( request, id_curs ):
    if request.method == 'GET':   #request.is_ajax()
        pk = int( id_curs )
        tots = Grup.objects.filter( curs__pk = pk )
        message = u'<option value="" selected>-- Tria --</option>' ;
        for iterador in tots:
            message +=  u'<option value="%s">%s</option>'% (iterador.pk, unicode(iterador) )
        return HttpResponse(message)

@login_required
@group_required(['consergeria','professors','professional'])
def triaAlumneAlumneAjax( request, id_grup ):
    if request.method == 'GET':   #request.is_ajax()
        pk = int( id_grup )
        tots = Alumne.objects.filter( grup__pk = pk )
        message = u'<option value="" selected>-- Tria --</option>' ;
        for iterador in tots:
            message +=  u'<option value="%s">%s</option>'% (iterador.pk, unicode(iterador) )
        return HttpResponse(message)

#---------------------  --------------------------------------------#

    
@login_required
@group_required(['professors'])
def elsMeusAlumnesAndAssignatures( request ):

    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor( user )     
    
    report = []
    
    nTaula=0

    assignatura_grup = set()
    for ca in Impartir.objects.filter( horari__professor = professor ):
        if ca.horari.grup is not None: 
            assignatura_grup.add( (ca.horari.assignatura, ca.horari.grup )  )
            
    for (assignatura, grup,) in  assignatura_grup: 
    
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = u'{0} - {1}'.format(unicode( assignatura ) , unicode( grup ) )
        
        taula.titol = tools.classebuida()
        taula.titol.contingut = ""
        
        capcelera_nom = tools.classebuida()
        capcelera_nom.amplade = 230
        capcelera_nom.contingut = u'{0} - {1}'.format(unicode( assignatura ) , unicode( grup ) )

        capcelera_nIncidencies = tools.classebuida()
        capcelera_nIncidencies.amplade = 90
        capcelera_nIncidencies.contingut = u'Incidències'

        capcelera_assistencia = tools.classebuida()
        capcelera_assistencia.amplade = 80
        capcelera_assistencia.contingut = u'Assist.'

        capcelera_nFaltes = tools.classebuida()
        capcelera_nFaltes.amplade = 340
        nClasses = Impartir.objects.filter( horari__professor = professor ,
                                            horari__assignatura = assignatura, 
                                            horari__grup = grup 
                                            ).count()
        nClassesImpartides =   Impartir.objects.filter( 
                                            horari__professor = professor ,
                                            horari__assignatura = assignatura, 
                                            horari__grup = grup, 
                                            dia_impartir__lte = date.today() 
                                            ).count() 

        capcelera_nFaltes.contingut = u' ({0}h impartides / {1}h)'.format( nClassesImpartides, nClasses)            

        capcelera_contacte = tools.classebuida()
        capcelera_contacte.amplade = 80
        capcelera_contacte.contingut = u'Dades de contacte Tutors.'
        
        taula.capceleres = [capcelera_nom, capcelera_nIncidencies, capcelera_assistencia, capcelera_nFaltes, capcelera_contacte]
        
        taula.fileres = []
        for alumne in Alumne.objects.filter( 
                            controlassistencia__impartir__horari__grup = grup,
                            controlassistencia__impartir__horari__assignatura = assignatura, 
                            controlassistencia__impartir__horari__professor = professor  ).distinct().order_by('cognoms'):
            
            filera = []
            
            #-nom--------------------------------------------
            camp_nom = tools.classebuida()
            camp_nom.enllac = None
            camp_nom.contingut = u'{0}'.format( alumne )
            filera.append(camp_nom)
            
            #-incidències--------------------------------------------
            camp_nIncidencies = tools.classebuida()
            camp_nIncidencies.enllac = None
            nIncidencies = alumne.incidencia_set.filter(
                                                        control_assistencia__impartir__horari__grup = grup,
                                                        control_assistencia__impartir__horari__professor = professor, 
                                                        control_assistencia__impartir__horari__assignatura = assignatura,
                                                        tipus__es_informativa = False 
                                                       ).count()
            nExpulsions = alumne.expulsio_set.filter( 
                                                        control_assistencia__impartir__horari__grup = grup,
                                                        control_assistencia__impartir__horari__professor = professor, 
                                                        control_assistencia__impartir__horari__assignatura = assignatura
                                                    ).exclude(
                                                        estat = 'ES'
                                                    ).count()
            camp_nIncidencies.multipleContingut = [ ( u'Incid: {0}'.format( nIncidencies ), None, ), 
                                                    ( u'Expul: {0}'.format( nExpulsions), None,  ) ]
            filera.append(camp_nIncidencies)

            #-Assistencia--------------------------------------------
            from django.db.models import Sum, Count
#                nFaltes = alumne.controlassistencia_set.filter( 
#                                                               estat__isnull = False  ,
#                                                               impartir__horari__assignatura = assignatura
#                                                        ).aggregate( 
#                                        ausencia = Sum( 'estat__pct_ausencia' ),
#                                        classes = Count( 'estat' ) 
#                                                        )
            
            controls = alumne.controlassistencia_set.filter(   
                                                    impartir__dia_impartir__lte = datetime.today(), 
                                                    impartir__horari__grup = grup,
                                                    impartir__horari__professor = professor, 
                                                    impartir__horari__assignatura = assignatura 
                                                           )
            
            nFaltesNoJustificades = controls.filter(  Q(estat__codi_estat = 'F' )  ).count()
            nFaltesJustificades = controls.filter( estat__codi_estat = 'J'  ).count()
            nRetards = controls.filter( estat__codi_estat = 'R'  ).count()
            nControls = controls.filter(estat__codi_estat__isnull = False ).count( )
            camp = tools.classebuida()
            camp.enllac = None
            tpc = 100.0 - ( ( 100.0 * float(nFaltesNoJustificades + nFaltesJustificades) ) / float(nControls) ) if nControls > 0 else 'N/A'
            camp.contingut = u"""{0:.2f}%""".format( tpc ) if nControls > 0 else 'N/A'
            filera.append(camp)

            camp = tools.classebuida()
            camp.enllac = None
            contingut = "Controls: {0},F.no J.: {1},F.Just: {2},Retards: {3}".format( nControls, nFaltesNoJustificades , nFaltesJustificades, nRetards)
            camp.multipleContingut =  [ (c, None,) for c in contingut.split(',') ]
            filera.append(camp)

            #--
            #-nom--------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0},{1}'.format( alumne.tutors, alumne.telefons )
            filera.append(camp)
            
            
            taula.fileres.append( filera )
        
        report.append(taula)
        
    return render_to_response(
                'reportTabs.html',
                    {'report': report,
                     'head': u'Informació alumnes' ,
                    },
                    context_instance=RequestContext(request))            
        


#---------------------  --------------------------------------------#

    
@login_required
@group_required(['professors'])
def blanc( request ):
    return render_to_response(
                'blanc.html',
                    {},
                    context_instance=RequestContext(request)) 


# ---------------- PROMOCIONS ------------------------#

@login_required
@group_required(['direcció'])
def llistaGrupsPromocionar(request):
    grups = Grup.objects.all().order_by("descripcio_grup")
    return render_to_response('mostraGrupsPromocionar.html', {"grups" : grups}, context_instance=RequestContext(request))

@login_required
@group_required(['direcció'])
def nouAlumnePromocionar(request):
    #Aqui va el tractament del formulari i tota la polla...

    if request.method == 'POST':
        # Ve per post, he de guardar l'alumne si les dades estan correctes
        pass
    form = newAlumne()
    return render_to_response('mostraFormulariPromocionar.html', {'form': form}, context_instance=RequestContext(request))

@login_required
@group_required(['direcció'])
def mostraGrupPromocionar(request, grup=""):

    from datetime import date
    PromoFormset = modelformset_factory(Alumne, form=promoForm, extra = 0)
    if request.method == 'POST':
        curs_vinent = request.POST.get('curs_desti')
        print request.POST
        formset = PromoFormset(request.POST)
        for form in formset.forms:
            if form.is_valid():

                decisio = form.cleaned_data['decisio']
                if (decisio == "2"):

                    id =  form.cleaned_data['id'].id
                    alumne = Alumne.objects.get(id=id)
                    alumne.data_baixa = date.today()
                    alumne.estat_sincronitzacio = 'DEL'
                    alumne.motiu_bloqueig = 'Baixa'
                    alumne.save()


                if (decisio == "0"):

                    id = form.cleaned_data['id'].id
                    alumne = Alumne.objects.get(id = id)
                    alumne.grup_id = curs_vinent
                    alumne.save()


        pass

    grups = Grup.objects.all().order_by("descripcio_grup")
    grup_actual = Grup.objects.get(id=grup)
    alumnes = Alumne.objects.filter(grup=grup, data_baixa__isnull = True ).order_by("cognoms")
    if (len(alumnes) == 0):

        msg = "Aquest grup no te alumnes actualment."
        return render_to_response('mostraGrupsPromocionar.html', {"grups" : grups, "msg": msg}, context_instance=RequestContext(request))

    formset = PromoFormset(queryset=alumnes)

    return render_to_response('mostraGrupPromocionar.html', {"grup_actual" : grup_actual, "formset" : formset, "grups":grups}, context_instance=RequestContext(request))



@login_required
@group_required(['consergeria'])
def detallAlumneHorari(request, pk, detall='all'):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    qAvui = (Q(impartir__dia_impartir=datetime.today()))
    alumne = get_object_or_404( Alumne, pk=pk)
    controlOnEslAlumneAvui = alumne.controlassistencia_set.filter(qAvui)
    aules =[]
    for c in controlOnEslAlumneAvui:
        novaaula={'aula': c.impartir.horari.nom_aula,
                  'professor': c.impartir.horari.professor,
                  'hora': c.impartir.horari.hora,
                  'hora_inici': c.impartir.horari.hora.hora_inici,
                  'assignatura': c.impartir.horari.assignatura,
                  'es_hora_actual': ( c.impartir.horari.hora.hora_inici 
                                      <= datetime.now().time() 
                                      <= c.impartir.horari.hora.hora_fi ),
                  }
        aules.append(novaaula)

    aules_sorted = sorted(aules, key= lambda x: x['hora_inici'] )
    table=HorariAlumneTable(aules_sorted)
    table.order_by = 'hora_inici' 
    RequestConfig(request).configure(table)

    missatge = u"Horari de l'alumne/a <b>{0}</b> del grup {1}".format(alumne,alumne.grup)
    messages.info(request, mark_safe( missatge)  )

    return render(
        request,
        'table2.html',
        {'table': table,
         },
        context_instance=RequestContext(request))

@login_required
@group_required(['consergeria'])
def cercaUsuari(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    if request.method == 'POST':
        formUsuari = triaAlumneSelect2Form(request.POST)  # todo: multiple=True (multiples alumnes de cop)
        if formUsuari.is_valid():
            alumne = formUsuari.cleaned_data['alumne']
            return HttpResponseRedirect(r'/alumnes/detallAlumneHorari/{0}/all/'.format(alumne.pk))
    else:
        formUsuari = triaAlumneSelect2Form()
    return render_to_response(
        'form.html',
        {'form': formUsuari,
         'head': 'Triar usuari'
         },
        context_instance=RequestContext(request))
