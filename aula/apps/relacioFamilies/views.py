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
from aula.apps.sortides.models import Sortida, NotificaSortida, SortidaPagament, QuotaPagament, Pagament
from aula.apps.relacioFamilies.forms import AlumneModelForm, comunicatForm, escollirAlumneForm, ResponsableModelForm
from aula.apps.relacioFamilies.models import Responsable
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
from aula.apps.usuaris.models import User2Professor, AlumneUser, User2Responsable, User2Alumne
from aula.apps.tutoria.models import Tutor
from aula.utils.decorators import group_required

from django.db.models import Q
from django.forms.models import modelform_factory, modelformset_factory
from datetime import datetime, timedelta

from aula.apps.usuaris.tools import enviaBenvingudaAlumne, bloqueja, desbloqueja, testEmail, getRol, creaNotifUsuari

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
    # TODO fa falta aquesta view ?
    # Si fa falta, s'hauria de replantejar afegint els responsables.
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
    seg_tutor_de_lalumne = seg_es_tutor = False
    if pk:
        alumne = get_object_or_404(Alumne, pk=pk) if pk else None
        alumnes = [alumne, ]
        seg_tutor_de_lalumne = pk and professor in alumne.tutorsDeLAlumne()
    else:
        els_meus_alumnes_de_grups_tutorats = [a for t in professor.tutor_set.all()
                                              for a in t.grup.alumne_set.all()]
        els_meus_tutorats_individualitzats = [t.alumne for t in professor.tutorindividualitzat_set.all()]
        alumnes = els_meus_alumnes_de_grups_tutorats + els_meus_tutorats_individualitzats
        seg_es_tutor = professor.tutor_set.exists() or professor.tutorindividualitzat_set.exists()
    # seg-------------------
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
        filename = "QR-{0}.odt".format("{0}-{1}".format(alumne.cognoms, alumne.nom) if pk else "Tot l'alumnat")
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
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
        menuCTX = list({"/open/qrTokens/": "Genera nous codis QR per a tot el grup"}.items())
        return render(
            request,
            'report.html',
            {'report': report,
             'head': "QR's dels meus tutorats",
             'menuCTX' : menuCTX,
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

    resps = alumne.get_dades_responsables()
    
    infoForm = [
          ('Alumne',unicode( alumne) ),
          ('Edat alumne', edatAlumne),
          ('Responsable preferent', resps['respPre']),
          ('Responsable (altre)', resps['respAlt']),
          ('Altres telèfons', alumne.get_telefons()),
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
    ResponsableFormSet = modelform_factory(Responsable,
                                          form=ResponsableModelForm
                                        )
    
    resp1, resp2 = alumne.get_responsables(compatible=True)
    
    if request.method == 'POST':
        formAlmn = AlumneFormSet(True, request.POST, request.FILES, instance=alumne)
        if resp1: formResp1 = ResponsableFormSet('resp1', request.POST, request.FILES, instance=resp1)
        if resp2: formResp2 = ResponsableFormSet('resp2', request.POST, request.FILES, instance=resp2)
        hihaerrors=False
        if formAlmn.is_valid() and (not resp1 or formResp1.is_valid()) and (not resp2 or formResp2.is_valid()):
            #Comprova els dominis de correu
            errors = {}
            email=formAlmn.cleaned_data['correu']
            res, email = testEmail(email, False)
            if res<-1:
                errors.setdefault('correu', []).append(u'''Adreça no vàlida''')
            if len(errors)>0:
                formAlmn._errors.update(errors)
                hihaerrors=True
            else:
                formAlmn.save()
            if resp1:
                errors = {}
                email=formResp1.cleaned_data['correu_relacio_familia']
                res, email = testEmail(email, False)
                if res<-1:
                    errors.setdefault('correu_relacio_familia', []).append(u'''Adreça no vàlida''')
                if len(errors)>0:
                    formResp1._errors.update(errors)
                    hihaerrors=True
                else:
                    if resp1.dni: formResp1.save()
            if resp2:
                errors = {}
                email=formResp2.cleaned_data['correu_relacio_familia']
                res, email = testEmail(email, False)
                if res<-1:
                    errors.setdefault('correu_relacio_familia', []).append(u'''Adreça no vàlida''')
                if len(errors)>0:
                    formResp2._errors.update(errors)
                    hihaerrors=True
                else:
                    if resp2.dni: formResp2.save()
            url_next = '/open/dadesRelacioFamilies#{0}'.format(alumne.pk  ) 
            if not hihaerrors: return HttpResponseRedirect( url_next )

    else:
        formAlmn = AlumneFormSet(True, instance=alumne)
        if resp1: formResp1 = ResponsableFormSet('resp1', instance=resp1)
        if resp2: formResp2 = ResponsableFormSet('resp2', instance=resp2)
        
    formset=[]
    formAlmn.infoForm=infoForm
    formset.append( formAlmn )
    if resp1: formset.append( formResp1 )
    if resp2: formset.append( formResp2 )
    
    return render(
                request,
                'configuraConnexio.html',
                    {'formset': formset,
                     'image': imageUrl,
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
                (u'activitats o pagaments', NotificaSortida,),
                (u'incidencies o observacions', Incidencia,),
                (u'sanció(ns)', Sancio,),
                (u'expulsió(ns)', Expulsio,),
                (u'faltes assistència', ControlAssistencia,),
                (u'pagament(s)', QuotaPagament,),
            ]

            familia_pendent_de_mirar = {}
            for codi, model in familia_pendent_de_mirar_models:
                familia_pendent_de_mirar[codi]= ( model
                                                    .objects
                                                    .filter( alumne__in = alumnes )
                                                    .filter( notificacions_familia__tipus = 'N' )
                                                    .exclude( notificacions_familia__tipus = 'R' )
                                                    .distinct()
                                                  )
                #DEPRECATED vvv
                # Per compatibilitat amb dades existents
                try:
                    avui = datetime.now().date()
                    if codi==u'pagament(s)':
                        comp_pendent_de_mirar= ( model
                                                   .objects
                                                   .filter( alumne__in = alumnes )
                                                   .filter( data_hora_pagament__isnull = True )
                                                   .exclude( pagament_realitzat = True )
                                                   .exclude( notificacions_familia__tipus = 'R' )
                                                   .distinct()
                                                 )
                    elif codi==u'activitats o pagaments':
                        comp_pendent_de_mirar= ( model
                                                   .objects
                                                   .filter( alumne__in = alumnes )
                                                   .exclude( sortida__data_fi__lt = avui )
                                                   .filter( relacio_familia_revisada__isnull = True )
                                                   .filter( relacio_familia_notificada__isnull = False )
                                                   .exclude( notificacions_familia__tipus = 'R' )
                                                   .distinct()
                                                 )
                    elif codi==u'qualitativa':
                        comp_pendent_de_mirar= ( model
                                                   .objects
                                                   .filter( alumne__in = alumnes )
                                                   .exclude( qualitativa__data_tancar_tancar_portal_families__lt = avui )
                                                   .filter( relacio_familia_revisada__isnull = True )
                                                   .filter( relacio_familia_notificada__isnull = False )
                                                   .exclude( notificacions_familia__tipus = 'R' )
                                                   .distinct()
                                                 )
                    elif codi==u'faltes assistència':
                        comp_pendent_de_mirar= ( model
                                                   .objects
                                                   .filter( alumne__in = alumnes )
                                                   .exclude(estat__codi_estat__in = ['P','O'])
                                                   .filter( relacio_familia_revisada__isnull = True )
                                                   .filter( relacio_familia_notificada__isnull = False )
                                                   .exclude( notificacions_familia__tipus = 'R' )
                                                   .distinct()
                                                 )
                    else:
                        comp_pendent_de_mirar= ( model
                                                   .objects
                                                   .filter( alumne__in = alumnes )
                                                   .filter( relacio_familia_revisada__isnull = True )
                                                   .filter( relacio_familia_notificada__isnull = False )
                                                   .exclude( notificacions_familia__tipus = 'R' )
                                                   .distinct()
                                                 )
                except:
                    comp_pendent_de_mirar=model.objects.none()

                familia_pendent_de_mirar[codi] = model.objects.filter(Q(pk__in=familia_pendent_de_mirar[codi]) | Q(pk__in=comp_pendent_de_mirar)).distinct()
                #DEPRECATED ^^^

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
                dataDarreraConnexio = []
                bloquejat_text =  [ ( alumne.motiu_bloqueig, None ), ] if  alumne.motiu_bloqueig else []
                nConnexions = alumne.user_associat.LoginUsuari.filter(exitos=True).count()
                if nConnexions > 0:
                    dataDarreraConnexio.append(alumne.user_associat.LoginUsuari.filter(exitos=True).order_by( '-moment' )[0].moment)
                for r in alumne.get_responsables():
                    if not r: continue
                    if not bool(r.motiu_bloqueig): bloquejat_text = []
                    if r.get_user_associat(): count = r.get_user_associat().LoginUsuari.filter(exitos=True).count()
                    else: count=0
                    nConnexions = nConnexions + count
                    if count > 0:
                        dataDarreraConnexio.append(r.get_user_associat().LoginUsuari.filter(exitos=True).order_by( '-moment' )[0].moment)
                camp.multipleContingut = bloquejat_text + [ ( u'( {0} connexs. )'.format(nConnexions) , None, ), ]
                if nConnexions > 0:
                    camp.multipleContingut.append( ( u'Darrera Connx: {0}'.format(  max(dataDarreraConnexio).strftime( '%d/%m/%Y' ) ), None, ) )
                for ambit in familia_pendent_de_mirar:
                    if familia_pendent_de_mirar[ambit].filter(alumne=alumne.pk).exists():
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

    _, responsable, alumne = getRol( user, request )
    if not alumne: return HttpResponseRedirect('/')
    edatAlumne = None
    try:
        if alumne: edatAlumne = alumne.edat()
    except:
        pass
    
    if responsable:
        resps = alumne.get_dades_responsables(responsable=responsable)
    elif alumne:
        resps = alumne.get_dades_responsables(nomesNoms=True)
    dades1 = resps['respPre']
    dades2 = resps['respAlt']
    
    infoForm = [
        ('Alumne', unicode(alumne)),
        ('Edat alumne', str(edatAlumne) + ' (' + formats.date_format(alumne.data_neixement, "SHORT_DATE_FORMAT") + ')' ),
        ('RALC', alumne.ralc),
        ('Responsable', dades1),
        ]
    if dades2: infoForm.append(('Responsable', dades2))
    infoForm.append(('Altres telèfons', alumne.get_telefons()))
        
    
    AlumneFormSet = modelform_factory(Alumne,
                                      form=AlumneModelForm,
                                      widgets={
                                          'foto': FileInput,}
                                         )
    if responsable:
        ResponsableFormSet = modelform_factory(Responsable,
                                          form=ResponsableModelForm
                                        )
    
    if request.method == 'POST':
        formAlmn = AlumneFormSet(False, request.POST, request.FILES, instance=alumne)
        if responsable: formResp = ResponsableFormSet('resp', request.POST, request.FILES, instance=responsable)
        hihaerrors=False
        if formAlmn.is_valid() and (not responsable or formResp.is_valid()):
            #Comprova els dominis de correu
            errors = {}
            email=formAlmn.cleaned_data['correu']
            res, email = testEmail(email, False)
            if res<-1:
                errors.setdefault('correu', []).append(u'''Adreça no vàlida''')
            if len(errors)>0:
                formAlmn._errors.update(errors)
                hihaerrors=True
            else:
                formAlmn.save()
            if responsable: 
                errors = {}
                email=formResp.cleaned_data['correu_relacio_familia']
                res, email = testEmail(email, False)
                if res<-1:
                    errors.setdefault('correu_relacio_familia', []).append(u'''Adreça no vàlida''')
                if len(errors)>0:
                    formResp._errors.update(errors)
                    hihaherrors=True
                else:
                    formResp.save()
            if not hihaerrors:
                return HttpResponseRedirect( '/open/elMeuInforme/' )

    else:
        formAlmn = AlumneFormSet(False, instance=alumne)
        if responsable: formResp = ResponsableFormSet('resp', instance=responsable)

    formset=[]
    formAlmn.infoForm=infoForm
    formset.append( formAlmn )
    if responsable: formset.append( formResp )

    return render(
                request,
                'configuraConnexio.html',
                    {'formset': formset,
                     'image': alumne.get_foto_or_default,
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

    _, responsable, alumne = getRol( user, request )
    if not alumne or (not responsable and alumne.edat()<18):
        messages.info( request, u"Els comunicats d'alumnes menors d'edat els ha de fer un responsable." )
        return HttpResponseRedirect('/')
    
    ara=datetime.now()
    primerdia=properdiaclasse(alumne, ara)
    if not primerdia:
        messages.info( request, u"No és possible fer comunicats. No té programada cap classe." )
        return HttpResponseRedirect('/')

    if primerdia > (ara+timedelta(days=diesantelacio)).date():
        messages.info( request, 
                u"Només es poden fer comunicats amb antelació màxima d'una setmana. La següent classe serà el dia {0}."\
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
            enviaMsg(alumne.get_user_associat(), credentials, alumne, datai, horai, dataf, horaf, motiu, observ)
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
    
    _, responsable, alumne = getRol( user, request )
    if not alumne: return HttpResponseRedirect('/')
    q = alumne.get_user_associat().missatge_set.filter(tipus_de_missatge=tipus)

    table = ComunicatsTable(q)
    RequestConfig(request, paginate={"paginator_class":DiggPaginator , "per_page": 25}).configure(table)
  
    return render(
                    request,
                    'table2.html',
                    {'table': table,
                    },
                 )

def getNousElements(elements, user):
    '''
    Busca elements no revisats a "elements", comprova també si tenen pendent la notificació.
    elements  Query amb els elements a comprovar si n'hi ha de nous, es a dir, no revisats.
    user      Usuari, pot ser: professor, responsable o alumne.
    Retorna   Query amb els elements no revisats nous trobats i un boolean indicant si tenen pendent la notificació (True o False).
    '''
    #DEPRECATED vvv
    # Per compatibilitat amb dades existents
    try:
        if elements.filter( relacio_familia_notificada__isnull = False ):
            elements = elements.exclude( relacio_familia_revisada__isnull = False )
    except:
        pass
    #DEPRECATED ^^^
    if User2Professor( user ):
        Nous = elements.exclude( notificacions_familia__tipus = 'R' )
        return Nous, False
    else:
        useralum = Q(notificacions_familia__usuari = user)
        Nous = elements.exclude( useralum & Q(notificacions_familia__tipus = 'R') )
        Notificats = Nous.filter( useralum & Q(notificacions_familia__tipus = 'N') )
        return Nous, (Nous.count()-Notificats.count())>0
    
@login_required
def elMeuInforme( request, pk = None ):
    """Dades que veurà l'alumne"""
    
    detall = 'all'

    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
    nTaula = 0
    
    tePermis = True
    semiImpersonat = False
    professor, responsable, alumne = getRol(user, request )
    if pk and professor:
        try:
            alumne =  Alumne.objects.get( pk = pk )   
            tePermis = professor in alumne.tutorsDeLAlumne()
            semiImpersonat = True
        except Exception as e:
            tePermis = False 
    
    if not alumne or not tePermis:
        if responsable:
            # Selecciona l'alumne del responsable
            return HttpResponseRedirect('/open/escollirAlumne/')
        raise Http404 
    
    head = u'{0} ({1})'.format(alumne , unicode( alumne.grup ) )
    
    ara = datetime.now()
    notifAlumne=None
    revisAlumne=None
    
    report = []

    #----Assistencia --------------------------------------------------------------------
    if detall in ['all', 'assistencia']:
        controls = alumne.controlassistencia_set.exclude( estat__codi_estat__in = ['P','O']
                                                              ).filter(  
                                                        estat__isnull=False                                                          
                                                            )
        controlsNous, creaNotif = getNousElements(controls, user)
        if creaNotif and not notifAlumne: notifAlumne=creaNotifUsuari(user, alumne, 'N')
        if controlsNous and not revisAlumne: revisAlumne=creaNotifUsuari(user, alumne, 'R')
            
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
            
            notificacio, revisio = control.get_notif_revisio(user)
            negreta = False if revisio else True
            
            filera = []
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = unicode(control.impartir.dia_impartir.strftime( '%d/%m/%Y' ))  
            camp.negreta = negreta
            filera.append(camp)
    
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} a {1} ({2})'.format(
                                                 control.estat,
                                                 control.impartir.horari.assignatura.nom_assignatura,
                                                 control.impartir.horari.hora 
                                    )        
            camp.negreta = negreta
            filera.append(camp)

            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(notificacio)
            camp.negreta = negreta
            filera.append(camp)

            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(revisio)
            camp.negreta = negreta
            filera.append(camp)

            #--
            taula.fileres.append( filera )
            if not semiImpersonat:
                if not notificacio: control.set_notificacio(notifAlumne)
                if not revisio: control.set_revisio(revisAlumne)
                
        report.append(taula)    
        
    #----observacions --------------------------------------------------------------------
        observacions = alumne.incidencia_set.filter( tipus__es_informativa = True)
        observacionsNoves, creaNotif = getNousElements(observacions, user)
        if creaNotif and not notifAlumne: notifAlumne=creaNotifUsuari(user, alumne, 'N')
        if observacionsNoves and not revisAlumne: revisAlumne=creaNotifUsuari(user, alumne, 'R')
            
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
            notificacio, revisio = incidencia.get_notif_revisio(user)
            negreta = False if revisio else True
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( incidencia.dia_incidencia.strftime( '%d/%m/%Y' ))  
            camp.negreta = negreta
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'Sr(a): {0} - {1}'.format(incidencia.professional , 
                                                        incidencia.descripcio_incidencia )
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(notificacio)
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(revisio)
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            taula.fileres.append( filera )
            if not semiImpersonat:
                if not notificacio: incidencia.set_notificacio(notifAlumne)
                if not revisio: incidencia.set_revisio(revisAlumne)
            
        report.append(taula)      
        
    #----incidències --------------------------------------------------------------------
        incidencies = alumne.incidencia_set.filter( tipus__es_informativa = False )
        incidenciesNoves, creaNotif = getNousElements(incidencies, user)
        if creaNotif and not notifAlumne: notifAlumne=creaNotifUsuari(user, alumne, 'N')
        if incidenciesNoves and not revisAlumne: revisAlumne=creaNotifUsuari(user, alumne, 'R')
            
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
            notificacio, revisio = incidencia.get_notif_revisio(user)
            negreta = False if revisio else True
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1}'.format( incidencia.dia_incidencia.strftime( '%d/%m/%Y' ), 
                                                'Vigent' if incidencia.es_vigent else '')   
            camp.negreta = negreta
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'Sr(a): {0} - {1}'.format(incidencia.professional , 
                                                        incidencia.descripcio_incidencia )        
            camp.negreta = negreta
            filera.append(camp)

            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(notificacio)
            camp.negreta = negreta
            filera.append(camp)

            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(revisio)
            camp.negreta = negreta
            filera.append(camp)

        #--
            taula.fileres.append( filera )            
            if not semiImpersonat:
                if not notificacio: incidencia.set_notificacio(notifAlumne)
                if not revisio: incidencia.set_revisio(revisAlumne)
                    
        report.append(taula)
        

    #----Expulsions --------------------------------------------------------------------
        expulsions = alumne.expulsio_set.exclude( estat = 'ES' )
        expulsionsNoves, creaNotif = getNousElements(expulsions, user)
        if creaNotif and not notifAlumne: notifAlumne=creaNotifUsuari(user, alumne, 'N')
        if expulsionsNoves and not revisAlumne: revisAlumne=creaNotifUsuari(user, alumne, 'R')
            
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
            notificacio, revisio = expulsio.get_notif_revisio(user)
            negreta = False if revisio else True
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1}'.format( expulsio.dia_expulsio.strftime( '%d/%m/%Y' ),
                                                u'''(per acumulació d'incidències)''' if expulsio.es_expulsio_per_acumulacio_incidencies else '')
            camp.negreta = negreta
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( expulsio.moment_comunicacio_a_tutors.strftime( '%d/%m/%Y' ) 
                                                     if expulsio.moment_comunicacio_a_tutors 
                                                     else u'Pendent de comunicar.')         
            camp.negreta = negreta
            filera.append(camp)            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'Sr(a): {0} - {1}'.format(                                                
                                               expulsio.professor , 
                                               expulsio.motiu if expulsio.motiu else u'Pendent redactar motiu.')        
            camp.negreta = negreta
            filera.append(camp)

            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(notificacio)
            camp.negreta = negreta
            filera.append(camp)

            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(revisio)
            camp.negreta = negreta
            filera.append(camp)

            #--
            taula.fileres.append( filera )
            if not semiImpersonat:
                if not notificacio: expulsio.set_notificacio(notifAlumne)
                if not revisio: expulsio.set_revisio(revisAlumne)
                    
        report.append(taula)        

    #----Sancions -----------------------------------------------------------------------------   
    if detall in ['all', 'incidencies']:
        sancions = alumne.sancio_set.filter( impres = True )
        sancionsNoves, creaNotif = getNousElements(sancions, user)
        if creaNotif and not notifAlumne: notifAlumne=creaNotifUsuari(user, alumne, 'N')
        if sancionsNoves and not revisAlumne: revisAlumne=creaNotifUsuari(user, alumne, 'R')
            
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
            notificacio, revisio = sancio.get_notif_revisio(user)
            negreta = False if revisio else True
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} a {1}'.format( sancio.data_inici.strftime( '%d/%m/%Y' ) ,  sancio.data_fi.strftime( '%d/%m/%Y' ))       
            camp.negreta = negreta
            filera.append(camp)
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0} {1} {2}'.format( sancio.tipus , ' - ' if sancio.motiu else '', sancio.motiu )        
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(notificacio)
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(revisio)
            camp.negreta = negreta
            filera.append(camp)
            #--
            taula.fileres.append( filera )
            if not semiImpersonat:
                if not notificacio: sancio.set_notificacio(notifAlumne)
                if not revisio: sancio.set_revisio(revisAlumne)
                    
        report.append(taula)

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
    
            #----nom------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Nom'
        filera.append(camp)
        
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0}'.format( str(alumne) if responsable else alumne.get_nom_sentit() )        
        filera.append(camp)
        
        taula.fileres.append( filera )
        
            #----grup------------------------------------------
        filera = []
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'Grup'        
        filera.append(camp)
    
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'{0} Tutor(a): {1}'.format( alumne.grup, u", ".join([str(t) for t in alumne.tutorsDelGrupDeLAlumne()] ))        
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
        
        if professor:
            resps = alumne.get_dades_responsables()
        elif responsable:
            resps = alumne.get_dades_responsables(responsable=responsable)
        elif alumne:
            resps = alumne.get_dades_responsables(nomesNoms=True)
        
        camp.multipleContingut = [(resps['respPre'], None,),]
        if bool(resps['respAlt']): camp.multipleContingut.append((resps['respAlt'], None,))
        
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
        camp.contingut = u'{0} - ({1} {2})'.format(alumne.adreca, alumne.cp, localitat_i_o_municipi)
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

    infSortida=detall in ['all', 'sortides'] and settings.CUSTOM_MODUL_SORTIDES_ACTIU and not settings.CUSTOM_SORTIDES_OCULTES_A_FAMILIES
    pagquotes = QuotaPagament.objects.filter(alumne=alumne, quota__importQuota__gt=0)
    pagquotesNoves, creaNotif = getNousElements(pagquotes.filter(pagament_realitzat=False), user)
    if creaNotif and not notifAlumne: notifAlumne=creaNotifUsuari(user, alumne, 'N')
    if pagquotesNoves and not revisAlumne: revisAlumne=creaNotifUsuari(user, alumne, 'R')

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
        
        sortidesNoves, creaNotif = getNousElements(sortides, user)
        if creaNotif and not notifAlumne: notifAlumne=creaNotifUsuari(user, alumne, 'N')
        if sortidesNoves and not revisAlumne: revisAlumne=creaNotifUsuari(user, alumne, 'R')
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
                notificacio, revisio = notifica.first().get_notif_revisio(user)
                negreta = False if revisio else True
            else:
                notificacio, revisio = '', ''
                negreta = True                
            
            filera = []
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
            camp.contingut = u'{0}'.format(notificacio)
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(revisio)
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
                #alumnat_tret_de_lactivitat = act.alumnes_que_no_vindran.all().union(
                #    act.alumnes_justificacio.all())
                alumne_tret_de_lactivitat = alumne in act.alumnes_que_no_vindran.all() or alumne in act.alumnes_justificacio.all() 
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
            if not semiImpersonat:
                if not notificacio and notifica: notifica.first().set_notificacio(notifAlumne)
                if not revisio and notifica: notifica.first().set_revisio(revisAlumne)
                
        if not infQuota: report.append(taula)

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
            notificacio, revisio = pagquota.get_notif_revisio(user)
            negreta = not bool( pagquota.pagamentFet )
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = naturalday(pagquota.getdataLimit)
            camp.negreta = negreta
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = ''       
            camp.negreta = negreta
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( pagquota.quota.descripcio )        
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( notificacio )
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format( revisio )
            camp.negreta = negreta
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
            if not semiImpersonat:
                if not notificacio and not revisio: pagquota.set_notificacio(notifAlumne)
                if not revisio: pagquota.set_revisio(revisAlumne)
    
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
        respostesNoves, creaNotif = getNousElements(respostes, user)
        if creaNotif and not notifAlumne: notifAlumne=creaNotifUsuari(user, alumne, 'N')
        if respostesNoves and not revisAlumne: revisAlumne=creaNotifUsuari(user, alumne, 'R')
            
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
            notificacio, revisio = respostes[0].get_notif_revisio(user)
            negreta = False if revisio else True
            
            filera = []
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = respostes[0].qualitativa.nom_avaluacio       
            camp.negreta = negreta
            filera.append(camp)

            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = respostes[0].assignatura.nom_assignatura or respostes[0].assignatura
            camp.negreta = negreta
            filera.append(camp)
            
            #----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.multipleContingut = []
            for resposta in respostes:
                camp.multipleContingut.append( ( u'{0}'.format( resposta.get_resposta_display() ), None, ) )        
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(notificacio)
            camp.negreta = negreta
            filera.append(camp)
            # ----------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = u'{0}'.format(revisio)
            camp.negreta = negreta
            filera.append(camp)

            #--
            taula.fileres.append( filera )
            if not semiImpersonat:
                for resposta in respostes:
                    notificacio, revisio = resposta.get_notif_revisio(user)
                    if not notificacio: resposta.set_notificacio(notifAlumne)
                    if not revisio: resposta.set_revisio(revisAlumne)
                
        report.append(taula)

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

@login_required
def canviaAlumne( request, idalumne ):
    '''
    idalumne és l'id del model Alumne que es vol gestionar
    Si és tracta d'un usuari responsable i l'id d'alumne correspon
    a un dels seus alumnes associats, passa a gestionar aquest alumne.
    '''
    credentials = tools.getImpersonateUser(request) 
    (user, l4 ) = credentials
    
    responsable = User2Responsable( user )
    alum = None
    if responsable:
        a=Alumne.objects.filter( pk = int(idalumne) )
        if a.exists() and a.first() in responsable.get_alumnes_associats():
            alum=a.first()
    else:
        alum = User2Alumne( user )
    if alum:
        request.session["alumne_actual"]=alum.id
    return HttpResponseRedirect('/')

@login_required
def escollirAlumne(request):
    _, responsable, alumne = getRol( request.user, request )
    if responsable:
        if responsable.get_alumnes_associats().count()>1:
            if request.method == 'POST':
                form = escollirAlumneForm(request.user, responsable, request.POST)
                if form.is_valid():
                    alumneid=form.cleaned_data['alumne']
                    return HttpResponseRedirect(reverse_lazy('relacio_families__canviaAlumne',
                                                kwargs={"idalumne": alumneid},))
            else:
                form = escollirAlumneForm(request.user, responsable)
            return render(request, 'form.html', {'form': form, 'head': u'Selecciona l\'alumne' ,})
        else:
            if responsable.get_alumnes_associats().count()==1:
                return HttpResponseRedirect(reverse_lazy('relacio_families__canviaAlumne',
                                                    kwargs={"idalumne": responsable.get_alumnes_associats().first().id},))
            else:
                # No té alumnes
                return HttpResponseRedirect('/logout/')
    if alumne:
        alumneid=alumne.id
        return HttpResponseRedirect(reverse_lazy('relacio_families__canviaAlumne',
                                                kwargs={"idalumne": alumneid},))
    return HttpResponseRedirect('/')
