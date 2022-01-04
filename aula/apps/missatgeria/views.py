# This Python file uses the following encoding: utf-8

#workflow
from django.shortcuts import render#workflow
from django.http import HttpResponseRedirect

#auth
from django.contrib.auth.decorators import login_required

#templates
from django.template import RequestContext

from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django_tables2 import RequestConfig
from aula.apps.missatgeria.table2_models import MissatgesTable
from aula.apps.usuaris.forms import triaProfessorsConsergesSelect2Form
from aula.utils import tools
from aula.utils.tools import unicode
from django.forms.models import modelform_factory
from aula.apps.alumnes.forms import triaAlumneForm, triaAlumneSelect2Form
from aula.apps.missatgeria.forms import EmailForm
from aula.apps.missatgeria.models import Missatge, Destinatari
from aula.apps.tutoria.models import Tutor
from django.core.exceptions import NON_FIELD_ERRORS
from django.contrib.auth.models import User, Group
from aula.utils.forms import dataForm
from django.shortcuts import get_object_or_404
from aula.utils.decorators import group_required
from aula.utils.my_paginator import DiggPaginator
from django.contrib import messages
from aula.apps.missatgeria.missatges_a_usuaris import MISSATGES, CONSERGERIA_A_TUTOR, tipusMissatge, \
    CONSERGERIA_A_CONSERGERIA, ERROR_AL_PROGRAMA, ACUS_REBUT_ERROR_AL_PROGRAMA, ACUS_REBUT_ENVIAT_A_PROFE_O_PAS, \
    EMAIL_A_FAMILIES, AVIS_ABSENCIA
from aula.apps.relacioFamilies.notifica import enviaEmailFamilies
import collections

@login_required
def elMeuMur( request, pg ,tipus = 'all'):
    
    credentials = tools.getImpersonateUser(request) 
    (user, l4) = credentials

    #amorilla@xtec.cat
    #Per veure tots els missatges junts
    if tipus.upper()=='TOT':
        tipus='all'
    q = user.destinatari_set.filter(missatge__tipus_de_missatge=tipus.upper()).order_by('-missatge__data') \
        if tipus != 'all' else user.destinatari_set.order_by('-missatge__data')

    if not request.session.has_key('impersonacio'):
        request.user.destinatari_set.filter(
                    moment_lectura__isnull = True,
                ).update( moment_lectura = datetime.now() )

    table = MissatgesTable(q)
    RequestConfig(request, paginate={"paginator_class":DiggPaginator , "per_page": 25}).configure(table)

    missatges = dict()
    for key,value in MISSATGES.items():
        missatges [key] = list(value.keys())[0]
        
    #Afegeix tipus TOT per opció de veure tots els missatges
    missatges['TOT'] = 'default'
    # Ordena alfabèticament els tipus
    missatges=collections.OrderedDict(sorted(missatges.items()))
    
    return render(
                    request,
                    'missatges.html',
                    {'table': table,
                     'missatges': missatges,
                    },
                 )
    
def enviaMsg(user, credentials, alumne, datai, horai, dataf, horaf, motiu, observ):
    from aula.apps.alumnes.tools import controlsRang
    
    msg = Missatge( remitent = user )
    msg.credentials = credentials
    msg.text_missatge = AVIS_ABSENCIA
    msg.enllac = '/tutoria/justificaFaltes/{0}/{1}/{2}/{3}'.format(alumne.pk, datai.year, datai.month, datai.day)
    msg.tipus_de_missatge = tipusMissatge(msg.text_missatge)
    msg.text_missatge=msg.text_missatge.format(alumne, 
                                               datai.strftime( '%d/%m' ),
                                               horai.strftime( '%H:%M' ), 
                                               dataf.strftime( '%d/%m' ), 
                                               horaf.strftime( '%H:%M' ), 
                                               motiu+((" - "+ observ) if bool(observ) else ""))
    msg.save()
    
    ctrlqs=controlsRang(alumne, datai, horai, dataf, horaf)
    # enllaça Missatge amb ControlAssistència
    for c in ctrlqs:
        c.comunicat=msg
        c.save()
        
    tutors = alumne.tutorsDeLAlumne()
    if len( tutors ) > 0:
        for tutor in tutors:
            msg.envia_a_usuari(tutor.getUser(), 'IN')

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
        formAlumne = triaAlumneSelect2Form( data = request.POST)
        formData= dataForm( data = request.POST  )
        formData.fields['data'].required = True
        msgForm = msgFormF( data = request.POST, instance = msg )        
        
        if formAlumne.is_valid() and msgForm.is_valid() and formData.is_valid():
            alumne = formAlumne.cleaned_data['alumne']
            tutors = alumne.tutorsDeLAlumne()
            data = formData.cleaned_data['data']
            if len( tutors ) == 0:
                formAlumne._errors.setdefault(NON_FIELD_ERRORS, []).append(  u'''No trobat el tutor d'aquest alumne. Cal trucar al cap d'estudis.'''  )
            else:
                request.session['consergeria_darrera_data'] = data
                txt2 = msg.text_missatge
                txt = CONSERGERIA_A_TUTOR
                msg.text_missatge = txt
                msg.enllac = '/tutoria/justificaFaltes/{0}/{1}/{2}/{3}'.format(alumne.pk, data.year, data.month, data.day)
                tipus_de_missatge = tipusMissatge(txt)
                msg.tipus_de_missatge = tipus_de_missatge
                msg.save()
                msg.afegeix_info(u"Alumne: {alumne}".format(alumne=alumne))
                msg.afegeix_info(u"Data relativa a l'avís: {data}".format(data=data))
                msg.afegeix_info(u"Avís: {txt2}".format(txt2=txt2))
                for tutor in tutors:
                    msg.envia_a_usuari(tutor.getUser(), 'IN')
                strTutors = u", ".join(  u'Sr(a) {}'.format( tutor) for tutor in tutors )

                #envio al que ho envia:
                missatge = CONSERGERIA_A_CONSERGERIA
                tipus_de_missatge = tipusMissatge(missatge)
                msg = Missatge( remitent = user,
                                text_missatge = missatge.format( alumne, strTutors, txt2 ),
                                tipus_de_missatge = tipus_de_missatge)
                msg.envia_a_usuari(user, 'PI')
                msg.destinatari_set.filter(destinatari = user).update(moment_lectura=datetime.now())  #marco com a llegit
                
                url = '/missatgeria/enviaMissatgeTutors/'
                messages.info( request, u"Avís als tutors de {} ({}) enviat correctament".format(unicode(alumne), strTutors ) )
                return HttpResponseRedirect( url )  
    else:
        
        consergeria_darrera_data = request.session.get( 'consergeria_darrera_data' , datetime.today() )
        formAlumne = triaAlumneSelect2Form( )
        formData = dataForm(  label='Data', 
                              help_text=u'El text del missatge començarà per: Amb data ______, ' ,
                              initial = {'data': consergeria_darrera_data })        
        formData.fields['data'].required = True
        msgForm = msgFormF(  )
    
    
    
    formset.append( formAlumne )
    formset.append( formData )
    formset.append( msgForm )

    for form in formset:
        for field in form.fields:
            form.fields[field].widget.attrs['class'] = "form-control"


    return render(
                request,
                'formset.html',
                    {'formset': formset,
                     'titol_formulari': u"Missatge a professors tutors de l'alumne",                    
                     'head': 'Avís a tutors.' ,
                    },
                )


@login_required
# Permet a qualsevol usuari
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
                missatge = ERROR_AL_PROGRAMA
                msg.text_missatge = missatge.format(msg.text_missatge)
                tipus_de_missatge = tipusMissatge(missatge)
                msg.tipus_de_missatge = tipus_de_missatge
                msg.save()
                strAdmins = u''
                separador = ''
                for administrador in administradors:
                    msg.envia_a_usuari(administrador, 'VI')
                    strAdmins += separador + u'Sr(a)' + unicode( administrador )
                    separador = u', '
                txtMsg = msg.text_missatge
                
                #envio al que ho envia:
                missatge = ACUS_REBUT_ERROR_AL_PROGRAMA
                tipus_de_missatge = tipusMissatge(missatge)
                msg = Missatge( remitent = user, text_missatge = missatge.format( txtMsg ), tipus_de_missatge = tipus_de_missatge )
                msg.envia_a_usuari(user, 'PI')
                
                url = '/missatgeria/elMeuMur/'
                return HttpResponseRedirect( url )  
    else:
        msgForm = msgFormF(  )
    
    formset.append( msgForm )

    for form in formset:
        for field in form.fields:
            form.fields[field].widget.attrs['class'] = "form-control"

    return render(
                request,
                'formset.html',
                    {'formset': formset,
                     'head': u'''Avís a administradors. En cas d'error, sisplau, detalla clarament totes les passes per reproduir l'error.''' ,
                    },
                )


@login_required
@group_required(['professors', 'professional', 'consergeria',])
def enviaMissatgeProfessorsPas(request):
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    formset = []
    msgFormF = modelform_factory(Missatge, fields=('text_missatge',))

    if request.method == 'POST':
        msg = Missatge(remitent=user)
        msg.credentials = credentials
        formProfessorConserge = triaProfessorsConsergesSelect2Form(data=request.POST)
        msgForm = msgFormF(data=request.POST, instance=msg)

        if formProfessorConserge.is_valid() and msgForm.is_valid():
            msg.tipus_de_missatge = 'MISSATGERIA'
            msg.save()
            professors_conserges = formProfessorConserge.cleaned_data['professors_conserges']
            destinataris_txt = ", ".join( unicode(pc) for pc in professors_conserges)
            for professor_conserge in professors_conserges:
                msg.envia_a_usuari(professor_conserge.getUser(), 'IN')

            # envio al que ho envia:
            missatge = ACUS_REBUT_ENVIAT_A_PROFE_O_PAS
            tipus_de_missatge = tipusMissatge(missatge)
            msg2 = Missatge(remitent=user,
                           text_missatge=missatge.format(
                               destinataris_txt,
                               msg.text_missatge),
                            tipus_de_missatge= tipus_de_missatge)
            msg2.envia_a_usuari(user, 'PI')
            msg2.destinatari_set.filter(destinatari = user).update(moment_lectura=datetime.now())

            messages.info(request, u"Missatge a {destinataris} enviat correctament".format(destinataris=destinataris_txt))

            if user.groups.filter(name="consergeria").exists():
                url = '/missatgeria/enviaMissatgeProfessorsPas/'
            else:
                url = '/missatgeria/elMeuMur/'
            return HttpResponseRedirect(url)
    else:
        formProfessorConserge = triaProfessorsConsergesSelect2Form()
        msgForm = msgFormF()

    formset.append(formProfessorConserge)
    formset.append(msgForm)

    for form in formset:
        for field in form.fields:
            form.fields[field].widget.attrs['class'] = "form-control"

    return render(
        request,
        'formset.html',
        {'formset': formset,
         'titol_formulari': u"Missatge a professors i/o PAS",
         'head': u"Missatge a membres del professorat o consergeria",
         },
        )


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
    

@login_required
@group_required(['direcció','administradors'])
def EmailFamilies(request):
    '''Envia email a totes les famílies
    
    L'usuari que envia l'email rep un missatge per Django amb una còpia del correu
    '''
    
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    formset = []

    if request.method == 'POST':
        msgForm = EmailForm(request.POST,request.FILES)

        if msgForm.is_valid():
            subject = msgForm.cleaned_data['assumpte']
            message = msgForm.cleaned_data['missatge']
            attach = request.FILES.getlist('adjunts') if request.FILES else []
            try:
                contOk, contErr = enviaEmailFamilies(subject, message, attach)
                # envio al que ho envia:
                missatge = EMAIL_A_FAMILIES
                tipus_de_missatge = tipusMissatge(missatge)
                msg = Missatge(remitent=user,
                                text_missatge=missatge.format(contOk, "\n"+subject+":\n"+message+"\n\nadjunts:"+
                                                              (str( [ f.name for f in attach if f.name ]) if attach else "")),
                                tipus_de_missatge= tipus_de_missatge)
                msg.envia_a_usuari(user, 'PI')
                msg.destinatari_set.filter(destinatari = user).update(moment_lectura=datetime.now())
    
                messages.info(request, u"Email a famílies enviat a {0} adreces".format(contOk)+
                              (", error en {0} adreces".format(contErr) if contErr>0 else ""))
            except:
                messages.error(request, u"No s'ha pogut fer l'enviament, torneu a intentar en uns minuts")
            url = '/missatgeria/elMeuMur/'
            return HttpResponseRedirect(url)
    else:
        msgForm = EmailForm()

    formset.append(msgForm)
    
    for form in formset:
        for field in form.fields:
            form.fields[field].widget.attrs['class'] = "form-control"
    
    return render(
        request,
        'formset.html',
        {'formset': formset,
         'titol_formulari': u"Email per a les famílies",
         'head': u"Email a totes les famílies",
         },
        )
    