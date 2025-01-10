# This Python file uses the following encoding: utf-8
import itertools
from itertools import groupby

from django.conf import settings

#templates
from django.forms import FileInput
from django.template import RequestContext
from django.templatetags.static import static

#workflow
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy

#auth
from django.contrib.auth.decorators import login_required
from django_tables2 import RequestConfig

from aula.apps.usuaris.models import QRPortal

#helpers
from aula.apps.avaluacioQualitativa.models import RespostaAvaluacioQualitativa
from aula.apps.incidencies.models import Incidencia, Sancio, Expulsio
from aula.apps.presencia.models import ControlAssistencia, EstatControlAssistencia
from aula.apps.sortides.models import Sortida, NotificaSortida, SortidaPagament, QuotaPagament
from aula.apps.relacioFamilies.forms import AlumneModelForm, comunicatForm
from aula.mblapp.table2_models import Table2_QRPortalAlumne
from aula.settings import CUSTOM_DADES_ADDICIONALS_ALUMNE, CUSTOM_FAMILIA_POT_MODIFICAR_PARAMETRES
from aula.utils import tools
from aula.utils.my_paginator import DiggPaginator
from aula.utils.tools import unicode
from aula.apps.alumnes.models import Alumne, DadesAddicionalsAlumne
from aula.apps.alumnes.tools import get_hores, properdiaclasse, ultimdiaclasse
import qrcode
from aula.utils.tools import classebuida
#qualitativa


#exceptions
from django.http import Http404, HttpResponseRedirect, HttpResponse
from aula.apps.usuaris.models import User2Professor, AlumneUser
from aula.apps.tutoria.models import Tutor
from aula.utils.decorators import group_required

from django.db.models import Q
from django.forms.models import modelform_factory, modelformset_factory
from datetime import datetime, timedelta

from aula.apps.usuaris.tools import enviaBenvingudaAlumne, bloqueja, desbloqueja, testEmail

import random
from django.contrib.humanize.templatetags.humanize import naturalday
from django.contrib import messages
import json
from django.utils.html import escapejs
import django.utils.timezone
from aula.apps.matricula.viewshelper import inforgpd
from aula.apps.missatgeria.models import Missatge
from django.utils import formats

#@login_required
#@group_required(['professors'])
#def dadesRelacioFamilies_old( request ):
#    credentials = tools.getImpersonateUser(request) 
#    (user, l4 ) = credentials
#
#    professor = User2Professor( user )     
#    
#    grups = [ t.grup for t in  Tutor.objects.filter( professor = professor )]
#    consulta_alumnes_grups = Q( grup__in =  grups )           
#    consulta_alumnes_individuals = Q( pk__in = [ti.alumne.pk for ti in professor.tutorindividualitzat_set.all() ]  )
#            
#    alumnes =  Alumne.objects.filter( consulta_alumnes_individuals | consulta_alumnes_grups )
#    
#    AlumneFormSet = modelformset_factory(Alumne, 
#                                         fields = ( 'nom',  'correu_relacio_familia_pare', 'correu_relacio_familia_mare', 'compte_bloquejat'  ), 
#                                         extra =0)
#    
#    formset = AlumneFormSet(queryset=alumnes)
#    
#    if request.method == 'POST':
#        form = formset(  request.POST  )
#        if form.is_valid(  ):
#            form.save()
#
#    else:
#        pass  
#        #form.base_fields['data'].widget = forms.DateTimeInput(attrs={'class':'DateTimeAnyTime'} )                
#        
#    return render(
#                request,
#                'formsetgrid.html',
#                    {'formset': formset,
#                     'head': u'Gestió relació familia amb empreses' ,
#                     'formSetDelimited':True},
#                   )


#--------------------------------------------


@login_required
@group_required(['professors'])
def enviaBenvinguda( request , pk ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    professor = User2Professor( user )     
            
    alumne =  get_object_or_404(Alumne, pk = int(pk) )
    
    url_next = '/open/dadesRelacioFamilies/#{0}'.format(alumne.pk)
            
    #seg-------------------
    te_permis = l4 or  professor in alumne.tutorsDeLAlumne() 
    if  not te_permis:
        raise Http404()     
    
    filera = []                
        
    try:
        cosMissatge = enviaBenvingudaAlumne( alumne ) 
    except Exception as e:
        cosMissatge = {'errors': [ e ], 'infos':[], 'warnings':[] }
    
    cosMissatge['url_next']=url_next
        
    return render(
                request,
                'resultat.html',
                    {'msgs': cosMissatge ,
                     'head': u"Acció Envia Benviguda a {0}".format( alumne ) ,
                    },
                )


#--------------------------------------------

@login_required
@group_required(['professors'])
def bloquejaDesbloqueja( request , pk ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    professor = User2Professor( user )     
            
    alumne =  Alumne.objects.get( pk = int(pk) )
    
    url_next = '/open/dadesRelacioFamilies/#{0}'.format(alumne.pk)

    #seg-------------------
    te_permis = l4 or  professor in alumne.tutorsDeLAlumne() 
    if  not te_permis:
        raise Http404()
        
    actiu =  alumne.esta_relacio_familia_actiu() 
    
    if actiu:
        resultat = bloqueja( alumne, u'Bloquejat per {0} amb data {1}'.format( professor, datetime.now() ) )
    else:
        resultat = desbloqueja( alumne )
    resultat['url_next'] = url_next
    
    return render(
                request,
                'resultat.html',
                    {'msgs': resultat ,
                     'head': 'Canvi configuració accés família de {0}'.format( alumne ) ,
                    },
                )

@login_required
@group_required(['professors'])
def qrTokens( request , pk=None ):
    import time
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials

    professor = User2Professor(user)

    if pk:
        alumne = get_object_or_404(Alumne, pk=pk) if pk else None
        alumnes = [alumne, ]
    else:
        els_meus_alumnes_de_grups_tutorats = [a for t in professor.tutor_set.all()
                                              for a in t.grup.alumne_set.all()]
        els_meus_tutorats_individualitzats = [t.alumne for t in professor.tutorindividualitzat_set.all()]
        alumnes = els_meus_alumnes_de_grups_tutorats + els_meus_tutorats_individualitzats

        # seg-------------------
        seg_tutor_de_lalumne = pk and professor in alumne.tutorsDeLAlumne()
        seg_es_tutor = professor.tutor_set.exists() or professor.i.tutorindividualitzat_set.exists()
        te_permis = l4 or seg_tutor_de_lalumne or seg_es_tutor
        if not te_permis:
            raise Http404()

    report = []


    fitxers_a_esborrar = []

    for copia, alumne in itertools.product( [1,2,], alumnes ):
        # munto el token
        qr_token = QRPortal()
        qr_token.calcula_clau_i_localitzador()
        qr_token.alumne_referenciat = alumne
        qr_token.save()

        qr_dict = {"key": qr_token.clau,
                   "id": alumne.id,
                   "name": alumne.nom,
                   "surname": alumne.cognoms,
                   "api_end_point": settings.URL_DJANGO_AULA,
                   "organization": settings.NOM_CENTRE,
                   }
        qr_text = json.dumps(qr_dict)


        # munto imatge:
        nom_fitxer = r"/tmp/barcode-{0}-{1}-{2}-{3}.png".format( time.time(),
                                                             request.session.session_key,
                                                             alumne.pk,
                                                             copia )
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=3,
            border=2,
        )
        qr.add_data(qr_text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(nom_fitxer)
        fitxers_a_esborrar.append( nom_fitxer )
        o = classebuida()
        o.alumne = unicode(alumne)
        o.grup = unicode(alumne.grup)
        o.copia = copia
        o.clau = qr_text if settings.DEBUG else ""
        report.append(o)
        o.barres = nom_fitxer

    # from django.template import Context
    from appy.pod.renderer import Renderer
    import html
    import os
    from django import http

    excepcio = None

    # try:

    # resultat = StringIO.StringIO( )
    resultat = "/tmp/DjangoAula-temp-{0}-{1}.odt".format(time.time(), request.session.session_key)
    # context = Context( {'reports' : reports, } )
    path = os.path.join(settings.PROJECT_DIR, '../customising/docs/qr.odt')
    if not os.path.isfile(path):
        path = os.path.join(os.path.dirname(__file__), 'templates/qr.odt')

    renderer = Renderer(path, {'report': report, }, resultat)
    renderer.run()
    docFile = open(resultat, 'rb')
    contingut = docFile.read()
    docFile.close()
    os.remove(resultat)

    # barcode
    for nom_fitxer in fitxers_a_esborrar:
        os.remove(nom_fitxer)

    #     except Exception, e:
    #         excepcio = unicode( e )

    if True:  # not excepcio:
        response = http.HttpResponse(contingut, content_type='application/vnd.oasis.opendocument.text')
        response['Content-Disposition'] = u'attachment; filename="{0}-{1}-{2}.odt"'.format("QR", alumne.cognoms, alumne.nom)

    else:
        response = http.HttpResponse('''Als Gremlin no els ha agradat aquest fitxer! %s''' % html.escape(excepcio))

    return response

@login_required
@group_required(['professors'])
def qrs( request):

        credentials = tools.getImpersonateUser(request)
        (user, _) = credentials

        professor = User2Professor(user)

        report = []
        grups = [t.grup for t in Tutor.objects.filter(professor=professor)]
        grups.append('Altres')
        for grup in grups:
            taula = tools.classebuida()

            taula.titol = tools.classebuida()
            taula.titol.contingut = ''
            taula.titol.enllac = None

            taula.capceleres = []

            capcelera = tools.classebuida()
            capcelera.amplade = 75
            capcelera.contingut = grup if grup == 'Altres' else u'{0} ({1})'.format(unicode(grup), unicode(grup.curs))
            capcelera.enllac = ""
            taula.capceleres.append(capcelera)


            capcelera = tools.classebuida()
            capcelera.amplade = 25
            capcelera.contingut = u'Acció'
            taula.capceleres.append(capcelera)

            taula.fileres = []

            if grup == 'Altres':
                consulta_alumnes = Q(pk__in=[ti.alumne.pk for ti in professor.tutorindividualitzat_set.all()])
            else:
                consulta_alumnes = Q(grup=grup)

            alumnes = Alumne.objects.filter(consulta_alumnes)


            for alumne in alumnes:

                filera = []

                # -Alumne--------------------------------------------
                camp = tools.classebuida()
                camp.codi = alumne.pk
                camp.enllac = None
                camp.contingut = unicode(alumne)
                filera.append(camp)


                # -Acció--------------------------------------------
                camp = tools.classebuida()
                camp.enllac = None
                accio_list = [(u'Genera nous codis QR', '/open/qrTokens/{0}'.format(alumne.pk)),
                              (u"Gestiona QR's existents", '/open/gestionaQRs/{0}'.format(alumne.pk)),
                              ]
                camp.multipleContingut = accio_list
                filera.append(camp)

                # --
                taula.fileres.append(filera)
            report.append(taula)

        return render(
            request,
            'report.html',
            {'report': report,
             'head': "QR's dels meus tutorats",
             },
        )

@login_required
@group_required(['professors'])
def gestionaQRs(request, pk=None):
    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    alumne=Alumne.objects.get(pk=pk)

    qrs = (QRPortal
                .objects
                .filter(alumne_referenciat=alumne)
                .order_by('moment_expedicio')
                .distinct()
                )

    table = Table2_QRPortalAlumne(data=list(qrs))
    table.order_by = '-moment_expedicio'
    RequestConfig(request, paginate={"paginator_class": DiggPaginator, "per_page": 10}).configure(table)

    return render(
        request,
        'gestionaQRs.html',
        {'table': table,
         'alumne': alumne,
         }
    )


@login_required
@group_required(['professors'])
def configuraConnexio( request , pk ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    professor = User2Professor( user )     
            
    alumne =  Alumne.objects.get( pk = int(pk) )
    
    #seg-------------------
    te_permis = l4 or  professor in alumne.tutorsDeLAlumne() 
    if  not te_permis:
        raise Http404() 

    edatAlumne = None
    try:
        edatAlumne = alumne.edat()
    except:
        pass

    imageUrl = alumne.get_foto_or_default

    dades_resp1 = [alumne.rp1_nom, alumne.rp1_mobil if alumne.rp1_mobil else alumne.rp1_telefon, alumne.rp1_correu]
    dades_resp2 = [alumne.rp2_nom, alumne.rp2_mobil if alumne.rp2_mobil else alumne.rp2_telefon, alumne.rp2_correu]

    infoForm = [
          ('Alumne',unicode( alumne) ),
          ('Edat alumne', edatAlumne),
          ('Dades responsable 1', ' - '.join(filter(None,dades_resp1))),
          ('Dades responsable 2', ' - '.join(filter(None,dades_resp2))),
          ('Altres telèfons alumne', alumne.altres_telefons),
    ]


    if alumne.dadesaddicionalsalumne_set.exists():
        for element in CUSTOM_DADES_ADDICIONALS_ALUMNE:
            if 'Tutor' in element['visibilitat']:
                try:
                    valor = alumne.dadesaddicionalsalumne_set.get(label=element['label']).value
                except:
                    valor = '-'
                infoForm.append((element['label'] + u'(Esfer@/Saga)', valor))

    AlumneFormSet = modelform_factory(Alumne,
                                      form=AlumneModelForm,
                                      widgets={
                                          'foto': FileInput,}
                                         )

    if request.method == 'POST':
        form = AlumneFormSet(  request.POST , request.FILES, instance=alumne )
        if form.is_valid(  ):
            #Comprova els dominis de correu
            errors = {}
            email=form.cleaned_data['correu_relacio_familia_pare']
            res, email = testEmail(email, False)
            if res<-1:
                errors.setdefault('correu_relacio_familia_pare', []).append(u'''Adreça no vàlida''')
            email=form.cleaned_data['correu_relacio_familia_mare']
            res, email = testEmail(email, False)
            if res<-1:
                errors.setdefault('correu_relacio_familia_mare', []).append(u'''Adreça no vàlida''')

            if len(errors)>0:
                form._errors.update(errors)
            else:
                form.save()
                url_next = '/open/dadesRelacioFamilies#{0}'.format(alumne.pk  ) 
                return HttpResponseRedirect( url_next )

    else:
        form = AlumneFormSet(instance=alumne)                
        
    return render(
                request,
                'configuraConnexio.html',
                    {'form': form,
                     'image': imageUrl,
                     'infoForm': infoForm,
                     'head': u'Gestió relació família' ,
                     'formSetDelimited':True},
                )

    
#--------------------------------------------------------------------------------------------------------

@login_required
@group_required(['professors'])
def dadesRelacioFamilies( request ):
    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    report = []
    grups = [ t.grup for t in  Tutor.objects.filter( professor = professor )]
    grups.append( 'Altres' )
    for grup in grups:
            taula = tools.classebuida()

            taula.titol = tools.classebuida()
            taula.titol.contingut = ''
            taula.titol.enllac = None

            taula.capceleres = []
            
            capcelera = tools.classebuida()
            capcelera.amplade = 25
            capcelera.contingut = grup if grup == 'Altres' else u'{0} ({1})'.format(unicode( grup ) , unicode( grup.curs ) ) 
            capcelera.enllac = ""
            taula.capceleres.append(capcelera)
            
            capcelera = tools.classebuida()
            capcelera.amplade = 35
            capcelera.contingut = u'Correus Contacte'
            taula.capceleres.append(capcelera)
                        
            capcelera = tools.classebuida()
            capcelera.amplade = 25
            capcelera.contingut = u'Estat'
            taula.capceleres.append(capcelera)

            capcelera = tools.classebuida()
            capcelera.amplade = 15
            capcelera.contingut = u'Acció'
            taula.capceleres.append(capcelera)
                        
            taula.fileres = []
            
            if grup == 'Altres':
                consulta_alumnes = Q( pk__in = [ti.alumne.pk for ti in professor.tutorindividualitzat_set.all() ]  )
            else:
                consulta_alumnes = Q( grup =  grup )

            alumnes = Alumne.objects.filter(consulta_alumnes )

            familia_pendent_de_mirar_models = [
                (u'qualitativa', RespostaAvaluacioQualitativa,),
                (u'sortida(es)', NotificaSortida,),
                (u'incidencies o observacions', Incidencia,),
                (u'sanció(ns)', Sancio,),
                (u'expulsió(ns)', Expulsio,),
                (u'faltes assistència', ControlAssistencia,),
            ]

            familia_pendent_de_mirar = {}

            for codi, model in familia_pendent_de_mirar_models:
                familia_pendent_de_mirar[codi]= ( model
                                                    .objects
                                                    .filter( alumne__in = alumnes )
                                                    .filter( relacio_familia_revisada__isnull = True )
                                                    .filter( relacio_familia_notificada__isnull = False )
                                                    .values_list( 'alumne__pk', flat=True )
                                                  )

            for alumne in alumnes:
                
                filera = []
                
                #-Alumne--------------------------------------------
                camp = tools.classebuida()
                camp.codi = alumne.pk
                camp.enllac = None
                camp.contingut = unicode(alumne)
                filera.append(camp)

                #-Correus Contacte--------------------------------------------
                camp = tools.classebuida()
                camp.enllac = None
                camp.contingut = unicode( ', '.join( alumne.get_correus_relacio_familia() ) )
                filera.append(camp)


                #-Bloquejat--------------------------------------------           
                camp = tools.classebuida()
                camp.codi = alumne.pk
                camp.enllac = None
                bloquejat_text =  [ ( alumne.motiu_bloqueig, None ), ] if  alumne.motiu_bloqueig else []
                nConnexions = alumne.user_associat.LoginUsuari.filter(exitos=True).count()
                camp.multipleContingut = bloquejat_text + [ ( u'( {0} connexs. )'.format(nConnexions) , None, ), ]
                if nConnexions > 0:
                    dataDarreraConnexio = alumne.user_associat.LoginUsuari.filter(exitos=True).order_by( '-moment' )[0].moment
                    camp.multipleContingut.append( ( u'Darrera Connx: {0}'.format(  dataDarreraConnexio.strftime( '%d/%m/%Y' ) ), None, ) )
                for ambit in familia_pendent_de_mirar:
                    if alumne.pk in familia_pendent_de_mirar[ambit]:
                        camp.multipleContingut.append( (u"{} x revisar".format(ambit), None,) )
                filera.append(camp)
                
                #-Acció--------------------------------------------
                camp = tools.classebuida()
                camp.enllac = None
                accio_list = [ (u'Configura', '/open/configuraConnexio/{0}'.format(alumne.pk) ), 
                               #(u'Bloquejar' if alumne.esta_relacio_familia_actiu() else u'Desbloquejar', '/open/bloquejaDesbloqueja/{0}'.format(alumne.pk)),
                               (u'Envia benvinguda' , '/open/enviaBenvinguda/{0}'.format(alumne.pk)),
                               (u'Veure Portal', '/open/elMeuInforme/{0}'.format(alumne.pk)),
                               ]
                camp.multipleContingut = accio_list
                filera.append(camp)
                
                #--
                taula.fileres.append( filera )            
            report.append(taula)
        
    return render(
                request,
                'report.html',
                    {'report': report,
                     'head': 'Els meus alumnes tutorats' ,
                    },
                )


                
#--------------------------------------------------------------------------------------------------------    
@login_required
def canviParametres( request ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    if  not CUSTOM_FAMILIA_POT_MODIFICAR_PARAMETRES:
        raise Http404()

    alumne = Alumne.objects.get( user_associat = user )

    edatAlumne = None
    try:
        edatAlumne = alumne.edat()
    except:
        pass

    infoForm = [
        ('Alumne', unicode(alumne)),
        # ( 'Telèfon Alumne', alumne.telefons),
        ('Telèfon Alumne', alumne.rp1_telefon + u', ' + alumne.rp2_telefon + u', ' + alumne.altres_telefons),
        # ( 'Nom tutors', alumne.tutors),
        ('Nom tutors', alumne.rp1_nom + u', ' + alumne.rp2_nom),
        # ('Correu tutors (Saga)', alumne.correu_tutors),
        ('Correu tutors (Saga)', alumne.rp1_correu + u', ' + alumne.rp2_correu),
        ('Edat alumne', edatAlumne),
    ]
    
    AlumneFormSet = modelform_factory(Alumne,
                                      form=AlumneModelForm,
                                      widgets={
                                          'foto': FileInput,}
                                         )
    
    if request.method == 'POST':
        form = AlumneFormSet(  request.POST , request.FILES, instance=alumne )
        if form.is_valid(  ):
            #Comprova els dominis de correu
            errors = {}
            email=form.cleaned_data['correu_relacio_familia_pare']
            res, email = testEmail(email, False)
            if res<-1:
                errors.setdefault('correu_relacio_familia_pare', []).append(u'''Adreça no vàlida''')
            email=form.cleaned_data['correu_relacio_familia_mare']
            res, email = testEmail(email, False)
            if res<-1:
                errors.setdefault('correu_relacio_familia_mare', []).append(u'''Adreça no vàlida''')

            if len(errors)>0:
                form._errors.update(errors)
            else:
                form.save()
                url_next = '/open/elMeuInforme/'
                return HttpResponseRedirect( url_next )

    else:
        form = AlumneFormSet(instance=alumne)

    return render(
                request,
                'configuraConnexio.html',
                    {'form': form,
                     'image': alumne.get_foto_or_default,
                     'infoForm': infoForm,
                     'head': u'Canvi de paràmetres' ,
                     'formSetDelimited':True,
                     'rgpd': inforgpd()},
                )

#--------------------------------------------------------------------------------------------------------

def choices_hores(alumne, dia, actual=True):
    if not bool(alumne): hores=[]
    else: hores=get_hores(alumne, dia, actual)
    hores=[("0","- dia complet -")]+hores

    return hores

#--------------------- AJAX per seleccionar hores segons alumne i dia --------------------------------------------#
@login_required
def horesAlumneAjax( request, idalumne, dia ):
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials

    alumne = Alumne.objects.filter( user_associat = user )
    if alumne and alumne[0].id!=int(idalumne):
        return HttpResponse("")
    
    # Es manté idalumne per futures ampliacions a on professorat 
    # farà servir aquest view    
    if request.method == 'GET':  #request.is_ajax()
        try:
            alumne = Alumne.objects.get( id=idalumne )
        except Alumne.DoesNotExist as e:
            return HttpResponse("")
        dia=datetime.strptime(dia, "%Y-%m-%d").date()
        hores = get_hores(alumne, dia)
        message = u'<option value="0" selected>- dia complet -</option>' ;
        for h in hores:
            message +=  u'<option value="%s">%s</option>'% (h[0], h[1] )
        return HttpResponse(message)
    
@login_required
def comunicatAbsencia( request ):
    from aula.apps.missatgeria.views import enviaMsg
    from aula.apps.horaris.models import FranjaHoraria
    
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
    diesantelacio = 6

    alumne = Alumne.objects.filter( user_associat = user )
    
    if alumne:
        alumne=alumne[0]
    else:
        messages.info( request, u"No és possible fer comunicats." )
        return HttpResponseRedirect('/')
    
    ara=datetime.now()
    primerdia=properdiaclasse(alumne, ara)
    if not primerdia:
        messages.info( request, u"No és possible fer comunicats." )
        return HttpResponseRedirect('/')

    if primerdia > (ara+timedelta(days=diesantelacio)).date():
        messages.info( request, 
                u"Només es poden fer comunicats amb antelació màxima d'una setmana. La propera classe serà el dia {0}."\
                .format(primerdia.strftime( '%d/%m' )))
        return HttpResponseRedirect('/')
    
    ultimdia=ultimdiaclasse(alumne,primerdia+timedelta(days=diesantelacio))
    if not ultimdia:
        ultimdia=primerdia
    if request.method == 'POST':
        form = comunicatForm(alumne, primerdia, ultimdia, request.POST)
        if form.is_valid():
            datai=form.cleaned_data['datainici']
            horai=form.cleaned_data['horainici']
            dataf=form.cleaned_data['datafi']
            horaf=form.cleaned_data['horafi']
            motiu = form.cleaned_data['motiu']
            motiu = dict(form.fields['motiu'].choices)[motiu]
            observ=form.cleaned_data['observacions']
            if int(horai)==0:
                hores=get_hores(alumne, datai)
                horai=hores[0][0] if hores and hores[0] else FranjaHoraria.objects.first().id
            if int(horaf)==0:
                hores=get_hores(alumne, dataf)
                horaf=hores[-1][0] if hores and hores[-1] else FranjaHoraria.objects.last().id
            horai=FranjaHoraria.objects.get(id=horai).hora_inici
            horaf=FranjaHoraria.objects.get(id=horaf).hora_fi
            enviaMsg(user, credentials, alumne, datai, horai, dataf, horaf, motiu, observ)
            url_next = reverse_lazy('relacio_families__informe__el_meu_informe')
            messages.info( request, u"Comunicat d'absència per {}, enviat correctament".format(unicode(alumne.nom)) )
            return HttpResponseRedirect( url_next )
        else:
            datai=form.cleaned_data.get('datainici',None)
            if datai:
                form.initial['datainici']=datai.strftime('%d/%m/%Y')
                form.fields['horainici'].choices=choices_hores(alumne, datai)
            dataf=form.cleaned_data.get('datafi',None)
            if dataf:
                form.initial['datafi']=dataf.strftime('%d/%m/%Y')
                form.fields['horafi'].choices=choices_hores(alumne, dataf)

    else:
        form = comunicatForm(alumne, primerdia, ultimdia)

    return render(
                request,
                'form.html',
                {'form': form,
                 'head': u'Comunicat d\'absència' ,
                 },
                )
    
import django_tables2 as tables

class ComunicatsTable(tables.Table):
 
    class Meta:
        model = Missatge
        # add class="paleblue" to <table> tag
        attrs = {"class": "paleblue table table-striped"}
        template = 'bootable2.html'
        fields = ("data", "text_missatge")
        order_by = ("-data" )

@login_required
def comunicatsAnteriors(request):
    from django_tables2 import RequestConfig
    from aula.apps.missatgeria.missatges_a_usuaris import tipusMissatge, AVIS_ABSENCIA
    from aula.utils.my_paginator import DiggPaginator
    
    credentials = tools.getImpersonateUser(request)
    (user, l4) = credentials
    tipus = tipusMissatge(AVIS_ABSENCIA)
    
    q = user.missatge_set.filter(tipus_de_missatge=tipus)

    table = ComunicatsTable(q)
    RequestConfig(request, paginate={"paginator_class":DiggPaginator , "per_page": 25}).configure(table)
  
    return render(
                    request,
                    'table2.html',
                    {'table': table,
                    },
                 )

@login_required
def elMeuInforme( request, pk = None ):
    """Dades que veurà l'alumne"""
    
    detall = 'all'

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
    nTaula = 0
    
    tePermis = True
    semiImpersonat = False
    if pk:
        professor = User2Professor( user )
        alumne =  Alumne.objects.get( pk = pk )   
        tePermis = professor in alumne.tutorsDeLAlumne() 
        semiImpersonat = True
    else:
        try:
            alumne = Alumne.objects.get( user_associat = user )
        except Exception as e:
            alumne = None
    
    if not alumne or not tePermis:
        raise Http404 
    
    head = u'{0} ({1})'.format(alumne , unicode( alumne.grup ) )
    
    ara = datetime.now()
    
    report = []

    #----Assistencia --------------------------------------------------------------------
    if detall in ['all', 'assistencia']:
        controls = alumne.controlassistencia_set.exclude( estat__codi_estat__in = ['P','O']
                                                              ).filter(  
                                                        estat__isnull=False                                                          
                                                            )
        controlsNous = controls.filter( relacio_familia_revisada__isnull = True )
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Faltes i retards {0}'.format( pintaNoves( controlsNous.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        taula.fileres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 25
        capcelera.contingut = u'Dia' 
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 40
        capcelera.contingut = u'Falta, assignatura i franja horària.'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Notificada'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Revisada'
        taula.capceleres.append(capcelera)

        tots_els_controls = list( controls.select_related('impartir', 'estat').order_by( '-impartir__dia_impartir' , '-impartir__horari__hora') )
        
        assistencia_calendari = []  #{"date":"2016-04-02","badge":true,"title":"Example 2"}
        from itertools import groupby
        for k, g in groupby(tots_els_controls, lambda x: x.impartir.dia_impartir ):
            gs= list(g)
            gs.reverse()
            assistencia_calendari.append(   { 'date': k.strftime( '%Y-%m-%d' ),
                                              'badge': any( [ c.estat.codi_estat == 'F' for c in gs ] ),
                                              'title':  u'\n'.join(  [  escapejs(u'{0} a {1} ({2})'.format(
                                                                                     c.estat,
                                                                                     c.impartir.horari.assignatura,
                                                                                     c.impartir.horari.hora 
                                                                                                            )
                                                                                   )   
                                                                            for c in gs
                                                                        ] )      # Store group iterator as a list
                                             }
                                         )
        
        
        for control in tots_els_controls:
            
            filera = []
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = unicode(control.impartir.dia_impartir.strftime( '%d/%m/%Y' ))  
            camp.negreta = False if control.relacio_familia_revisada else True      
            filera.append(camp)
    
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} a {1} ({2})'.format(
                                                 control.estat,
                                                 control.impartir.horari.assignatura.nom_assignatura,
                                                 control.impartir.horari.hora 
                                    )        
            camp.negreta = False if control.relacio_familia_revisada else True      
            filera.append(camp)

            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(control.relacio_familia_notificada.strftime('%d/%m/%Y %H:%M')) if control.relacio_familia_notificada else ''
            camp.negreta = False if control.relacio_familia_revisada else True
            filera.append(camp)

            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(control.relacio_familia_revisada.strftime('%d/%m/%Y %H:%M')) if control.relacio_familia_revisada else ''
            camp.negreta = False if control.relacio_familia_revisada else True
            filera.append(camp)

#             assistencia_calendari.append(  { 'date': control.impartir.dia_impartir.strftime( '%Y-%m-%d' ) , 
#                                              'badge': control.estat.codi_estat == 'F', 
#                                              'title': escapejs( camp.contingut )
#                                             } )
    
            #--
            taula.fileres.append( filera )
    
        report.append(taula)    
        if not semiImpersonat:
            controlsNous.filter( relacio_familia_notificada__isnull = True ).update( relacio_familia_notificada = ara )
            controlsNous.update( relacio_familia_revisada = ara )           
    

        
    #----observacions --------------------------------------------------------------------
        observacions = alumne.incidencia_set.filter( tipus__es_informativa = True)
        observacionsNoves = observacions.filter(  relacio_familia_revisada__isnull = True)
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Observacions {0}'.format( pintaNoves( observacionsNoves.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Dia'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 50
        capcelera.contingut = u'Professor i observació.'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Notificada'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Revisada'
        taula.capceleres.append(capcelera)

        taula.fileres = []
    
        for incidencia in observacions.order_by( '-dia_incidencia', '-franja_incidencia' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( incidencia.dia_incidencia.strftime( '%d/%m/%Y' ))  
            camp.negreta = False if incidencia.relacio_familia_notificada else True
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.negreta = False if incidencia.relacio_familia_revisada else True
            camp.contingut = u'Sr(a): {0} - {1}'.format(incidencia.professional , 
                                                        incidencia.descripcio_incidencia )
            camp.negreta = False if incidencia.relacio_familia_revisada else True
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(incidencia.relacio_familia_notificada.strftime('%d/%m/%Y %H:%M')) if incidencia.relacio_familia_notificada else ''
            camp.negreta = False if incidencia.relacio_familia_revisada else True
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(incidencia.relacio_familia_revisada.strftime('%d/%m/%Y %H:%M')) if incidencia.relacio_familia_revisada else ''
            camp.negreta = False if incidencia.relacio_familia_revisada else True
            filera.append(camp)
            # ----------------------------------------------
            taula.fileres.append( filera )
        
        report.append(taula)
        if not semiImpersonat:
            observacionsNoves.filter( relacio_familia_notificada__isnull = True ).update( relacio_familia_notificada = ara )
            observacionsNoves.update( relacio_familia_revisada = ara )           
                    
    #----incidències --------------------------------------------------------------------
        incidencies = alumne.incidencia_set.filter( tipus__es_informativa = False )
        incidenciesNoves = incidencies.filter( relacio_familia_revisada__isnull = True )
    
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Incidències {0}'.format( pintaNoves(  incidenciesNoves.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Dia i estat'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 50
        capcelera.contingut = u'Professor i Incidència'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Notificada'
        taula.capceleres.append(capcelera)


        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Revisada'
        taula.capceleres.append(capcelera)

        taula.fileres = []
    
        for incidencia in incidencies.order_by( '-dia_incidencia', '-franja_incidencia' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1}'.format( incidencia.dia_incidencia.strftime( '%d/%m/%Y' ), 
                                                'Vigent' if incidencia.es_vigent else '')   
            camp.negreta = False if incidencia.relacio_familia_revisada else True      
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'Sr(a): {0} - {1}'.format(incidencia.professional , 
                                                        incidencia.descripcio_incidencia )        
            camp.negreta = False if incidencia.relacio_familia_revisada else True      
            filera.append(camp)

            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(incidencia.relacio_familia_notificada.strftime('%d/%m/%Y %H:%M')) if incidencia.relacio_familia_notificada else ''
            camp.negreta = False if incidencia.relacio_familia_revisada else True
            filera.append(camp)

            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(incidencia.relacio_familia_revisada.strftime('%d/%m/%Y %H:%M')) if incidencia.relacio_familia_revisada else ''
            camp.negreta = False if incidencia.relacio_familia_revisada else True
            filera.append(camp)

        #--
            taula.fileres.append( filera )            
    
        report.append(taula)
        if not semiImpersonat:
            incidenciesNoves.filter( relacio_familia_notificada__isnull = True ).update( relacio_familia_notificada = ara )
            incidenciesNoves.update( relacio_familia_revisada = ara )           
        

    #----Expulsions --------------------------------------------------------------------
        expulsions = alumne.expulsio_set.exclude( estat = 'ES' )
        expulsionsNoves = expulsions.filter( relacio_familia_revisada__isnull = True )
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Expulsions {0}'.format( pintaNoves( expulsionsNoves.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 10
        capcelera.contingut = u'Dia'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 10
        capcelera.contingut = u'Data comunicació'
        taula.capceleres.append(capcelera)
            
        capcelera = tools.classebuida()
        capcelera.amplade = 60
        capcelera.contingut = u'Professor i motiu'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Notificada'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Revisada'
        taula.capceleres.append(capcelera)

        taula.fileres = []
        
        for expulsio in expulsions.order_by( '-dia_expulsio', '-franja_expulsio' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1}'.format( expulsio.dia_expulsio.strftime( '%d/%m/%Y' ),
                                                u'''(per acumulació d'incidències)''' if expulsio.es_expulsio_per_acumulacio_incidencies else '')
            camp.negreta = False if expulsio.relacio_familia_revisada else True                      
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( expulsio.moment_comunicacio_a_tutors.strftime( '%d/%m/%Y' ) 
                                                     if expulsio.moment_comunicacio_a_tutors 
                                                     else u'Pendent de comunicar.')         
            camp.negreta = False if expulsio.relacio_familia_revisada else True                      
            filera.append(camp)            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'Sr(a): {0} - {1}'.format(                                                
                                               expulsio.professor , 
                                               expulsio.motiu if expulsio.motiu else u'Pendent redactar motiu.')        
            camp.negreta = False if expulsio.relacio_familia_revisada else True                      
            filera.append(camp)

            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(expulsio.relacio_familia_notificada.strftime('%d/%m/%Y %H:%M')) if expulsio.relacio_familia_notificada else ''
            camp.negreta = False if expulsio.relacio_familia_revisada else True
            filera.append(camp)

            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(expulsio.relacio_familia_revisada.strftime('%d/%m/%Y %H:%M')) if expulsio.relacio_familia_revisada else ''
            camp.negreta = False if expulsio.relacio_familia_revisada else True
            filera.append(camp)

            #--
            taula.fileres.append( filera )
            
        report.append(taula)        
        if not semiImpersonat:
            expulsionsNoves.filter( relacio_familia_notificada__isnull = True ).update( relacio_familia_notificada = ara )
            expulsionsNoves.update( relacio_familia_revisada = ara )           

    #----Sancions -----------------------------------------------------------------------------   
    if detall in ['all', 'incidencies']:
        sancions = alumne.sancio_set.filter( impres = True )
        sancionsNoves = sancions.filter(  relacio_familia_revisada__isnull = True )
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = 'Sancions {0}'.format( pintaNoves( sancionsNoves.count() ) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Dates'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 60
        capcelera.contingut = u'Detall'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Notificada'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Revisada'
        taula.capceleres.append(capcelera)

        taula.fileres = []
            
        for sancio in sancions.order_by( '-data_inici' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} a {1}'.format( sancio.data_inici.strftime( '%d/%m/%Y' ) ,  sancio.data_fi.strftime( '%d/%m/%Y' ))       
            camp.negreta = False if sancio.relacio_familia_revisada else True                
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1} {2}'.format( sancio.tipus , ' - ' if sancio.motiu else '', sancio.motiu )        
            camp.negreta = False if sancio.relacio_familia_revisada else True
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(sancio.relacio_familia_notificada.strftime('%d/%m/%Y %H:%M')) if sancio.relacio_familia_notificada else ''
            camp.negreta = False if sancio.relacio_familia_revisada else True
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(sancio.relacio_familia_revisada.strftime('%d/%m/%Y %H:%M')) if sancio.relacio_familia_revisada else ''
            camp.negreta = False if sancio.relacio_familia_revisada else True
            filera.append(camp)
            #--
            taula.fileres.append( filera )
    
        report.append(taula)
        if not semiImpersonat:
            sancionsNoves.filter( relacio_familia_notificada__isnull = True ).update( relacio_familia_notificada = ara )
            sancionsNoves.update( relacio_familia_revisada = ara )           

    #---dades alumne---------------------------------------------------------------------
    if detall in ['all','dades']:
        taula = tools.classebuida()
        taula.tabTitle = 'Dades personals'
    
        taula.codi = nTaula; nTaula+=1
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 25
        capcelera.contingut = u'Dades Alumne'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 75
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)
        
        taula.fileres = []
    
            #----grup------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Grup'        
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format( alumne.grup )        
        filera.append(camp)
    
        taula.fileres.append( filera )
    
            #----data neix------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Data Naixement'        
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = formats.date_format(alumne.data_neixement, "SHORT_DATE_FORMAT") 
        filera.append(camp)
    
        taula.fileres.append( filera )
    
    
        #----Pares------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Responsables'
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None

        camp.multipleContingut = [(alumne.rp1_nom, None),
                                  (alumne.rp2_nom,None),
                                  ]
        filera.append(camp)
    
        taula.fileres.append( filera )
    
            #----adreça------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Adreça'        
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None
        localitat_i_o_municipi = alumne.localitat if not alumne.municipi \
            else (alumne.municipi if not alumne.localitat
                  else (alumne.localitat + '-' + alumne.municipi if alumne.localitat != alumne.municipi
                        else alumne.localitat))
        camp.contingut = u'{0} - {1}'.format(alumne.adreca, localitat_i_o_municipi)
        filera.append(camp)
    
        taula.fileres.append( filera )

        # # ----dades addicionals-----------------------------------------
        if CUSTOM_DADES_ADDICIONALS_ALUMNE:
            dades_addicionals = DadesAddicionalsAlumne.objects.filter(alumne=alumne)
            labels = [x['label'] for x in CUSTOM_DADES_ADDICIONALS_ALUMNE]
            for dada_addicional in dades_addicionals:
                element = next((item for item in CUSTOM_DADES_ADDICIONALS_ALUMNE if item["label"] == dada_addicional.label), None)
                if element and dada_addicional.label in labels and 'Familia' in element['visibilitat']:
                    filera = []
                    camp = tools.classebuida()
                    camp.enllac = None
                    camp.contingut = dada_addicional.label
                    filera.append(camp)

                    camp = tools.classebuida()
                    camp.enllac = None
                    dada_camp = dada_addicional.value
                    camp.contingut = dada_camp
                    filera.append(camp)

                    taula.fileres.append(filera)

        report.append(taula)

    infSortida=detall in ['all', 'sortides'] and settings.CUSTOM_MODUL_SORTIDES_ACTIU
    pagquotes = QuotaPagament.objects.filter(alumne=alumne, quota__importQuota__gt=0)
    pagquotesNoves = pagquotes.filter(pagament_realitzat=False)
    infQuota=detall in ['all', 'sortides'] and (pagquotes or settings.CUSTOM_QUOTES_ACTIVES)

    titol_sortides = 'Activitats/Pagaments'
    
    
    #----Sortides -----------------------------------------------------------------------------   
    if infSortida:
        sortides = alumne.notificasortida_set.all()
        
        # sortides a on s'ha convocat a l'alumne
        sortidesnotificat = Sortida.objects.filter(notificasortida__alumne=alumne)
        # sortides pagades a les que ja no s'ha convocat a l'alumne
        sortidespagadesperalumne = SortidaPagament.objects.filter(alumne=alumne, pagament_realitzat=True).values_list('sortida', flat=True).distinct()
        sortidespagadesnonotificades = Sortida.objects.filter(id__in=sortidespagadesperalumne, pagaments__pagament__alumne=alumne, pagaments__pagament__pagament_realitzat=True).exclude(notificasortida__alumne=alumne)
        # totes les sortides relacionades amb l'alumne
        activitats=sortidesnotificat.union(sortidespagadesnonotificades)
        
        sortidesNoves = sortides.filter(  relacio_familia_revisada__isnull = True )
        sortides_on_no_assistira = alumne.sortides_on_ha_faltat.values_list( 'id', flat=True ).distinct()           
        sortides_justificades = alumne.sortides_falta_justificat.values_list( 'id', flat=True ).distinct()           
        
        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = '{0} {1}'.format( titol_sortides, pintaNoves( sortidesNoves.count() + pagquotesNoves.count()) )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Dates'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 25
        capcelera.contingut = u' '
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 25
        capcelera.contingut = u'Detall'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Notificada'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Revisada'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 10
        capcelera.contingut = u' '
        taula.capceleres.append(capcelera)
                
        taula.fileres = []
            
        for act in activitats.order_by( '-calendari_desde' ):
            # notifica és la notificació a l'alumne
            notifica=act.notificasortida_set.filter(alumne=alumne)
            if notifica:
                notifica=notifica[0]
            else:
                notifica=None
            
            filera = []
            revisada_per_la_familia = not notifica or bool( notifica.relacio_familia_revisada )
            negreta = not revisada_per_la_familia
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            if act.tipus=='P':
                camp.contingut = naturalday(act.termini_pagament)
            else:              
                camp.contingut = naturalday(act.calendari_desde)       
            camp.negreta = negreta
            filera.append(camp)
            
            #----------------------------------------------
            #  NO INSCRIT A L’ACTIVITAT. L'alumne ha d'assistir al centre excepte si són de viatge de final de curs. 
            comentari_no_ve = u""            
            if act.pk in sortides_on_no_assistira:
                comentari_no_ve = u"NO INSCRIT A L’ACTIVITAT."
                if act.pk in sortides_justificades:
                    comentari_no_ve += u"NO INSCRIT A L’ACTIVITAT. Té justificada l'absència."

            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = comentari_no_ve       
            camp.negreta = negreta
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( act.titol )
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(notifica.relacio_familia_notificada.strftime('%d/%m/%Y %H:%M')) if notifica and notifica.relacio_familia_notificada else ''
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(notifica.relacio_familia_revisada.strftime('%d/%m/%Y %H:%M')) if notifica and notifica.relacio_familia_revisada else ''
            camp.negreta = negreta
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.modal = {}
            camp.modal['id'] = act.id
            camp.modal['txtboto'] = u'Detalls' 
            camp.modal['tittle'] =  u"{0} ({1})".format( 
                                        act.titol,
                                        naturalday(act.calendari_desde),
                                        )
            if act.tipus=='P':
                camp.modal['body'] =  u'{0}\n{1}\n{2}\n{3}\n{4}'.format(
                                            act.programa_de_la_sortida,
                                            act.condicions_generals,
                                            act.informacio_pagament,
                                            u'Preu: {0} €'.format(str(act.preu_per_alumne)) if act.preu_per_alumne else u'Preu: 0 €',
                                            u'Data límit pagament: {0}'.format(str(act.termini_pagament)) if act.termini_pagament else ''
                                            )
            else:
                camp.modal['body'] =  u'Del {0} al {1} \n\n{2}\n{3}\n{4}\n{5}\n{6}'.format(
                                            act.calendari_desde.strftime( '%d/%m/%Y %H:%M' ),  
                                            act.calendari_finsa.strftime( '%d/%m/%Y %H:%M' ),                                        
                                            act.programa_de_la_sortida,
                                            act.condicions_generals,
                                            act.informacio_pagament,
                                            u'Preu: {0} €'.format(str(act.preu_per_alumne)) if act.preu_per_alumne else u'Preu: 0 €',
                                            u'Data límit pagament: {0}'.format(str(act.termini_pagament)) if act.termini_pagament else ''
                                            )
            filera.append(camp)

            # ----------------------------------------------
            if act.tipus_de_pagament == 'ON':
                alumnat_tret_de_lactivitat = act.alumnes_que_no_vindran.all().union(
                    act.alumnes_justificacio.all())
                alumne_tret_de_lactivitat = alumne in alumnat_tret_de_lactivitat
                camp = tools.classebuida()
                camp.nexturl = reverse_lazy('relacio_families__informe__el_meu_informe')
                #pagament corresponent a una sortida i un alumne
                if not alumne_tret_de_lactivitat:
                    pagament_sortida_alumne = get_object_or_404(SortidaPagament, alumne=alumne, sortida=act)
                    camp.id = pagament_sortida_alumne.id
                    # Pagaments pendents o ja fets. Si sortida caducada no mostra pagament pendent.
                    if (act.termini_pagament and act.termini_pagament >= datetime.now()) or not bool(act.termini_pagament) or pagament_sortida_alumne.pagamentFet:
                        if pagament_sortida_alumne.pagamentFet:
                            camp.negreta = True
                            camp.contingut = "Pagat"
                        else:
                            if settings.CUSTOM_SORTIDES_PAGAMENT_ONLINE:
                                camp.buto = u'sortides__sortides__pago_on_line'
                                camp.contingut = "Pagar Online"
                else:
                        camp.negreta = True
                        camp.contingut = "Baixa de l'activitat/pagament"
                filera.append(camp)

            #--
            taula.fileres.append( filera )

        if not infQuota: report.append(taula)

        if not semiImpersonat:
            sortidesNoves.filter( relacio_familia_notificada__isnull = True ).update( relacio_familia_notificada = ara )
            sortidesNoves.update( relacio_familia_revisada = ara )           

    #----Quotes -----------------------------------------------------------------------------   
    if infQuota:
        if not infSortida:
            taula = tools.classebuida()
            taula.codi = nTaula; nTaula+=1
            taula.tabTitle = titol_sortides
            taula.tabTitle = '{0} {1}'.format( titol_sortides, pintaNoves( pagquotesNoves.count() ) )
        
            taula.titol = tools.classebuida()
            taula.titol.contingut = ''
            taula.titol.enllac = None
        
            taula.capceleres = []
            
            capcelera = tools.classebuida()
            capcelera.amplade = 15
            capcelera.contingut = u'Dates'
            capcelera.enllac = ""
            taula.capceleres.append(capcelera)
        
            capcelera = tools.classebuida()
            capcelera.amplade = 25
            capcelera.contingut = u' '
            capcelera.enllac = ""
            taula.capceleres.append(capcelera)
        
            capcelera = tools.classebuida()
            capcelera.amplade = 25
            capcelera.contingut = u'Detall'
            taula.capceleres.append(capcelera)
    
            capcelera = tools.classebuida()
            capcelera.amplade = 20
            capcelera.contingut = u'Notificada'
            taula.capceleres.append(capcelera)
    
            capcelera = tools.classebuida()
            capcelera.amplade = 20
            capcelera.contingut = u'Revisada'
            taula.capceleres.append(capcelera)
    
            capcelera = tools.classebuida()
            capcelera.amplade = 10
            capcelera.contingut = u' '
            taula.capceleres.append(capcelera)
                    
            taula.fileres = []

        for pagquota in pagquotes.order_by( '-quota__any', '-quota__dataLimit', 'dataLimit' ):
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = naturalday(pagquota.getdataLimit)
            camp.negreta = not bool( pagquota.pagamentFet )
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = ''       
            camp.negreta = not bool( pagquota.pagamentFet )
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( pagquota.quota.descripcio )        
            camp.negreta = not bool( pagquota.pagamentFet )
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = pagquota.data_hora_pagament.strftime('%d/%m/%Y %H:%M') if pagquota.data_hora_pagament and not pagquota.pagamentFet else ''
            camp.negreta = not bool( pagquota.pagamentFet )
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = pagquota.data_hora_pagament.strftime('%d/%m/%Y %H:%M') if pagquota.data_hora_pagament and pagquota.pagamentFet else ''
            camp.negreta = not bool( pagquota.pagamentFet )
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.modal = {}
            camp.modal['id'] = pagquota.id 
            camp.modal['txtboto'] = u'Detalls' 
            camp.modal['tittle'] =  u"{0} ({1})".format( 
                                        pagquota.quota.descripcio,
                                        naturalday(pagquota.quota.any),
                                        )
            valor=pagquota.importReal
            camp.modal['body'] =  u'{0}\n{1}\n{2}'.format(
                                        settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ONLINE if settings.CUSTOM_SORTIDES_PAGAMENT_ONLINE else \
                                        settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT_ENTITAT_BANCARIA if settings.CUSTOM_SORTIDES_PAGAMENT_CAIXER else \
                                        settings.CUSTOM_SORTIDES_INSTRUCCIONS_PAGAMENT,
                                        u'Preu: {0} €'.format(valor),
                                        u'Data límit pagament: {0}'.format(str(pagquota.getdataLimit)) if pagquota.getdataLimit else ''
                                  )
            filera.append(camp)

            # ----------------------------------------------
            camp = tools.classebuida()
            camp.id = pagquota.id
            camp.nexturl = reverse_lazy('relacio_families__informe__el_meu_informe')
            if pagquota.pagamentFet:
                camp.negreta = True
                camp.contingut = "Pagat"
            else:
                if settings.CUSTOM_SORTIDES_PAGAMENT_ONLINE:
                    camp.buto = u'sortides__sortides__pago_on_line'
                    camp.contingut = "Pagar Online"
                else:
                    camp.buto = None
                    camp.contingut = ""
                    
            filera.append(camp)

            #--
            taula.fileres.append( filera )
    
        report.append(taula)

    #----Qualitativa -----------------------------------------------------------------------------
    qualitatives_alumne= { r.qualitativa for r in alumne.respostaavaluacioqualitativa_set.all() }
    avui = datetime.now().date()
    qualitatives_en_curs = [ q for q in qualitatives_alumne
                               if ( bool(q.data_obrir_portal_families) and
                                    bool( q.data_tancar_tancar_portal_families ) and 
                                    q.data_obrir_portal_families <= avui <= q.data_tancar_tancar_portal_families
                                   )
                           ]

    if detall in ['all', 'qualitativa'] and qualitatives_en_curs:
        
        respostes = alumne.respostaavaluacioqualitativa_set.filter( qualitativa__in = qualitatives_en_curs )
        respostesNoves = respostes.filter( relacio_familia_revisada__isnull = True )

        assignatures = list(set( [r.assignatura for r in respostes] ))
        hi_ha_tipus_assignatura = ( bool(assignatures)
                                    and assignatures[0]
                                    and assignatures[0].tipus_assignatura is not None
                                    and assignatures[0].tipus_assignatura.capcelera
                                    )
        asignatura_label = assignatures[0].tipus_assignatura.capcelera if hi_ha_tipus_assignatura else u"Matèria"

        taula = tools.classebuida()
        taula.codi = nTaula; nTaula+=1
        taula.tabTitle = u"Avaluació qualitativa {0}".format( u"!" if respostesNoves.exists() else "" )
    
        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None
    
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Qualitativa'
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = asignatura_label
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)
    
        capcelera = tools.classebuida()
        capcelera.amplade = 45
        capcelera.contingut = u''
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Notificada'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 20
        capcelera.contingut = u'Revisada'
        taula.capceleres.append(capcelera)

        taula.fileres = []

        respostes_pre = ( respostes
                          .order_by( 'qualitativa__data_obrir_avaluacio','assignatura' )
                         )
        
        keyf = lambda x: (x.qualitativa.nom_avaluacio + x.assignatura.nom_assignatura)
        respostes_sort=sorted( respostes_pre, key=keyf )
        from itertools import groupby
             
        for _ , respostes in groupby( respostes_sort, keyf ):
            respostes=list(respostes)
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = respostes[0].qualitativa.nom_avaluacio       
            camp.negreta = False if bool( respostes[0].relacio_familia_revisada ) else True                
            filera.append(camp)

            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = respostes[0].assignatura.nom_assignatura or respostes[0].assignatura
            camp.negreta = False if bool( respostes[0].relacio_familia_revisada ) else True                
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.multipleContingut = []
            for resposta in respostes:
                camp.multipleContingut.append( ( u'{0}'.format( resposta.get_resposta_display() ), None, ) )        
            camp.negreta = False if respostes[0].relacio_familia_revisada else True                
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(respostes[0].relacio_familia_notificada.strftime('%d/%m/%Y %H:%M')) if respostes[0].relacio_familia_notificada else ''
            camp.negreta = False if bool(respostes[0].relacio_familia_revisada) else True
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(respostes[0].relacio_familia_revisada.strftime('%d/%m/%Y %H:%M')) if respostes[0].relacio_familia_revisada else ''
            camp.negreta = False if bool(respostes[0].relacio_familia_revisada) else True
            filera.append(camp)

            #--
            taula.fileres.append( filera )
    
        report.append(taula)
        if not semiImpersonat:
            respostesNoves.filter( relacio_familia_notificada__isnull = True ).update( relacio_familia_notificada = ara )
            respostesNoves.update( relacio_familia_revisada = ara )           

    return render(
                request,
                'report_detall_families.html',
                    {'report': report,
                     'head': u'Informació alumne {0}'.format( head ) ,
                     'assistencia_calendari': json.dumps(  assistencia_calendari ),
                    },
                )



def pintaNoves( numero ):
    txt = ''
    if numero == 1:
        txt = u'({0} nova)'.format( numero ) 
    elif numero > 1:
        txt = u'({0} noves)'.format( numero )
    return txt

def blanc(request):
    return render(request, 'blanc.html', {},)
