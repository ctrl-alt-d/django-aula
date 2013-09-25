# This Python file uses the following encoding: utf-8

#templates
from django.template import RequestContext

from aula.apps.usuaris.forms import CanviDadesUsuari, triaUsuariForm, loginUsuariForm,\
    recuperacioDePasswdForm, sendPasswdByEmailForm, canviDePasswdForm

from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

from aula.apps.extKronowin.models import ParametreKronowin

#workflow
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response

#helpers
from aula.utils import tools
from aula.utils.forms import ckbxForm
from aula.apps.usuaris.models import Professor, LoginUsuari, AlumneUser, OneTimePasswd,\
    Accio
from django.utils.datetime_safe import datetime
from datetime import timedelta
from django.db.models import Q
from aula.apps.presencia.models import Impartir

from django.contrib.auth import authenticate, login
from django.forms.forms import NON_FIELD_ERRORS
from django.contrib.auth.models import User
from aula.apps.usuaris.tools import enviaOneTimePasswd
from aula.utils.tools import getClientAdress

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
          
    resposta = render_to_response(
                  "form.html", 
                  {"form": form,
                   "head": head,
                   'infoForm': infoForm,
                   },
                  context_instance=RequestContext(request))
    
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
            passwd, _ =ParametreKronowin.objects.get_or_create( nom_parametre = 'passwd', defaults={'valor_parametre':'1234'}  )
            usuari.set_password( passwd )
            usuari.is_active = True
            usuari.save()
            return HttpResponseRedirect( url_next )
            
    else:
        form = triaUsuariForm()
    
    return render_to_response(
                'form.html', 
                {'form': form, 
                 'head': head},
                context_instance=RequestContext(request))    
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
    return render_to_response(
                'formset.html', 
                {'formset': formset, 
                 'head': head},
                context_instance=RequestContext(request))
    
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
    capcelera.amplade = 230
    capcelera.contingut = u'Professor'
    taula.capceleres.append( capcelera )
    
    capcelera = tools.classebuida()
    capcelera.amplade = 200
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
        imparticions = Impartir.objects.filter(qProfessor & qFinsAra & qTeGrup )
        nImparticios = imparticions.exclude( pot_no_tenir_alumnes = True).count()
        nImparticionsLlistaPassada = imparticions.exclude( pot_no_tenir_alumnes = True).filter( professor_passa_llista__isnull = False ).count()
        pct = nImparticionsLlistaPassada * 100 / nImparticios if nImparticios > 0 else 'N/A'
        camp.contingut = u'{0}% ({1} classes impartides, {2} controls)'.format( pct, nImparticios, nImparticionsLlistaPassada)
        filera.append(camp)


        #--
        taula.fileres.append( filera )
    
    report.append(taula)
        
    return render_to_response(
                'report.html',
                    {'report': report,
                     'head': 'Informació professors' ,
                    },
                    context_instance=RequestContext(request))            
        

def loginUser( request ):
    head=u'Login' 

    client_address = getClientAdress( request )

    url_next = '/'  
    if request.method == 'POST':
        form = loginUsuariForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['usuari']
            paraulaDePas=form.cleaned_data['paraulaDePas']
            user = authenticate(username=username, password=paraulaDePas)
            if user is not None:
                #Usuari i passwd estan bé
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


    return render_to_response(
                'loginForm.html',
                    {'form': form,
                     'head': head ,
                    },
                    context_instance=RequestContext(request))      

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
        
    return render_to_response(
                'form.html',
                    {'form': form,
                     'infoForm':infoForm,
                     'head': u'Canvi de Contrasenya' 
                     },
                    context_instance=RequestContext(request))   

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
        
    return render_to_response(
                'form.html',
                    {'form': form,
                     'infoForm':infoForm,
                     'head': u'Recuperació de Contrasenya' 
                     },
                    context_instance=RequestContext(request))    


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
        
    return render_to_response(
                'form.html',
                    {'form': form,
                     'infoForm':infoForm,
                     'head': u'Recuperació de Contrasenya' 
                     },
                    context_instance=RequestContext(request))  

def sendPasswdByEmail( request ):
    
    if request.method == 'POST':
        form = sendPasswdByEmailForm(request.POST, initial={'captcha': request.META['REMOTE_ADDR']})
        if form.is_valid():
            resultat = enviaOneTimePasswd( form.cleaned_data['email'] )
            resultat['url_next'] = '/'

            return render_to_response(
                        'resultat.html',
                            {'msgs': resultat ,
                             'head': 'Recuperació de contrasenya',
                            },
                            context_instance=RequestContext(request)) 
                    
    else:
        form = sendPasswdByEmailForm(  )
        
    return render_to_response(
    'form.html',
        {'form': form,
         'head': u'Recuperació de Contrasenya' 
         },
        context_instance=RequestContext(request))  
            
            