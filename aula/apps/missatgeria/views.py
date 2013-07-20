# This Python file uses the following encoding: utf-8

#workflow
from django.shortcuts import render_to_response#workflow
from django.http import HttpResponseRedirect

#auth
from django.contrib.auth.decorators import login_required

#templates
from django.template import RequestContext

from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from aula.utils import tools
from django.forms.models import modelform_factory
from aula.apps.alumnes.forms import triaAlumneForm
from aula.apps.missatgeria.models import Missatge, Destinatari
from aula.apps.tutoria.models import Tutor
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.models import User, Group
from aula.utils.forms import dataForm
from django.shortcuts import get_object_or_404
from aula.utils.decorators import group_required

@login_required
def elMeuMur( request, pg ):
    
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials
        
    q = user.destinatari_set.order_by('-missatge__data')
    paginator = Paginator(q.all(), 20)
    try:
        dests = paginator.page(pg)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        dests = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), delive#workflow
        dests = paginator.page(paginator.num_pages)

    if not request.session.has_key('impersonacio'):
        request.user.destinatari_set.filter(
                    moment_lectura__isnull = True,
                    pk__in = [ m.pk for m in dests.object_list ]
                ).update( moment_lectura = datetime.now() )
            
    return render_to_response(
                'missatges.html',
                    {'msgs' : dests,
                     'head': 'Missatges' ,
                    },
                    context_instance=RequestContext(request))
    
@login_required
@group_required(['professors','professional','consergeria'])
def enviaMissatgeTutors( request ):
    
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials   
    
    formset = []
    msgFormF = modelform_factory(Missatge, fields=( 'text_missatge', ) )
    
    if request.method == 'POST':        
        msg = Missatge( remitent = user )
        msg.credentials = credentials
        formAlumne = triaAlumneForm( data = request.POST)
        formData= dataForm( data = request.POST  )
        msgForm = msgFormF( data = request.POST, instance = msg )        
        
        if formAlumne.is_valid() and msgForm.is_valid() and formData.is_valid():
            alumne = formAlumne.cleaned_data['alumne']
            tutors = alumne.tutorsDeLAlumne()
            data = formData.cleaned_data['data']
            if len( tutors ) == 0:
                formAlumne._errors.setdefault(NON_FIELD_ERRORS, []).append(  u'''No trobat el tutor d'aquest alumne. Cal trucar al cap d'estudis.'''  )
            else:
                msg.save()
                strTutors = u''
                separador = ''
                for tutor in tutors:
                    txt = u'''Missatge relatiu al teu alumne tutorat {0}: Amb data {1}, {2}'''.format( unicode(alumne), unicode(data), msg.text_missatge)
                    msg.text_missatge = txt
                    msg.envia_a_usuari(tutor.getUser(), 'IN')
                    msg.enllac = '/tutoria/justificaFaltes/{0}/{1}/{2}/{3}'.format( alumne.pk, data.year, data.month, data.day )
                    msg.save()
                    strTutors += separador + u'Sr(a)' + unicode(tutor )
                    separador = u', '
                txtMsg = msg.text_missatge
                
                #envio al que ho envia:
                msg = Missatge( remitent = user, text_missatge = u'''Avís a tutors de l'alumne {0} enviat a {1}. El text de l'avís és: "{2}"'''.format( alumne, strTutors, txtMsg ) )
                msg.envia_a_usuari(user, 'PI')
                
                url = '/missatgeria/elMeuMur/'  
                return HttpResponseRedirect( url )  
    else:
        formAlumne = triaAlumneForm( )
        formData = dataForm(  label='Data', help_text=u'El text del missatge començarà per: Amb data ______, ' )        
        msgForm = msgFormF(  )
    
    formData.fields['data'].required = True
    
    formset.append( formAlumne )
    formset.append( formData )
    formset.append( msgForm )
        
    return render_to_response(
                'formset.html',
                    {'formset': formset,
                     'head': 'Avís a tutors.' ,
                    },
                    context_instance=RequestContext(request))


@login_required
@group_required(['professors','professional','consergeria','alumne'])
def enviaMissatgeAdministradors( request ):
    
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials   
    
    formset = []
    msgFormF = modelform_factory(Missatge, fields=( 'text_missatge', ) )
    
    if request.method == 'POST':        
        msg = Missatge( remitent = user )
        msg.credentials = credentials
        msgForm = msgFormF( data = request.POST, instance = msg )        
        
        if msgForm.is_valid():           
            administradors = Group.objects.get_or_create( name = 'administradors' )[0].user_set.all()
            if len( administradors ) == 0:
                msgForm._errors.setdefault(NON_FIELD_ERRORS, []).append(  u'''No estan definits els administradors, sorry.'''  )
            else:
                msg.text_missatge = u'''Avís d'error al programa: {0}'''.format(msg.text_missatge)
                msg.save()
                strAdmins = u''
                separador = ''
                for administrador in administradors:
                    msg.envia_a_usuari(administrador, 'VI')
                    strAdmins += separador + u'Sr(a)' + unicode( administrador )
                    separador = u', '
                txtMsg = msg.text_missatge
                
                #envio al que ho envia:
                msg = Missatge( remitent = user, text_missatge = u'''Avís a administradors enviat correctament. El text de l'avís és: "{0}"'''.format( txtMsg ) )
                msg.envia_a_usuari(user, 'PI')
                
                url = '/missatgeria/elMeuMur/'  
                return HttpResponseRedirect( url )  
    else:
        msgForm = msgFormF(  )
    
    formset.append( msgForm )
        
    return render_to_response(
                'formset.html',
                    {'formset': formset,
                     'head': u'''Avís a administradors. En cas d'error, sisplau, detalla clarament totes les passes per reproduir l'error.''' ,
                    },
                    context_instance=RequestContext(request))
    
    
@login_required
def llegeix( request, pk ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials

    destinatari = get_object_or_404( Destinatari, pk = pk )    
    
    if not request.session.has_key('impersonacio') and user == destinatari.destinatari:
        destinatari.credentials = credentials
        destinatari.followed = True
        destinatari.save()
    
    return HttpResponseRedirect( destinatari.missatge.enllac )  
    
    
    
    
          
    