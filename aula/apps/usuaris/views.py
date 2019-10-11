# This Python file uses the following encoding: utf-8

#templates
from django.template import RequestContext
from django_tables2 import RequestConfig
from django.urls import reverse

from aula.apps.usuaris.forms import CanviDadesUsuari, triaUsuariForm, loginUsuariForm, \
    recuperacioDePasswdForm, sendPasswdByEmailForm, canviDePasswdForm, triaProfessorSelect2Form

from django.contrib.auth.decorators import login_required

from aula.apps.usuaris.tables2_models import HorariProfessorTable
from aula.utils.decorators import group_required

from aula.apps.extKronowin.models import ParametreKronowin

#workflow
from django.http import HttpResponseRedirect
from django.shortcuts import  get_object_or_404, render

#helpers
from django.http import HttpResponseNotFound, HttpResponse

from aula.utils import tools
from aula.utils.tools import unicode
from aula.utils.forms import ckbxForm
from aula.apps.usuaris.models import Professor, LoginUsuari, AlumneUser, OneTimePasswd,\
    Accio
from django.utils.datetime_safe import datetime
from datetime import timedelta
from django.db.models import Q

from django.contrib.auth import authenticate, login
from django.forms.forms import NON_FIELD_ERRORS
from django.contrib.auth.models import User
from aula.apps.usuaris.tools import enviaOneTimePasswd
from aula.apps.usuaris.models import User2Professor, GetDadesAddicionalsProfessor, DadesAddicionalsProfessor
from aula.utils.tools import getClientAdress

from django.contrib import messages
from django.conf import settings

#-- ical:
from aula.apps.presencia.models import Impartir
from aula.apps.sortides.models import Sortida
from icalendar import Calendar, Event
from icalendar import vCalAddress, vText
from django.templatetags.tz import localtime

@login_required
def canviDadesUsuari( request):
    credentials = tools.getImpersonateUser(request) 
    (user, _) = credentials
        
    if request.method == "POST":
        form=CanviDadesUsuari(
                                request.POST,                                
                                instance= user )
        form.fields['first_name'].label = 'Nom'
        form.fields['last_name'].label = 'Cognoms'
        if form.is_valid():
            form.save()
            return HttpResponseRedirect( '/' )
    else:
        form=CanviDadesUsuari(instance=user)
        form.fields['first_name'].label = 'Nom'
        form.fields['last_name'].label = 'Cognoms'

    head = u'''Dades d'usuari'''
    infoForm = [ (u'Codi Usuari', user.username), ]      
          
    resposta = render(
                request,
                  "form.html", 
                  {"form": form,
                   "head": head,
                   'infoForm': infoForm,
                   }
                )
    
    return resposta

#--------------------------------------------------------------------

@login_required
@group_required(['direcció'])
def resetPasswd(request):
    head=u'Impersonar-se' 

    url_next = '/'  
    if request.method == 'POST':
        form = triaUsuariForm(request.POST)
        form.fields['professor'].required = True
        
        if form.is_valid():            
            usuari = form.cleaned_data['professor']

            defaultPasswd, _ = ParametreKronowin.objects.get_or_create( nom_parametre = 'passwd', defaults={'valor_parametre':'1234'}  )
            passwd = defaultPasswd.valor_parametre
            usuari.set_password( passwd )
            usuari.is_active = True
            usuari.save()
            messages.add_message(request, messages.INFO, u"Canviat el Pass de {usuari}({username}), nou passwd és [{passwd}]".format( usuari = usuari, passwd = passwd, username = usuari.username) )
            return HttpResponseRedirect( url_next )
            
    else:
        form = triaUsuariForm()
    
    return render(
                request,
                'form.html', 
                {'form': form, 
                 'head': head}
                )
#--------------------------------------------------------------------

@login_required
@group_required(['direcció'])
def impersonacio(request):
            
    head=u'Impersonar-se' 

    url_next = '/'  
    if request.method == 'POST':
        form = triaUsuariForm(request.POST)
        form.fields['professor'].required = False
        formckbx = ckbxForm( data=request.POST, label = u'Accés de nivell 4(UAT)', 
                             help_text=u'''Marca aquesta cassella per realitzar les operacions
                                         sense les restriccions habituals''' )
        
        if form.is_valid() and formckbx.is_valid():            
            try:
                del request.session['impersonacio']
                del request.session['l4']
            except:
                pass
            if form.cleaned_data['professor']:
                request.session['impersonacio'] = form.cleaned_data['professor'].getUser()
            l4 = formckbx.cleaned_data['ckbx']
            request.session['l4'] = l4
            return HttpResponseRedirect( url_next )
    else:
        form = triaUsuariForm()
        
        formckbx = ckbxForm( label = u'Accés de nivell 4(UAT)', 
                             help_text=u'''Marca aquesta cassella per realitzar les operacions
                                         sense les restriccions habituals''' )
        formckbx.fields['ckbx' ].initial = request.session.has_key('l4') and request.session['l4'] 
    formset = [form, formckbx]
    return render(
                request,
                'formset.html', 
                {'formset': formset, 
                 'head': head}
                )
    
@login_required
@group_required(['direcció'])
def resetImpersonacio(request):
    try:
        del request.session['impersonacio']
        del request.session['l4']
    except:
        pass
    
    url_next = '/'
    return HttpResponseRedirect( url_next )


#--------------------------------------
    
@login_required
@group_required(['direcció'])
def elsProfessors( request ):

    (user, l4) = tools.getImpersonateUser(request)    
    
    report = []
    
    taula = tools.classebuida()
    
    taula.capceleres = []
    
    taula.titol = tools.classebuida()
    taula.titol.contingut = ""
    
    capcelera = tools.classebuida()
    capcelera.amplade = 40
    capcelera.contingut = u'Professor'
    taula.capceleres.append( capcelera )
    
    capcelera = tools.classebuida()
    capcelera.amplade = 60
    capcelera.contingut = u'%Passa llista'
    taula.capceleres.append( capcelera )
       
    taula.fileres = []
    for professor in  Professor.objects.all():
        
        filera = []
        
        #-nom--------------------------------------------
        camp_nom = tools.classebuida()
        camp_nom.enllac = None
        camp_nom.contingut = unicode(professor)
        filera.append(camp_nom)
        
        #-incidències--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        qProfessor = Q(  horari__professor = professor )
       
        qAvui = Q( dia_impartir = datetime.today() ) & Q( horari__hora__hora_fi__lt = datetime.now()  )
        qFinsAhir = Q( dia_impartir__lt = datetime.today() )
        qFinsAra  = qFinsAhir | qAvui
        qTeGrup = Q( horari__grup__isnull = False)
        imparticions = ( Impartir
                         .objects
                         .filter(qProfessor & qFinsAra & qTeGrup )
                         .exclude( pot_no_tenir_alumnes = True)
                        )
        nImparticios = ( imparticions
                         .values_list( 'dia_impartir', 'horari__dia_de_la_setmana_id','horari__hora_id' )
                         .distinct()
                         .count()
                        )
        nImparticionsLlistaPassada = ( imparticions
                                       .filter( professor_passa_llista__isnull = False )
                                       .values_list( 'dia_impartir', 'horari__dia_de_la_setmana_id','horari__hora_id' )
                                       .distinct()
                                       .count()
                                     )
        pct = nImparticionsLlistaPassada * 100 / nImparticios if nImparticios > 0 else 0
        camp.contingut = u'{0:.0f}% ({1} classes impartides, {2} controls)'.format( pct, nImparticios, nImparticionsLlistaPassada)
        camp.codi_ordenacio = pct
        filera.append(camp)


        #--
        taula.fileres.append( filera )
        
    
    #fileres_ordenades = sorted( taula.fileres, key = lambda x: x.codi_ordenacio )    
    #taula.fileres = fileres_ordenades
    
    report.append(taula)
        
    return render(
                request,
                'report.html',
                    {'report': report,
                     'head': 'Informació professors' ,
                    }
                )
        

def loginUser( request ):
    head=u'Login' 

    client_address = getClientAdress( request )
    
    try:
        acces_restringit_a_grups = settings.ACCES_RESTRINGIT_A_GRUPS
    except AttributeError:
        acces_restringit_a_grups = None

    url_next = '/'  
    if request.method == 'POST':
        form = loginUsuariForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['usuari']
            paraulaDePas=form.cleaned_data['paraulaDePas']
            user = authenticate(username=username, password=paraulaDePas)
            if user is not None:
                #Usuari i passwd estan bé
                if acces_restringit_a_grups and not user.groups.filter( name__in = acces_restringit_a_grups ).exists():
                    LoginUsuari.objects.create( usuari = user, exitos = False, ip = client_address)   #TODO: truncar IP
                    form._errors.setdefault(NON_FIELD_ERRORS, []).append(  u'''El sistema està en mode restringit.'''  )
                else:
                    if user.is_active:
                        login(request, user)
                        LoginUsuari.objects.create( usuari = user, exitos = True, ip = client_address)   #TODO: truncar IP
                        return HttpResponseRedirect( url_next )
                    else:
                        LoginUsuari.objects.create( usuari = user, exitos = False, ip = client_address)   #TODO: truncar IP
                        form._errors.setdefault(NON_FIELD_ERRORS, []).append(  u'''Aquest compte està desactivat. Punxa a l'enllaç de recuperar contrasenya.'''  )
            else:
                #Error d'usuari i passwd
                try:
                    user = User.objects.get( username = username )
                    
                    #apunto el fallo:
                    LoginUsuari.objects.create( usuari = user, exitos = False, ip = client_address)                    
                    if user.is_active:
                        #comprova 3 intents fallits des del darrer intent bó.
                        #fa_5_minuts = datetime.now() - timedelta(minutes = 5)
                        logins_anteriors = LoginUsuari.objects.filter( 
                                                usuari = user 
                                                #,moment__gte = fa_5_minuts 
                                                                      ).order_by( '-moment' )[:3]                                                     
                        tresFallos = logins_anteriors.count() == 3 and all( not x.exitos for x in logins_anteriors ) 
                        if tresFallos and user.is_active:
                            user.is_active = False
                            user.save()
                            #no aviso per no donar pistes de que això sigui un usuari real.                    
                            try:
                                #si és un alumne ho haig d'apuntar al seu model:
                                alumne = AlumneUser.objects.get(pk = user.pk  )
                                alumne.motiu_bloqueig = u'Error reiterat entrant la contrasenya.'
                                alumne.save()
                            except:
                                pass
                            
                except:
                    pass

                form._errors.setdefault(NON_FIELD_ERRORS, []).append(  u'Usuari o paraula de pas incorrecte'  )
    else:
        form = loginUsuariForm()


    return render(
                request,
                'loginForm.html',
                    {'form': form,
                     'head': head ,
                     'acces_restringit_a_grups': acces_restringit_a_grups,
                    }
                    )

@login_required
def canviDePasswd( request ):     
    
    (user, _) = tools.getImpersonateUser(request)
      
    infoForm = [ ('Usuari',user.username,),]
    if request.method == 'POST':
        form = canviDePasswdForm(  request.POST  )

        if form.is_valid(  ):         
            passwdOLD = form.cleaned_data['p0']               
            passwdNEW = form.cleaned_data['p1']               
          

            userOK = authenticate(username=user.username, password=passwdOLD)

            if userOK is not None:              
                user.set_password( passwdNEW )
                user.save()

                url_next = '/' 
                return HttpResponseRedirect( url_next )        
            else:
                form._errors.setdefault(NON_FIELD_ERRORS, []).append( u'Comprova que la paraula de pas actual proporcionada sigui la correcta.' )

    else:
        form = canviDePasswdForm(   )
        
    return render(
                request,
                'form.html',
                    {'form': form,
                     'infoForm':infoForm,
                     'head': u'Canvi de Contrasenya' 
                     }
                    )

def recoverPasswd( request , username, oneTimePasswd ):     
    #AlumneUser.objects.get( username = username)
    if Professor.objects.filter( username = username ).count() > 0:
        return professorRecoverPasswd( request , username, oneTimePasswd )
    return alumneRecoverPasswd( request , username, oneTimePasswd )

def alumneRecoverPasswd( request , username, oneTimePasswd ):     
    
    client_address = getClientAdress( request )

    infoForm = [ ('Usuari',username,),]
    if request.method == 'POST':
        form = recuperacioDePasswdForm(  request.POST  )
        errors = []
        if form.is_valid(  ):         
            passwd = form.cleaned_data['p1']               
            data_neixement = form.cleaned_data['data_neixement']
            
            alumneOK = True
            try:
                alumneUser =  AlumneUser.objects.get( username = username)
                dataOK = data_neixement == alumneUser.getAlumne().data_neixement
                a_temps = datetime.now() - timedelta( minutes = 30 )
                codiOK = OneTimePasswd.objects.filter( usuari = alumneUser.getUser(), 
                                                                  clau = oneTimePasswd, 
                                                                  moment_expedicio__gte = a_temps,
                                                                  reintents__lt = 3 )
            except AlumneUser.DoesNotExist:
                alumneOK = False
            except  AttributeError:
                alumneOK = False
                
            if not alumneOK:
                errors.append( u'Dades incorrectes. Demaneu un altre codi de recuperació. Si el problema persisteix parleu amb el tutor.')
            elif codiOK and not dataOK:
                errors.append( u'La data proporcionada no és correcta.')
                codiOK[0].reintents += 1
                codiOK[0].save()
            elif dataOK and not codiOK:
                errors.append( u"L'enllaç que esteu utilitzant està caducat o no és correcta. Demaneu un altre codi de recuperació.")
            elif not dataOK and not codiOK:
                errors.append( u"Dades incorrectes. Demaneu un altre codi de recuperació.")                
                #todoBloquejar oneTimePasswd
            elif alumneUser.alumne.esBaixa():
                errors.append( u'Cal parlar amb el tutor per recuperar accés a aquest compte.')
            elif codiOK and dataOK and not alumneUser.alumne.esBaixa():                
                alumneUser.set_password( passwd )
                alumneUser.is_active = True
                alumneUser.save()
                if alumneUser.alumne.motiu_bloqueig:
                    alumneUser.alumne.motiu_bloqueig = u""
                    alumneUser.alumne.save()
                user = authenticate(username=alumneUser.username, password=passwd)
                login( request, user )
 

            if not errors:
                codiOK.update( reintents = 3 )

                #apunto el login:
                LoginUsuari.objects.create( usuari = user, exitos = True, ip = client_address) 
                                
                url_next = '/' 
                return HttpResponseRedirect( url_next )        
            else:
                try:
                    #apunto el login:
                    LoginUsuari.objects.create( usuari = alumneUser, exitos = False, ip = client_address) 
                except:
                    pass
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  errors  )    

    else:
        form = recuperacioDePasswdForm(   )
        
    return render(
                request,
                'form.html',
                    {'form': form,
                     'infoForm':infoForm,
                     'head': u'Recuperació de Contrasenya' 
                     }
                )


def professorRecoverPasswd( request , username, oneTimePasswd ):     
    
    infoForm = [ ('Usuari',username,),]
    if request.method == 'POST':
        form = recuperacioDePasswdForm(  request.POST  )
        del form.fields['data_neixement']
        errors = []
        if form.is_valid(  ):         
            passwd = form.cleaned_data['p1']                           

            professor =  Professor.objects.get( username = username)            
            a_temps = datetime.now() - timedelta( minutes = 30 )
            codiOK = OneTimePasswd.objects.filter( usuari = professor.getUser(), 
                                                              clau = oneTimePasswd, 
                                                              moment_expedicio__gte = a_temps,
                                                              reintents__lt = 3 )

            if not codiOK:
                errors.append( u"Dades incorrectes. Demaneu un altre codi de recuperació.")                
                #todoBloquejar oneTimePasswd
            elif codiOK:                
                professor.set_password( passwd )
                professor.is_active = True
                professor.save()
                user = authenticate(username=professor.username, password=passwd)
                login( request, user )

            if not errors:
                codiOK.update( reintents = 3 )
                url_next = '/' 
                return HttpResponseRedirect( url_next )        
            else:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  errors  )    

    else:
        form = recuperacioDePasswdForm(   )
        del form.fields['data_neixement']
        
    return render(
                request,
                'form.html',
                    {'form': form,
                     'infoForm':infoForm,
                     'head': u'Recuperació de Contrasenya' 
                     }
                )

def sendPasswdByEmail( request ):
    
    if request.method == 'POST':
        form = sendPasswdByEmailForm(request.POST, initial={'captcha': request.META['REMOTE_ADDR']})
        if form.is_valid():
            resultat = enviaOneTimePasswd( form.cleaned_data['email'] )
            resultat['url_next'] = '/'

            return render(
                        request,
                        'resultat.html',
                            {'msgs': resultat ,
                             'head': 'Recuperació de contrasenya',
                            }
                        )
                    
    else:
        form = sendPasswdByEmailForm(  )
        
    return render(
        request,
        'form.html',
            {'form': form,
             'head': u'Recuperació de Contrasenya'
             }
        )


@login_required
@group_required(['consergeria','professors','professional'])
def cercaProfessor(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    if request.method == 'POST':
        formUsuari = triaProfessorSelect2Form(request.POST)  # todo: multiple=True (multiples profes de cop)
        if formUsuari.is_valid():
            professor = formUsuari.cleaned_data['professor']
            next_url = r'/usuaris/detallProfessorHorari/{0}/all/'
            return HttpResponseRedirect(next_url.format(professor.pk))

    else:
        formUsuari = triaProfessorSelect2Form()
    return render(
        request,
        'form.html',
        {'form': formUsuari,
         'head': 'Triar usuari'
         }
        )

@login_required
@group_required(['professors','professional'])
def integraCalendari(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials
    professor =  User2Professor(user)
    dades_addicionals = GetDadesAddicionalsProfessor(professor)
    url = r"{0}{1}".format( settings.URL_DJANGO_AULA, reverse( 'gestio__calendari__comparteix', kwargs={'clau': str( dades_addicionals.clauDeCalendari) } ) )    
    return render(
        request,
        'integraCalendari.html',
        {
         'url_calendari': url,
         }
        )    

def comparteixCalendari(request, clau):
    cal = Calendar()
    cal.add('method','PUBLISH' ) # IE/Outlook needs this

    try:
        dades_adicionals_professor = DadesAddicionalsProfessor.objects.get( clauDeCalendari = clau )
        professor = dades_adicionals_professor.professor
    except:
        return HttpResponseNotFound("")         
    else:

        #-- imparticions
        imparticions = list(
            Impartir
            .objects
            .filter( horari__professor = professor  )
            .select_related("reserva")
            .select_related("reserva__aula")
            .select_related("horari")
            .select_related("horari__hora")
            .select_related("horari__assignatura")
        )

        for instance in imparticions:
            event = Event()

            assignatura = instance.horari.assignatura.nom_assignatura
            aula = instance.reserva.aula.nom_aula if hasattr(instance,"reserva") and instance.reserva is not None else ""
            grup = instance.horari.grup.descripcio_grup if hasattr(instance.horari, "grup") and instance.horari.grup is not None else ""

            summary = u"{assignatura} {aula} {grup}".format(
                assignatura=assignatura ,
                aula = aula,
                grup = grup,
                )
            d = instance.dia_impartir
            h = instance.horari.hora
            event.add('dtstart',localtime( datetime( d.year, d.month, d.day, h.hora_inici.hour, h.hora_inici.minute, h.hora_inici.second ) ) )
            event.add('dtend' ,localtime( datetime( d.year, d.month, d.day, h.hora_fi.hour, h.hora_fi.minute, h.hora_fi.second ) ) )
            event.add('summary',summary)
            event.add('uid', 'djau-ical-impartir-{0}'.format( instance.id ) )
            event['location'] = vText( aula )
            
            cal.add_component(event)

        #-- sortides
        q_professor = Q( professor_que_proposa = professor )
        q_professor |= Q(altres_professors_acompanyants = professor ) 
        q_professor |= Q(professors_responsables = professor ) 
        sortides = list (
            Sortida
            .objects
            .filter( q_professor )
            .filter( calendari_desde__isnull = False )
            .exclude(estat__in = ['E', 'P', ])
            .distinct()
                )
        for instance in sortides:
            event = Event()
            
            summary = u"{ambit}: {titol}".format(ambit=instance.ambit ,
                                                    titol= instance.titol_de_la_sortida)
            
            event.add('dtstart',localtime(instance.calendari_desde) )
            event.add('dtend' ,localtime(instance.calendari_finsa) )
            event.add('summary',summary)
            organitzador = u"\nOrganitza: "
            organitzador += u"{0}".format( u"Departament" + instance.departament_que_organitza.nom if instance.departament_que_organitza_id else u"" )
            organitzador += " " + instance.comentari_organitza
            event.add('organizer',  vText( u"{0} {1}".format( u"Departament " + instance.departament_que_organitza.nom  if instance.departament_que_organitza_id else u"" , instance.comentari_organitza )))
            event.add('description',instance.programa_de_la_sortida + organitzador)
            event.add('uid', 'djau-ical-sortida-{0}'.format( instance.id ) )
            event['location'] = vText( instance.ciutat )

            
            cal.add_component(event)


        return HttpResponse( cal.to_ical() )


@login_required
@group_required(['consergeria','professors'])
def detallProfessorHorari(request, pk, detall='all'):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    #grups_poden_veure_detalls = [u"sortides",u"consergeria",u"direcció",]

    #mostra_detalls = user.groups.filter(name__in=grups_poden_veure_detalls).exists()

    data_txt = request.GET.get( 'data', '' )

    try:
        data = datetime.strptime(data_txt, r"%Y-%m-%d").date()
    except ValueError:
        data = datetime.today()


    professor = get_object_or_404( Professor, pk=pk)
    tutoria = professor.tutor_set.filter( professor = professor )

    qHorari = Q(horari__professor = professor, dia_impartir = data)
    qGuardies = Q(professor_guardia = professor, dia_impartir = data)
    imparticions = Impartir.objects.filter( qHorari | qGuardies ).order_by( 'horari__hora')

    table=HorariProfessorTable(imparticions)

    RequestConfig(request).configure(table)

    return render(
        request,
        'mostraInfoProfessorCercat.html',
        {'table': table,
         'professor':professor,
         'tutoria': tutoria,
         'dia' : data,
         'lendema': (data + timedelta( days = +1 )).strftime(r'%Y-%m-%d'),
         'avui': datetime.today().date().strftime(r'%Y-%m-%d'),
         'diaabans': (data + timedelta( days = -1 )).strftime(r'%Y-%m-%d'),
         })

@login_required
@group_required(['professional'])
def blanc( request ):
    return render(
                request,
                'blanc.html',
                    {},
                    )