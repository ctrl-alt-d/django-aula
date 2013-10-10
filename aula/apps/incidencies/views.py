# This Python file uses the following encoding: utf-8
from aula.utils.widgets import DateTextImput
from itertools import groupby
#formularis
from aula.apps.incidencies.forms import posaIncidenciaAulaForm, posaExpulsioForm, posaExpulsioFormW2,\
    incidenciesRelacionadesForm
from django import forms
from aula.utils.forms import ckbxForm
from django.conf import settings

#templates
from django.template import RequestContext

#models
from aula.apps.presencia.models import Impartir, ControlAssistencia
from aula.apps.alumnes.models import Alumne
from aula.apps.incidencies.models import Incidencia, ExpulsioDelCentre
from aula.apps.usuaris.models import  Professor, User2Professor, Professional, User2Professional,\
    Accio
from aula.apps.incidencies.models import Expulsio
from aula.utils import tools    

from aula.utils.widgets import DateTimeTextImput,DateTextImput

#consultes
#from django.db.models import Q

#auth
from django.contrib.auth.decorators import login_required

#workflow
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.datetime_safe import datetime

#excepcions
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.http import Http404

#dates
from datetime import date, timedelta

#helpers
from django.forms.models import modelform_factory
from aula.utils.decorators import group_required
from aula.apps.horaris.models import FranjaHoraria
from django.core.exceptions import ObjectDoesNotExist
from aula.apps.incidencies.business_rules.incidencia import incidencia_despres_de_posar
from aula.apps.incidencies.business_rules.expulsio import expulsio_despres_de_posar
from django.db.models.aggregates import Count
from django.utils.text import slugify



#vistes -----------------------------------------------------------------------------------
@login_required
@group_required(['professors'])
def posaIncidenciaAula(request, pk):           #pk = pk_impartir
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    impartir = get_object_or_404(Impartir, pk=pk)
    
    head=u'Incidències aula ' + unicode( impartir )

    #Posa incidències
    alumnes = Alumne.objects.filter( pk__in = [ ca.alumne.pk for ca in impartir.controlassistencia_set.all() ] )
    
    if request.method == 'POST':
        form = posaIncidenciaAulaForm(request.POST, queryset=alumnes, etiqueta= u'Posar incidència a:' )
        
        if form.is_valid():
            
            alumnes_amb_incidencia = form.cleaned_data['alumnes']
            frases_de_la_bdd = form.cleaned_data['frases']
            frase_manual = form.cleaned_data['frase']
            es_informativa = form.cleaned_data['es_informativa']
            totes_les_frases = [ frase.frase for frase in frases_de_la_bdd ] + ( [ frase_manual ] if frase_manual else []    )
            
            s_ha_pogut_crear_la_incidencia = False
            for alumne_amb_incidencia in alumnes_amb_incidencia:
                for frase in totes_les_frases :
                    try:
                        control_assistencia = impartir.controlassistencia_set.get( alumne = alumne_amb_incidencia )
                        incidencia, created = Incidencia.objects.get_or_create( 
                                                professional = User2Professional( user ),
                                                control_assistencia = control_assistencia, 
                                                alumne = alumne_amb_incidencia, 
                                                descripcio_incidencia = frase,
                                                es_informativa = es_informativa )                        
                        s_ha_pogut_crear_la_incidencia = True
                        if created:
                            #LOGGING
                            Accio.objects.create( 
                                    tipus = 'IN',
                                    usuari = user,
                                    l4 = l4,
                                    impersonated_from = request.user if request.user != user else None,
                                    text = u"""Posada incidència a l'alumne {0}. Text incidència: {1}""".format( incidencia.alumne , incidencia.descripcio_incidencia)
                                )                             
                            incidencia_despres_de_posar( incidencia )
                    except ValidationError, e:
                        #Com que no és un formulari de model cal tractar a mà les incidències del save:
                        for _, v in e.message_dict.items():
                            form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  v  )
                

            if not s_ha_pogut_crear_la_incidencia:
                form._errors.setdefault(NON_FIELD_ERRORS, []).append( u'''No s'ha pogut crear la incidència.
                                    Comprova que has seleccionat al menys un alumne i una frase''' )
            else:
                #netejo el formulari per que no quedi marcat alumne i falta.
                form=posaIncidenciaAulaForm( queryset=alumnes, etiqueta= u'Posar incidència a'  )
                                      
    else:
        form=posaIncidenciaAulaForm( queryset=alumnes, etiqueta= u'Posar incidència a'  )

    #Recull incidències ( i permet afegir-ne més) 
    incidenciesXfrase = {}              
    for control_assistencia in impartir.controlassistencia_set.all():
        for incidencia in control_assistencia.incidencia_set.all():
            frase = incidencia.descripcio_incidencia
            incidenciesXfrase.setdefault(frase, []) .append(  incidencia  )
            

    #Expulsion
    expulsions = []
    for control_assistencia in impartir.controlassistencia_set.all():
        for expulsio in control_assistencia.expulsio_set.all():
            expulsions.append(expulsio)
                        
    return render_to_response(
                  "posaIncidenciaAula.html", 
                  {"form": form,
                   "incidenciesXfrase": incidenciesXfrase,
                   'expulsions': expulsions,
                   "id_impartir":  pk ,
                   "head": head,
                   },
                  context_instance=RequestContext(request))


@login_required
@group_required(['professors'])
def eliminaIncidenciaAula(request, pk):           #pk = pk_incidencia
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
        
    try:
        incidencia = Incidencia.objects.get(pk =pk)
    except:
        return render_to_response(
                        'resultat.html', 
                        {'head': u'Error eliminant incidència.' ,
                         'msgs': { 'errors': [], 'warnings':  [u'Aquesta incidència ja no existeix'], 'infos':  [] } },
                        context_instance=RequestContext(request)) 
    
    pk_impartir = incidencia.control_assistencia.impartir.pk

    url_next = '/incidencies/posaIncidenciaAula/%s/'% ( pk_impartir )
    try:
        incidencia.credentials = credentials
        incidencia.delete()

        #LOGGING
        Accio.objects.create( 
                tipus = 'IN',
                usuari = user,
                l4 = l4,
                impersonated_from = request.user if request.user != user else None,
                text = u"""Eliminada incidència d'aula de l'alumne {0}. Text incidència: {1}""".format( incidencia.alumne , incidencia.descripcio_incidencia)
            )  
        
    except ValidationError, e:
        import itertools
        resultat = { 'errors': list( itertools.chain( *e.message_dict.values() ) ), 
                    'warnings':  [], 'infos':  [], 'url_next': url_next }
        return render_to_response(
                       'resultat.html', 
                       {'head': u'Error a l\'esborrar incidència d \'aula' ,
                        'msgs': resultat },
                       context_instance=RequestContext(request))    
    
    
    return HttpResponseRedirect( url_next )    
    

@login_required
@group_required(['professors','professional'])
def eliminaIncidencia(request, pk):           #pk = pk_incidencia

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
        
    try:
        incidencia = Incidencia.objects.get(pk =pk)
    except:
        return render_to_response(
                        'resultat.html', 
                        {'head': u'Error al crear expulsió per acumulació' ,
                         'msgs': { 'errors': [], 'warnings':  [u'Aquesta incidència ja no existeix'], 'infos':  [] } },
                        context_instance=RequestContext(request)) 
    
    incidencia.credentials = credentials
    
    url_next = '/incidencies/llistaIncidenciesProfessional/'
    try:
        incidencia.delete()
        #LOGGING
        Accio.objects.create( 
                tipus = 'IN',
                usuari = user,
                l4 = l4,
                impersonated_from = request.user if request.user != user else None,
                text = u"""Eliminada incidència de l'alumne {0}. Text incidència: {1}""".format( incidencia.alumne , incidencia.descripcio_incidencia)
            )          
    except ValidationError, e:
        import itertools
        resultat = { 'errors': list( itertools.chain( *e.message_dict.values() ) ), 
                    'warnings':  [], 'infos':  [], 'url_next': url_next }
        return render_to_response(
                       'resultat.html', 
                       {'head': u'Error a l\'esborrar incidència d \'aula' ,
                        'msgs': resultat },
                       context_instance=RequestContext(request))    
    
    
    return HttpResponseRedirect( url_next )    
    
#dev novaEntrevista( request, pk ):
#https://docs.djangoproject.com/en/dev/ref/contrib/formtools/form-wizard/

#vistes -----------------------------------------------------------------------------------

from aula.apps.alumnes.forms import triaAlumneForm

@login_required
@group_required(['professors','professional'])
def posaIncidencia( request ):

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
    missatge = ""
    
    formIncidenciaF = modelform_factory(Incidencia, fields=['dia_incidencia',
                                                            'franja_incidencia',
                                                            'descripcio_incidencia',
                                                            'es_informativa'])
    formIncidenciaF.base_fields['dia_incidencia'].widget =  DateTextImput()               
    formIncidenciaF.base_fields['descripcio_incidencia'].widget = forms.TextInput(attrs={'style':'width:400px;'} )   

    formset = []
    if request.method == 'POST':
        
        formAlumne = triaAlumneForm(request.POST ) #todo: multiple=True (multiples alumnes de cop)        
        incidencia = Incidencia ( es_vigent = True )
        incidencia.professional = User2Professional(user)
        incidencia.credentials = credentials
        formIncidencia = formIncidenciaF(request.POST, instance = incidencia )
        if formAlumne.is_valid():            
            alumne = formAlumne.cleaned_data['alumne']
            incidencia.alumne = alumne            
            if formIncidencia.is_valid(): 
                    incidencia = formIncidencia.save( )
                    
                    #LOGGING
                    Accio.objects.create( 
                            tipus = 'IN',
                            usuari = user,
                            l4 = l4,
                            impersonated_from = request.user if request.user != user else None,
                            text = u"""Posar incidència a {0}. Text incidència: {1}""".format( alumne, incidencia.descripcio_incidencia )
                        )                    
                    
                    missatge = u"Incidència anotada"
                    incidencia_despres_de_posar( incidencia )
#                    incidencia = formIncidencia.save(commit = False )
#                    try:
#                        incidencia.save()
#                    except ValidationError, e:
#                        formIncidencia._errors = {}
#                        for _, v in e.message_dict.items():
#                            formIncidencia._errors.setdefault(NON_FIELD_ERRORS, []).extend(  v  ) 
#                    else:
#                        Incidencia_despres_de_posar( incidencia )
#                        url = '/incidencies/llistaIncidenciesProfessional'  #todo: a la pantalla d''incidencies
#                        return HttpResponseRedirect( url )    
#                    return HttpResponseRedirect( url )    

        formset.append( formAlumne )
        formset.append( formIncidencia )
        
    else:

        formAlumne = triaAlumneForm( ) #todo: multiple=True (multiples alumnes de cop)        
#        formIncidenciaF = modelform_factory(Incidencia, fields=['dia_incidencia',
#                                                                'franja_incidencia',
#                                                                'descripcio_incidencia',
#                                                                'es_informativa'])
#        formIncidenciaF.base_fields['dia_incidencia'].widget =  DateTextImput()               
        formIncidencia = formIncidenciaF()

        formset.append( formAlumne )
        formset.append( formIncidencia )
        
    return render_to_response(
                'formset.html',
                    {'formset': formset,
                     'head': 'Incidència' ,
                     'missatge': missatge
                    },
                    context_instance=RequestContext(request))


#vistes -----------------------------------------------------------------------------------


@login_required
@group_required(['professors'])
def posaExpulsio( request ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials     

    formset = []
    if request.method == 'POST':
        
        expulsio = Expulsio(  )
        expulsio.credentials = credentials
        expulsio.professor_recull =  User2Professor( user )
        
        formAlumne = triaAlumneForm(request.POST )   
        formExpulsio = posaExpulsioForm(data=request.POST, instance = expulsio )

        if formAlumne.is_valid():
            expulsio.alumne = formAlumne.cleaned_data['alumne']
            if formExpulsio.is_valid():
                expulsio.save()
                                    
                url = '/incidencies/posaExpulsioW2/{u}'.format(u=expulsio.pk)  
                return HttpResponseRedirect( url )    
         
        else:
            formset.append( formAlumne )
            formset.append( formExpulsio )
        
    else:

        formAlumne = triaAlumneForm( ) 
        
        franja_actual = None
        try:
            from aula.apps.horaris.models import FranjaHoraria
            franja_actual =  FranjaHoraria.objects.filter( hora_inici__lte = datetime.now() ).filter( hora_fi__gte = datetime.now() ).get()
        except:
            pass
            
        formExpulsio = posaExpulsioForm( initial = {  'franja_expulsio' : franja_actual, 'dia_expulsio': datetime.today() } )

        formset.append( formAlumne )
        formset.append( formExpulsio )
        
    return render_to_response(
                'formset.html',
                    {'formset': formset,
                     'head': u'Recullir Expulsió (Pas 1/2)' ,
                    },
                    context_instance=RequestContext(request))    


@login_required
@group_required(['professors'])
def posaExpulsioW2( request, pk ):
    credentials = tools.getImpersonateUser(request) 
    ( user , l4 ) = credentials
                
    expulsio = get_object_or_404( Expulsio, pk = pk)
    
    #seg---------
    if not ( l4 or expulsio.professor_recull.getUser().pk == user.pk) or expulsio.estat != 'ES':
        raise Http404() 
    
    expulsio.credentials = credentials
    
    infoForm = [
          ('Alumne',unicode( expulsio.alumne) ),
          ('Hora', expulsio.franja_expulsio ),
                ]

    #Miro quin podria ser el professor:
    from django.db.models import Q
    q_alumne = Q( alumne = expulsio.alumne )
    q_dia = Q( impartir__dia_impartir = expulsio.dia_expulsio )
    q_franja = Q( impartir__horari__hora = expulsio.franja_expulsio )
    
    possible_control_assistencia = None
    possible_professor = None
    possibles_professors = []
            
    possibles_controls_assistencia = ControlAssistencia.objects.filter( q_alumne &  q_dia & q_franja ).order_by()
    if possibles_controls_assistencia.exists():
        possible_control_assistencia = possibles_controls_assistencia[0]

        possible_professor = ( possible_control_assistencia.impartir.professor_passa_llista or
                               possible_control_assistencia.impartir.professor_guardia or 
                               possible_control_assistencia.impartir.horari.professor
                               )
        
        if possible_control_assistencia.impartir.professor_passa_llista is not None:
            possibles_professors.append(possible_control_assistencia.impartir.professor_passa_llista)
        
        if possible_control_assistencia.impartir.professor_guardia is not None:
            possibles_professors.append(possible_control_assistencia.impartir.professor_guardia)
        
        if possible_control_assistencia.impartir.horari.professor is not None:
            possibles_professors.append(possible_control_assistencia.impartir.horari.professor)
                
    if request.method == 'POST':
        
        formExpulsio = posaExpulsioFormW2(request.POST, instance = expulsio )
        formExpulsio.instance.estat = 'AS'
        if formExpulsio.is_valid():                        
            expulsio = formExpulsio.save( commit = False )
            if expulsio.professor in possibles_professors:
                expulsio.control_assistencia = possible_control_assistencia
            
            expulsio.save()

            #LOGGING
            Accio.objects.create( 
                    tipus = 'RE',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Recullir expulsió d'alumne {0}. Professor que expulsa: {1}""".format( expulsio.alumne, expulsio.professor )
                )    
                            
            expulsio_despres_de_posar( expulsio )
            url = '/missatgeria/elMeuMur/'  
            return HttpResponseRedirect( url )    
        
    else:

        if possible_control_assistencia is None:
            infoForm.append( ('Assignatura', u'''Aquest alumne no està assignat a cap classe a aquesta hora''' ) )
        else:
            infoForm.append( ('Assignatura', possible_control_assistencia.impartir.horari.assignatura ) )
        
        #TODO: Si no està a cap llista cal informar-ho!! 
        formExpulsio = posaExpulsioFormW2(instance = expulsio, initial = { 'professor':possible_professor } )

        
    return render_to_response(
                'form.html',
                    {'form': formExpulsio,
                     'infoForm': infoForm,
                     'head': u'Recullir Expulsió (Pas 2/2)' ,
                    },
                    context_instance=RequestContext(request))   
 


@login_required
@group_required(['professors'])
def editaExpulsio( request, pk ):
    #from incidencies.forms import editaExpulsioForm
    
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    expulsio = get_object_or_404( Expulsio, pk = pk)
    
    #seg---------
    pot_entrar = l4 or (expulsio.professor is not None and expulsio.professor.pk == user.pk) or user.groups.filter( name= u'direcció').exists()
    if not pot_entrar:
        raise Http404() 
    
    expulsio.credentials = credentials
    
    edatAlumne = None
    try:
        edatAlumne = (date.today() - expulsio.alumne.data_neixement).days / 365 
    except:
        pass
    
    infoForm = [
          ('Alumne',unicode( expulsio.alumne) ),
          ('Dia', expulsio.dia_expulsio ) ,
          ('Hora', expulsio.franja_expulsio ) ,
          ( 'Telèfon Alumne', expulsio.alumne.telefons),                     
          ( 'Nom tutors', expulsio.alumne.tutors),                     
          ( 'Edat alumne', edatAlumne ),
          ( 'Professor que expulsa',   expulsio.professor if expulsio.professor else 'N/A' ),
          ( 'Professor que recull expulsió', expulsio.professor_recull if expulsio.professor_recull else 'N/A'),                     
                ]
    
    fields = [ 'motiu_expulsio', 
              'tutor_contactat_per_l_expulsio', 
              'moment_comunicacio_a_tutors', 
              'tramitacio_finalitzada' ]
    if l4:
        fields.extend( [ 'professor_recull',
                        'dia_expulsio', 
                        'franja_expulsio', 
                        'provoca_expulsio_centre', 
                        'es_vigent'  ] )

    
    widgets = { 'moment_comunicacio_a_tutors': DateTimeTextImput()}
    editaExpulsioFormF = modelform_factory( Expulsio, fields = fields,widgets=widgets)
    #editaExpulsioFormF.base_fields['moment_comunicacio_a_tutors'].widget = forms.DateTimeInput(attrs={'class':'datepickerT'} )
    
    try:
        editaExpulsioFormF.base_fields['dia_expulsio'].widget = DateTextImput()
    except:
        pass
    
    if request.method == 'POST':
       
        #TODO: Canviar per una factoria: mirar actuacions.
        formExpulsio = editaExpulsioFormF(data = request.POST, instance = expulsio )
        can_delete = ckbxForm( data=request.POST, label = 'Esborrar expulsió', 
                             help_text=u'''Marca aquesta casella per esborrar aquesta expulsió''' )
        
        if formExpulsio.is_valid() and can_delete.is_valid():
            if can_delete.cleaned_data['ckbx'] and l4:
                expulsio.delete()
                #LOGGING
                Accio.objects.create( 
                        tipus = 'EE',
                        usuari = user,
                        l4 = l4,
                        impersonated_from = request.user if request.user != user else None,
                        text = u"""Esborrada expulsió d'alumne {0}.""".format( expulsio.alumne )
                    )  
            else:
                expulsio.save()
                #LOGGING
                Accio.objects.create( 
                        tipus = 'EE',
                        usuari = user,
                        l4 = l4,
                        impersonated_from = request.user if request.user != user else None,
                        text = u"""Editada expulsió d'alumne {0}.""".format( expulsio.alumne )
                    )                  
            url = '/incidencies/llistaIncidenciesProfessional/'
            return HttpResponseRedirect( url )
        
    else:
        formExpulsio = editaExpulsioFormF( instance = expulsio )
        can_delete = ckbxForm( data=request.POST, label = 'Esborrar expulsió:', 
                             help_text=u'''Marca aquesta cassella per esborrar aquesta expulsió''' )

    
    formExpulsio.infoForm = infoForm
    formset = [ formExpulsio ]
    formset.extend ( [  can_delete ] if l4 else []  )

    return render_to_response(
                'formset.html',
                    {'formset': formset,
                     'infoForm': infoForm,
                     'head': 'Expulsió' ,
                    },
                    context_instance=RequestContext(request))    

#--------------------------------------------------------------------------------------------------

@login_required
@group_required(['professors'])
def posaExpulsioPerAcumulacio( request, pk ):
    
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials    
    
    fa_30_dies = date.today() - timedelta( days = 30 )
    try:
        incidencia = Incidencia.objects.get(pk =pk)
    except:
        return render_to_response(
                        'resultat.html', 
                        {'head': u'Error al crear expulsió per acumulació' ,
                         'msgs': { 'errors': [], 'warnings':  [u'Aquesta incidència ja no existeix'], 'infos':  [] } },
                        context_instance=RequestContext(request)) 
    
    professional = incidencia.professional
    professor = User2Professor(professional.getUser() ) 
    
    #seg---------
    te_permis = (l4 or user.pk == professional.pk) 
    if not te_permis :
        raise Http404()
    
    #si l'expulsió ja ha estat generada abans l'envio a l'expulsió
    #seria el cas que seguissin l'enllaç d'un Missatge:
    
    if incidencia.provoca_expulsio:
        url_next = '/incidencies/editaExpulsio/{0}/'.format( incidencia.provoca_expulsio.pk  )    
        return HttpResponseRedirect( url_next )
    
    alumne = incidencia.alumne
    incidencies = alumne.incidencia_set.filter(  
                                               es_vigent = True,
                                               es_informativa = False,
                                               dia_incidencia__gte = fa_30_dies,
                                               professional = professional
                                            ) 
    enTe3oMes = incidencies.count() >= 3
    professor_recull = User2Professor(user) 
    
    str_incidencies = u''
    separador = u''
    for i in incidencies:
        str_incidencies +=  ( separador  + i.descripcio_incidencia + u'('+ unicode ( i.dia_incidencia) + u')')
        separador = u', '
  
    
    motiu = u'''Expulsió per acumulació d'incidències: {0}'''.format( str_incidencies )
    
    url_next = '/incidencies/llistaIncidenciesProfessional/'  #todo: a la pantalla d''incidencies
    if enTe3oMes:
        
        try:
            expulsio = Expulsio.objects.create(
                        estat = 'AS',
                        professor_recull = professor_recull,
                        professor = professor,
                        alumne = alumne,
                        dia_expulsio = incidencia.dia_incidencia,
                        franja_expulsio = incidencia.franja_incidencia,
                        motiu_expulsio = motiu,
                        es_expulsio_per_acumulacio_incidencies = True                        
                        )

            #LOGGING
            Accio.objects.create( 
                    tipus = 'EE',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Creada expulsió d'alumne {0} per acumulació d'incidències.""".format( expulsio.alumne )
                )   
        
            expulsio_despres_de_posar( expulsio )
            incidencies.update( es_vigent = False, provoca_expulsio = expulsio, es_informativa = False )
        except ValidationError, e:
            import itertools
            resultat = { 'errors': list( itertools.chain( *e.message_dict.values() ) ), 
                        'warnings':  [], 'infos':  [], 'url_next': url_next }
            return render_to_response(
                           'resultat.html', 
                           {'head': u'Error al crear expulsió per acumulació.' ,
                            'msgs': resultat },
                           context_instance=RequestContext(request))  

    return HttpResponseRedirect( url_next )         

#--------------------------------------------------------------------------------------------------

@login_required
@group_required(['professors','professional'])
def llistaIncidenciesProfessional( request ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
        
    professional = get_object_or_404(Professional, pk = user.pk )
    professor = get_object_or_404(Professor, pk = user.pk )  #TODO: compte, Han de poder entrar els no professors!
    
    nomProfessional = unicode( professional )
    
    #TODO: Deixar entrar a l'equip directiu 
    if user != professor.getUser():
        return HttpResponseRedirect('/')   

    #Expulsions pendents:
    expulsionsPendentsTramitar = []
    for expulsio in professor.expulsio_set.exclude( tramitacio_finalitzada = True ):
        expulsionsPendentsTramitar.append( expulsio  )
        
    
    expulsionsPendentsPerAcumulacio = []
    
    #alumne -> incidencies i expulsions
    alumnes = {}
    for incidencia in professional.incidencia_set.all():
        alumne_str = unicode ( incidencia.alumne)
        fa_30_dies = date.today() - timedelta( days = 30 )
        incidenciesAlumne = incidencia.alumne.incidencia_set.filter(
                                                        professional = professional, 
                                                        es_vigent = True,
                                                        es_informativa = False,
                                                        dia_incidencia__gte = fa_30_dies
                                                                                   )
        calTramitarExpulsioPerAcumulacio = incidenciesAlumne.count() >= 3
        exempleIncidenciaPerAcumulacio = incidenciesAlumne.order_by( 'dia_incidencia' ).reverse()[0] \
                                            if calTramitarExpulsioPerAcumulacio \
                                            else None
        if calTramitarExpulsioPerAcumulacio and alumne_str not in alumnes:
            expulsionsPendentsPerAcumulacio.append( exempleIncidenciaPerAcumulacio )
        
        alumnes.setdefault( alumne_str, {
                    'calTramitarExpulsioPerAcumulacio': calTramitarExpulsioPerAcumulacio,     
                    'exempleIncidenciaPerAcumulacio': exempleIncidenciaPerAcumulacio,      
                    'alumne': incidencia.alumne, 
                    'incidencies': [], 
                    'expulsions': []}  )
        alumnes[alumne_str]['incidencies'].append( incidencia  )

    for expulsio in professor.expulsio_set.all():
        alumne_str = unicode ( expulsio.alumne)
        alumnes.setdefault( alumne_str, { 'alumne': expulsio.alumne, 'inicidencies': [], 'expulsions': []}  )
        alumnes[alumne_str]['expulsions'].append( expulsio  )

    alumnesOrdenats = []
    for alumneKey in sorted(alumnes.iterkeys()):
        tupla = (alumneKey, alumnes[alumneKey], )
        alumnesOrdenats.append( tupla  )

    return render_to_response(
                'incidenciesProfessional.html',
                {'alumnes': alumnesOrdenats,
                 'expulsionsPendentsTramitar': expulsionsPendentsTramitar,
                 'expulsionsPendentsPerAcumulacio': expulsionsPendentsPerAcumulacio,
                 'head': u'Incidències recullides per '+ nomProfessional ,
                },
                context_instance=RequestContext(request))        


@login_required
@group_required(['direcció'])
def alertesAcumulacioExpulsions( request ):
    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor( user )     


    sql = u'''select 
                   a.id_alumne, 
                   count( distinct e.id_expulsio ) as nExpulsions,
                   count( distinct ia.id_incidencia ) as nIncidenciesAula,  
                   count( distinct ifa.id_incidencia ) as nIncidenciesForaAula
                from 
                   alumne a 
                         left outer join 
                   expulsio e on 
                      e.id_alumne = a.id_alumne and
                      e.es_vigent = 1 and
                      e.estat not in ('ES')
                         left outer join
                   incidencia ia on 
                      ia.id_control_assistencia is not null and
                      ia.es_informativa = 0 and
                      ia.es_vigent = 1 and
                      ia.id_alumne = a.id_alumne 
                         left outer join
                   incidencia ifa on 
                      ifa.id_control_assistencia is null and
                      ifa.es_informativa = 0 and
                      ifa.es_vigent = 1 and
                      ifa.id_alumne = a.id_alumne
                group by 
                   id_alumne
                having
                   count( distinct e.id_expulsio ) > 0 or
                   count( distinct ifa.id_incidencia ) > 0  or
                   count( distinct ia.id_incidencia ) > 0  
                order by
                   count( distinct e.id_expulsio ) * 3 + count( distinct ifa.id_incidencia ) desc,
                   count( distinct ia.id_incidencia ) desc   
                '''

    report = []

    taula = tools.classebuida()
    
    taula.titol = tools.classebuida()
    taula.titol.contingut = ""
    
    capcelera_nom = tools.classebuida()
    capcelera_nom.amplade = 250
    capcelera_nom.contingut = u'Ranking expulsions i incidències'

    capcelera_nIncidencies = tools.classebuida()
    capcelera_nIncidencies.amplade = 120
    capcelera_nIncidencies.contingut = u'Exp-Inc.fa-Inc'

    capcelera_clic = tools.classebuida()
    capcelera_clic.amplade = 100
    capcelera_clic.contingut = u'Expulsar del centre.'


    taula.capceleres = [capcelera_nom, capcelera_nIncidencies, capcelera_clic]

    taula.fileres = []
    
    alumnesAmbExpulsions = ( 
                            Expulsio
                           .objects
                           .filter( es_vigent = True )
                           .exclude( estat = 'ES' )
                           .order_by('alumne__id')
                           .values_list( 'alumne__id', flat = True )
                          )
    
    alumnesAmbIncidenciesAula = ( 
                            Incidencia
                           .objects
                           .filter( es_vigent = True, es_informativa = False, control_assistencia__isnull = False )
                           .order_by( 'alumne__id' )
                           .values_list( 'alumne__id', flat = True )
                          )
    
    
    alumnesAmbIncidenciesForaAula = ( 
                            Incidencia
                           .objects
                           .filter( es_vigent = True, es_informativa = False, control_assistencia__isnull = True )
                           .order_by( 'alumne__id' )
                           .values_list( 'alumne__id', flat = True )
                          )
    
    alumnesAmbExpulsions_dict = {}
    alumnesAmbIncidenciesAula_dict = {}
    alumnesAmbIncidenciesForaAula_dict = {}
    alumnes_ids = set()
    for x, g in groupby(alumnesAmbExpulsions, lambda x: x): 
        alumnes_ids.add( x ) 
        alumnesAmbExpulsions_dict[x] = len( list(g) )
        
        
    for x, g in groupby(alumnesAmbIncidenciesAula, lambda x: x): 
        alumnes_ids.add( x ) 
        alumnesAmbIncidenciesAula_dict[x] = len( list(g) )
        
        
    for x, g in groupby(alumnesAmbIncidenciesForaAula, lambda x: x): 
        alumnes_ids.add( x )
        alumnesAmbIncidenciesForaAula_dict[x] = len( list(g) )
        
    alumnes = []
    for alumne in  Alumne.objects.filter( id__in = alumnes_ids ):
        alumne.nExpulsions = alumnesAmbExpulsions_dict.get(alumne.id, 0 )
        alumne.nIncidenciesAula = alumnesAmbIncidenciesAula_dict.get(alumne.id, 0 )
        alumne.nIncidenciesForaAula = alumnesAmbIncidenciesForaAula_dict.get(alumne.id, 0 )
        alumnes.append(alumne)
        
    #for alumne in  Alumne.objects.raw( sql ): TODO
    for alumne in  sorted( alumnes, key = lambda a: a.nExpulsions * 3 + a.nIncidenciesAula + a.nIncidenciesForaAula, reverse=True ):
                
        filera = []
        
        #-nom--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = '/tutoria/detallTutoriaAlumne/{0}/all'.format(alumne.pk )
        camp.contingut = unicode(alumne) + ' (' + unicode(alumne.grup) + ')'
        filera.append(camp)
        
        #-incidències--------------------------------------------
        camp_nIncidencies = tools.classebuida()
        camp_nIncidencies.enllac = '/tutoria/detallTutoriaAlumne/{0}/incidencies'.format(alumne.pk )
#        incidenciesAula = alumne.incidencia_set.filter( 
#                                es_informativa = False,
#                                es_vigent = True,
#                                control_assistencia__isnull = False 
#                                ).count()
#        incidenciesForaAula = alumne.incidencia_set.filter( 
#                                es_informativa = False,
#                                es_vigent = True,
#                                control_assistencia__isnull = True 
#                                ).count()
#        expulsions = alumne.expulsio_set.filter(
#                                es_vigent = True 
#                                ).exclude(estat = 'ES').count()
        
        camp_nIncidencies.contingut = u'{0} - {1} - {2}'.format(  
                                                    alumne.nExpulsions, 
                                                    alumne.nIncidenciesForaAula,
                                                    alumne.nIncidenciesAula)
        filera.append(camp_nIncidencies)


        camp = tools.classebuida()
        camp.enllac = r'javascript:confirmAction("/incidencies/expulsioDelCentre/{0}", "Segur que vols expulsar a {1}?")'.format(alumne.pk, alumne ) 
        camp.contingut = u'expulsar ...'
        filera.append(camp)
        


        #--
        taula.fileres.append( filera )
    
    report.append(taula)
        
    return render_to_response(
                'report.html',
                    {'report': report,
                     'head': 'Informació alumnes' ,
                    },
                    context_instance=RequestContext(request))            


@login_required
@group_required(['direcció'])
def expulsioDelCentre( request, pk ):
    
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials    
    
    fa_30_dies = date.today() - timedelta( days = 30 )
    
    professor = User2Professor(user)
    
    alumne = Alumne.objects.get( pk = pk )
    alumne.incidencia_set.filter( dia_incidencia__lte = fa_30_dies).update( es_vigent = False )

    primeraFranja = FranjaHoraria.objects.all()[0]
    darreraFranja = FranjaHoraria.objects.reverse()[0]

    #expulsions:    
    expulsions = alumne.expulsio_set.filter(                                            
                            es_vigent = True 
                            ).exclude( estat = 'ES' )
                            
    str_expulsions = u', '.join( [  e.motiu_expulsio + u' ('+ unicode ( e.dia_expulsio.strftime( '%d/%m/%Y' )) + u')'
                                    for e in expulsions ] )
    str_expulsions = u'''Acumulació d'expulsions: {0}'''.format( str_expulsions ) if str_expulsions else ''

    #incidències
    incidencies = alumne.incidencia_set.filter( 
                        es_informativa = False,
                        es_vigent = True
                        )

    str_incidencies = u', '.join( [  i.descripcio_incidencia + u' ('+ unicode ( i.dia_incidencia.strftime( '%d/%m/%Y' )) + u')'
                                    for i in incidencies ] )
    str_incidencies = u'''Acumulació de incidències: {0}'''.format( str_incidencies ) if str_incidencies else '' 

    #expulsions + incidències        
    comentaris_cap_d_estudis = u' '.join( [ str_expulsions, str_incidencies ] )
    
    url_next = '/incidencies/alertesAcumulacioExpulsions/'  #si res falla torno a la llista
    try:
        expulsio_centre = ExpulsioDelCentre(
                         professor = User2Professor(user),
                         alumne = alumne,
                         motiu_expulsio = u'',
                         comentaris_cap_d_estudis= comentaris_cap_d_estudis,
                         data_inici = datetime.today(),
                         franja_inici = primeraFranja,
                         franja_fi = darreraFranja,
                         data_fi = datetime.today() + timedelta(days = 1)    ,
                         data_carta = datetime.today(),
                         signat = u'''Cap d'estudis'''
                    )
        expulsio_centre.save()
        
        #LOGGING
        Accio.objects.create( 
                tipus = 'EC',
                usuari = user,
                l4 = l4,
                impersonated_from = request.user if request.user != user else None,
                text = u"""Creada expulsió del centre de l'alumne {0}.""".format( expulsio_centre.alumne )
            )   

    except ValidationError, e:
        import itertools
        resultat = { 'errors': list( itertools.chain( *e.message_dict.values() ) ), 
                    'warnings':  [], 'infos':  [], 'url_next': url_next }
        return render_to_response(
                       'resultat.html', 
                       {'head': u'Error al crear expulsió per acumulació.' ,
                        'msgs': resultat },
                       context_instance=RequestContext(request))
    else:
        #assigno les expulsions a aquesta expulsió  
        expulsions.update( es_vigent = False, provoca_expulsio_centre = expulsio_centre )

        #assigno les incidències a aquesta expulsió
        if incidencies.count()  > 0:
            incidencies.update( es_vigent = False, provoca_expulsio_centre = expulsio_centre )
        
        url_next = '/incidencies/editaExpulsioCentre/{0}'.format(expulsio_centre.pk) 

    return HttpResponseRedirect( url_next )         

#--------------------------------------------------------------------------------------------------

@login_required
@group_required(['direcció'])
def expulsionsDelCentre( request, s = 'nom' ):
    report = []
        
    ordenacions = {'nom':['alumne__cognoms','data_inici',], 'data':['data_inici','alumne__cognoms',], }
    ordenacio = ordenacions[s] if s in ordenacions else []
    taula = tools.classebuida()
    
    taula.titol = tools.classebuida()
    taula.titol.contingut = u'Expulsions del Centre'
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 120
    capcelera.contingut = u'Alumne'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'Obre Expedient'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'Periode expulsió'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'Data Carta'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'Expulsions Relacionades'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'Incidències Relacionades'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'Accions'
    taula.capceleres.append( capcelera )

    taula.fileres = []
    
    expulsions = ExpulsioDelCentre.objects.order_by(*ordenacio)
    
    for expulsio in  expulsions:
                
        filera = []
        
        #-nom--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = ''
        camp.contingut = unicode(expulsio.alumne) + ' (' + unicode(expulsio.alumne.grup) + ')'
        filera.append(camp)
        
        #-obre expedient--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = ''
        camp.contingut = u'Sí' if expulsio.obra_expedient else u'No'
        filera.append(camp)

        #-periode--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = u'{0} a {1}'.format( 
                                expulsio.data_inici.strftime( '%d/%m/%Y' ), 
                                expulsio.data_fi.strftime( '%d/%m/%Y' ) ) 
        filera.append(camp)

        #-data carta--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = u'{0}{1}'.format( 
                    expulsio.data_carta.strftime( '%d/%m/%Y' ) if expulsio.data_carta else '',
                    u' (impresa)' if expulsio.impres else '' )

        filera.append(camp)
        
        #-Expulsions relacionades--------------------------------------------
        camp = tools.classebuida()
        camp.multipleContingut = [  ( e.dia_expulsio.strftime( '%d/%m/%Y' ),
                                     '/incidencies/editaExpulsio/{0}'.format(e.pk),
                                     )
                                  for e in expulsio.expulsio_set.exclude(estat = 'ES' ) ]
        filera.append(camp)
        
        #-Incidencies relacionades--------------------------------------------
        camp = tools.classebuida()
        camp.multipleContingut = [  ( u'{0} ({1})'.format(
                                                i.dia_incidencia.strftime( '%d/%m/%Y' ),
                                                i.descripcio_incidencia ),
                                     '',
                                     )
                                  for i in expulsio.incidencia_set.all() ]
        filera.append(camp)

        #-Incidencies relacionades--------------------------------------------
        camp = tools.classebuida()
        camp.esMenu = True
        camp.multipleContingut = [( u'Editar',
                                   u'/incidencies/editaExpulsioCentre/{0}'.format( expulsio.pk )
                                  ),
                                  ( u'Carta',
                                    '/incidencies/cartaExpulsioCentre/{0}'.format(expulsio.pk),
                                  ),
                                  ( u'Esborrar',
                                    r'''javascript:confirmAction("/incidencies/esborrarExpulsioCentre/{0}", "Segur que vols esborrar l'expulsió de {1}?")'''.format(expulsio.pk, expulsio.alumne )
                                  ),                                  
                                 ]
        filera.append(camp)

        
        taula.fileres.append( filera )

    report.append(taula)

    return render_to_response(
                'expulsionsDelCentre.html',
                    {'report': report,
                     'head': 'Informació Expulsions del Centre' ,
                    },
                    context_instance=RequestContext(request))  



@login_required
@group_required(['direcció'])
def expulsionsDelCentreExcel( request ):
    """
    Generates an Excel spreadsheet for review by a staff member.
    """
    expulsions = ExpulsioDelCentre.objects.order_by('data_inici','alumne__cognoms')
    
    dades_expulsions = [
                        [e.alumne,
                         e.data_inici.strftime( '%d/%m/%Y' ),
                         e.data_fi.strftime( '%d/%m/%Y' ),
                         u'Sí' if e.impres else 'No',
                         e.alumne.grup.descripcio_grup,
                         e.alumne.grup.curs.nivell ]
                        for e in expulsions]
    
    capcelera = [ u'Alumne', u'Data inici', u'Data fi', u'Ha estat imprés', u'grup', u'nivell' ]

    response = render_to_response(
                        "excel_table.html", 
                        {
                         'capcelera':capcelera,
                         'dades':dades_expulsions,
                        },
                        context_instance=RequestContext(request))
    filename = "expulsions.xls" 
    response['Content-Disposition'] = 'attachment; filename='+filename
    response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'

    return response




@login_required
@group_required(['direcció'])
def cartaExpulsioCentre( request, pk ):

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    expulsio = ExpulsioDelCentre.objects.get( pk = pk)
    
    #seg---------
    pot_entrar = True or l4 or expulsio.professor.pk == user.pk 
    if not pot_entrar:
        raise Http404() 
    
    expulsio.credentials = credentials
    
    #capcelera
    report = tools.classebuida()
    report.nom_alumne = unicode(expulsio.alumne)
    report.dies_expulsio = u" del {0} al {1}".format( 
                                        expulsio.data_inici.strftime( '%d/%m/%Y' ), 
                                        expulsio.data_fi.strftime( '%d/%m/%Y' ), 
                                        )
    report.motiu_expulsio = expulsio.motiu_expulsio
    report.signat_per = expulsio.signat
    report.data_signatura = expulsio.data_carta.strftime( '%d/%m/%Y' )
    report.expulsions = []
    report.incidencies = []
    #detall
    for e in expulsio.expulsio_set.exclude(estat = 'ES'):
        rpt_e = tools.classebuida()
        rpt_e.dia = e.dia_expulsio.strftime( '%d/%m/%Y' )
        rpt_e.professor = u'Sr/a: {0}'.format( e.professor )
        rpt_e.comunicacio = u'{0} - {1}'.format( 
                            e.moment_comunicacio_a_tutors.strftime( '%d/%m/%Y' ),
                            e.tutor_contactat_per_l_expulsio
                        ) if e.moment_comunicacio_a_tutors else u''
        rpt_e.motiu = e.motiu_expulsio
        report.expulsions.append(rpt_e)

    for i in expulsio.incidencia_set.all():
        rpt_i = tools.classebuida()
        rpt_i.data = i.dia_incidencia.strftime( '%d/%m/%Y' )
        rpt_i.professor = u'Sr/a: {0}'.format( i.professional )
        assignatura = u''''(fora d'aula')'''
        try:
            assignatura = i.control_assistencia.impartir.horari.assignatura
        except:
            pass
        rpt_i.assignatura = u'{0}'.format( assignatura ) 
                                 
        rpt_i.descripcio = i.descripcio_incidencia
        report.incidencies.append(rpt_i)
    
    
    #from django.template import Context                              
    from appy.pod.renderer import Renderer
    import cgi
    import os
    from django import http
    import time
    
    excepcio = None
    contingut = None
    try:
        
        #resultat = StringIO.StringIO( )
        resultat = "/tmp/DjangoAula-temp-{0}-{1}.odt".format( time.time(), request.session.session_key )
        #context = Context( {'reports' : reports, } )
        path = None
        try:
            path = os.path.join( settings.PROJECT_DIR,  '../customising/docs/cartaExpulsioCentre.odt' )
        except: 
            path = os.path.join(os.path.dirname(__file__), 'templates/cartaExpulsioCentre.odt')

        renderer = Renderer(path, {'report' :report, }, resultat)  
        renderer.run()
        docFile = open(resultat, 'rb')
        contingut = docFile.read()
        docFile.close()
        os.remove(resultat)
        
    except Exception, e:
        excepcio = unicode( e )
        
    if not excepcio:
        expulsio.impres = True
        expulsio.save()
        response = http.HttpResponse( contingut, mimetype='application/vnd.oasis.opendocument.text')
        response['Content-Disposition'] = u'attachment; filename="cartaExpulsioCentre-{0}.odt"'.format( slugify( unicode(expulsio.alumne ) ) )
                                                     
    else:
        response = http.HttpResponse('''Als Gremlin no els ha agradat aquest fitxer! %s''' % cgi.escape(excepcio))
    
    return response



@login_required
@group_required(['direcció'])
def editaExpulsioCentre( request, pk ):
    
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    expulsio = ExpulsioDelCentre.objects.get( pk = pk)
    
    #seg---------
    pot_entrar = l4 or user.groups.filter( name= 'direcció').exists()
    if not pot_entrar:
        raise Http404() 
    
    expulsio.credentials = credentials
    
    edatAlumne = None
    try:
        edatAlumne = (date.today() - expulsio.alumne.data_neixement).days / 365 
    except:
        pass
    
    infoForm = [
          ('Alumne',unicode( expulsio.alumne) ),
          ( 'Telèfon Alumne', expulsio.alumne.telefons),                     
          ( 'Nom tutors', expulsio.alumne.tutors),                     
          ( 'Edat alumne', edatAlumne ),                     
          ( 'Carta impresa (expulsió bloquejada)', expulsio.impres ),                     
                ]
    
    fields = [ 'data_inici', 
              'franja_inici', 
              'data_fi',
              'franja_fi',
              'data_carta',
              'motiu_expulsio',
              'obra_expedient',
              'comentaris_cap_d_estudis' ,
              'signat' ]
    if l4:
        fields.extend( [ 'professor', 'impres'] )

    editaExpulsioFormF = modelform_factory( ExpulsioDelCentre, fields = fields )
    try:
        editaExpulsioFormF.base_fields['data_inici'].widget =  DateTextImput()
        editaExpulsioFormF.base_fields['data_fi'].widget =  DateTextImput()
        editaExpulsioFormF.base_fields['data_carta'].widget =  DateTextImput()
    except:
        pass
    
    if request.method == 'POST':
       
        formExpulsio = editaExpulsioFormF(data = request.POST, instance = expulsio )
        can_delete = ckbxForm( data=request.POST, label = 'Esborrar expulsió', 
                             help_text=u'''Marca aquesta cassella per esborrar aquesta expulsió''' )
        formSelectIncidencies = incidenciesRelacionadesForm( data=request.POST,
                                                             querysetIncidencies = expulsio.incidencia_set.all(),
                                                             querysetExpulsions  = expulsio.expulsio_set.all()    )
        if formExpulsio.is_valid() and can_delete.is_valid() and formSelectIncidencies.is_valid():
            if can_delete.cleaned_data['ckbx'] and l4:
                expulsio.delete()
            else:
                formExpulsio.save()

                fa_30_dies = date.today() - timedelta( days = 30 )
                fa_60_dies = date.today() - timedelta( days = 60 )                
                                
                incidencies = formSelectIncidencies.cleaned_data['incidenciesRelacionades']
                incidencies_a_desvincular = expulsio.incidencia_set.exclude( pk__in = [ i.pk for i in incidencies ] )
                incidencies_a_desvincular.filter( dia_incidencia__gte = fa_30_dies).update( es_vigent = True  )
                incidencies_a_desvincular.update(  provoca_expulsio_centre = None )  

                expulsions = formSelectIncidencies.cleaned_data['expulsionsRelacionades']
                expulsions_a_desvincular = expulsio.expulsio_set.exclude( pk__in = [ i.pk for i in expulsions ] )
                expulsions_a_desvincular.filter( dia_expulsio__gte = fa_60_dies).update( es_vigent = True  )
                expulsions_a_desvincular.update(  provoca_expulsio_centre = None )  
                
            url = '/incidencies/expulsionsDelCentre/'
            return HttpResponseRedirect( url )
        
    else:
        formExpulsio = editaExpulsioFormF( instance = expulsio )
        can_delete = ckbxForm( data=request.POST, label = 'Esborrar expulsió:', 
                             help_text=u'''Marca aquesta cassella per esborrar aquesta expulsió''' )
        formSelectIncidencies = incidenciesRelacionadesForm( querysetIncidencies = expulsio.incidencia_set.all(),
                                                             querysetExpulsions  = expulsio.expulsio_set.all() )

    formset = [ formExpulsio, formSelectIncidencies ]
    formset.extend ( [  can_delete ] if l4 else []  )
    

    return render_to_response(
                'formset.html',
                    {'formset': formset,
                     'infoForm': infoForm,
                     'head': 'Expulsió' ,
                    },
                    context_instance=RequestContext(request))    

#--------------------------------------------------------------------------------------------------



login_required
@group_required(['direcció'])
def esborrarExpulsioCentre( request, pk ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    expulsio = ExpulsioDelCentre.objects.get( pk = pk)
    
    #seg---------
    pot_entrar = l4 or user.groups.filter( name= 'direcció').exists()
    if not pot_entrar:
        raise Http404() 
    
    if not l4 and expulsio.impres:
        return render_to_response(
                    'resultat.html', 
                    {'head': u'Error esborrant expulsió del centre' ,
                     'msgs': { 'errors': [u'Aquesta expulsió del centre ja ha estat impresa, no es pot esborrar'], 
                               'warnings':  [], 
                               'infos':  [],
                               'url_next':'/incidencies/expulsionsDelCentre/'} ,
                     },
                    context_instance=RequestContext(request)) 
    
    expulsio.credentials = credentials
    
    fa_30_dies = date.today() - timedelta( days = 30 )
    fa_60_dies = date.today() - timedelta( days = 60 )

    expulsio.incidencia_set.filter( dia_incidencia__gte = fa_30_dies).update( es_vigent = True  )
    expulsio.incidencia_set.update(  provoca_expulsio_centre = None )    

    expulsio.expulsio_set.filter( dia_expulsio__gte = fa_60_dies).update( es_vigent = True  )
    expulsio.expulsio_set.update(  provoca_expulsio_centre = None )    
    
    expulsio.delete()

    url = '/incidencies/expulsionsDelCentre/'
    return HttpResponseRedirect( url )    





#---------------------  --------------------------------------------#

    
@login_required
@group_required(['professors'])
def blanc( request ):
    return render_to_response(
                'blanc.html',
                    {},
                    context_instance=RequestContext(request)) 






#------No esborrar: com afegir errors a mà en un formulari a partir dels ValidationsError:
#                try:
#                    incidencia.save()
#                    Incidencia_despres_de_posar( incidencia )
#                    url = '/incidencies/llistaIncidenciesProfessional'  #todo: a la pantalla d''incidencies
#                    return HttpResponseRedirect( url )    
#                except ValidationError, e:
#                    #Com que no és un formulari de model cal tractar a mà les incidències del save:
#                    for _, v in e.message_dict.items():
#                        formIncidencia._errors.setdefault(NON_FIELD_ERRORS, []).extend(  v  )
