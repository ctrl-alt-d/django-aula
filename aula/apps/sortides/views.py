# This Python file uses the following encoding: utf-8
import base64
import hashlib
import hmac
import json
import random
import urllib

from Crypto.Cipher import DES3
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt

from aula.apps.missatgeria.missatges_a_usuaris import ACOMPANYANT_A_ACTIVITAT, tipusMissatge, RESPONSABLE_A_ACTIVITAT, \
    ERROR_SIGNATURES_REPORT_PAGAMENT_ONLINE, ERROR_FALTEN_DADES_REPORT_PAGAMENT_ONLINE, \
    ERROR_IP_NO_PERMESA_REPORT_PAGAMENT_ONLINE
from aula.settings import URL_DJANGO_AULA
from aula.utils.widgets import DateTextImput, bootStrapButtonSelect,\
    DateTimeTextImput
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

#helpers
from aula.utils import tools
from aula.utils.tools import unicode
from aula.apps.usuaris.models import User2Professor, AlumneUser, Professor
from aula.apps.presencia.models import Impartir
from aula.apps.horaris.models import FranjaHoraria
from django.shortcuts import render, get_object_or_404
from django.template.context import RequestContext, Context
from aula.apps.sortides.rpt_sortidesList import sortidesListRpt
from aula.apps.sortides.models import Sortida, SortidaPagament, Pagament, QuotaPagament, Quota
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django import forms
from aula.apps.sortides.table2_models import Table2_Sortides
from django_tables2.config import RequestConfig
from aula.utils.my_paginator import DiggPaginator
from django.shortcuts import render

from icalendar import Calendar, Event
from icalendar import vCalAddress, vText
from django.http.response import HttpResponse, Http404, HttpResponseServerError
from django.utils.datetime_safe import datetime
from django.conf import settings
from django.urls import reverse
from aula.apps.alumnes.models import Alumne, AlumneGrupNom, Curs
from django.contrib import messages
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.templatetags.tz import localtime
from django.utils.safestring import SafeText
from aula.apps.missatgeria.models import Missatge
from django.contrib.auth.models import User, Group
from django.db.models import Q
from django.template import loader
from django.template.defaultfilters import slugify
from aula.utils.tools import classebuida
import codecs
from django.db.utils import IntegrityError

from aula.apps.sortides.utils_sortides import TPVsettings

import django.utils.timezone
from dateutil.relativedelta import relativedelta
from django.urls import reverse_lazy
from django_select2.forms import ModelSelect2MultipleWidget



@login_required
@group_required(['professors'])  
def imprimir( request, pk, din = '4'):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    instance = get_object_or_404( Sortida, pk = pk )
    instance.flag_clean_nomes_toco_alumnes = True
    
    fEsDireccioOrGrupSortides = request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists()
    potEntrar = ( professor in instance.professors_responsables.all() or 
                  professor in instance.altres_professors_acompanyants.all() or 
                  fEsDireccioOrGrupSortides
                   )

    if not potEntrar:
        raise Http404 

    #Preparo el codi de barres
    import time
    import barcode
    from PIL import Image
    from barcode.writer import ImageWriter
    CodiBarres = barcode.get_barcode_class(u'code128')
    codi_barres = CodiBarres(instance.codi_de_barres or "x", writer=ImageWriter())
    barres = codi_barres.save("/tmp/barcode-{0}-{1}".format( time.time(), request.session.session_key ))
    im = Image.open(barres)
    im=im.crop( (20,20,385,50,) )
    s = im.size
    #im = im.resize((int(s[0] * 0.8), int(s[1] * 0.8)))
    im.save(barres)

        
    alumnes_que_hi_van = set( instance.alumnes_convocats.all() ) 
    alumnes_que_no_hi_van = set( instance.alumnes_que_no_vindran.all() )
    alumnes = list( alumnes_que_hi_van - alumnes_que_no_hi_van )
    
    report = []
    
    for alumne in Alumne.objects.filter( pk__in = [ a.id for a in alumnes ] ):
        o = classebuida()
        o.alumne = unicode( alumne )
        o.grup = unicode( alumne.grup )
        o.ciutat = instance.ciutat
        o.preu = instance.preu_per_alumne
        o.departament = unicode( instance.departament_que_organitza ) if instance.departament_que_organitza else instance.comentari_organitza
        o.titol = instance.titol_de_la_sortida 
        o.desde = instance.calendari_desde.strftime( "%H:%Mh del %d/%m/%Y" )
        o.desde_dia = instance.calendari_desde.strftime( "%d/%m/%Y" )
        o.finsa = instance.calendari_finsa.strftime( "%H:%Mh del %d/%m/%Y" )
        o.mitja = instance.get_mitja_de_transport_display()
        o.programa_de_la_sortida = instance.programa_de_la_sortida.split("\n") or ['',]
        o.condicions_generals = instance.condicions_generals.split("\n") or ['-',]
        o.terminipagament = u"" if not bool( instance.termini_pagament ) else u"- darrer dia pagament {0} -".format( instance.termini_pagament.strftime( '%d/%m/%Y' ) )
        report.append(o)
        o.barres = barres
        o.informacio_pagament = instance.informacio_pagament.split("\n") or ['-',]
        o.te_codi_barres = bool(instance.codi_de_barres)

    #from django.template import Context                              
    from appy.pod.renderer import Renderer
    import html
    import os
    from django import http
    
    excepcio = None

    #try:
        
    #resultat = StringIO.StringIO( )
    resultat = "/tmp/DjangoAula-temp-{0}-{1}.odt".format( time.time(), request.session.session_key )
    #context = Context( {'reports' : reports, } )
    path = os.path.join( settings.PROJECT_DIR,  '../customising/docs/autoritzacio2.odt') if din=='4' else os.path.join( settings.PROJECT_DIR,  '../customising/docs/autoritzacio2-A5.odt')
    if not os.path.isfile(path):
        path = os.path.join(os.path.dirname(__file__), 'templates/autoritzacio2.odt') if din=='4' else os.path.join(os.path.dirname(__file__), 'templates/autoritzacio2-A5.odt')

    renderer = Renderer(path, {'report' :report, }, resultat)  
    renderer.run()
    docFile = open(resultat, 'rb')
    contingut = docFile.read()
    docFile.close()
    os.remove(resultat)
    
    #barcode
    os.remove(barres)
        
#     except Exception as e:
#         excepcio = unicode( e )
        
    if True: #not excepcio:
        response = http.HttpResponse( contingut, content_type='application/vnd.oasis.opendocument.text')
        response['Content-Disposition'] = u'attachment; filename="{0}-{1}.odt"'.format( "autoritzacio_sortida", pk )
                                                     
    else:
        response = http.HttpResponse('''Als Gremlin no els ha agradat aquest fitxer! %s''' % html.escape(excepcio))
    
    return response
    

@login_required
@group_required(['professors'])
def sortidesMevesList( request ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    q_professor_proposa = Q( professor_que_proposa = professor  )
    q_professors_responsables = Q( professors_responsables = professor  )
    q_professors_acompanyants = Q(altres_professors_acompanyants = professor  )
    
    
    sortides = ( Sortida
                   .objects
                   .filter( q_professor_proposa | q_professors_responsables | q_professors_acompanyants )
                   .distinct()
                  )

    table = Table2_Sortides( list( sortides ), origen="Meves" ) 
    table.order_by = '-calendari_desde' 
    
    RequestConfig(request, paginate={"paginator_class":DiggPaginator , "per_page": 10}).configure(table)
        
    return render(
                  request, 
                  'lesMevesSortides.html', 
                  {'table': table,
                   }
                 )       


@login_required
@group_required(['professors'])
def sortidesAllList( request ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    sortides = list( Sortida
                     .objects
                     .all()
                     .distinct()                     
                )
 
    table = Table2_Sortides( data=sortides, origen="All" ) 
    table.order_by = '-calendari_desde' 
    
    RequestConfig(request, paginate={"paginator_class":DiggPaginator , "per_page": 10}).configure(table)
        
    url = r"{0}{1}".format( settings.URL_DJANGO_AULA, reverse( 'sortides__sortides__ical' ) )    
        
    return render(
                  request, 
                  'table2.html', 
                  {'table': table,
                   'url': url,
                   }
                 )       



@login_required
@group_required(['professors'])
def sortidesGestioList( request ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    filtre = []
    socEquipDirectiu = User.objects.filter( pk=user.pk, groups__name = 'direcció').exists()
    socCoordinador = User.objects.filter( pk=user.pk, groups__name__in = [ 'sortides'] ).exists()
    socSecretari = User.objects.filter(pk=user.pk, groups__name__in=['secretaria']).exists()

    #si sóc equip directiu només les que tinguin estat 'R' (Revisada pel coordinador)
    if socEquipDirectiu:
        filtre.append('R')
    #si sóc coordinador de sortides o secretari només les que tinguin estat 'P' (Proposada)
    if socCoordinador or socSecretari:
        filtre.append('P')

    sortides = ( Sortida
                   .objects
                   .exclude( estat = 'E' )
                   .filter( estat__in = filtre )
                   .distinct()
                  )

    # si sóc secretari i es pot pagar online, només les que tinguin tipus de pagament 'ON' (ONline)
    if socSecretari and settings.CUSTOM_SORTIDES_PAGAMENT_ONLINE:
        sortides = sortides.filter(tipus_de_pagament = 'ON')

    table = Table2_Sortides( data=list( sortides ), origen="Gestio" ) 
    table.order_by = '-calendari_desde' 
    
    RequestConfig(request, paginate={"paginator_class":DiggPaginator , "per_page": 10}).configure(table)
        
    url = r"{0}{1}".format( settings.URL_DJANGO_AULA, reverse( 'sortides__sortides__ical' ) )    
        
    return render(
                  request, 
                  'gestioDeSortides.html', 
                  {'table': table,
                   'url': url,
                   }
                 )


@login_required
@group_required(['consergeria'])
def sortidesConsergeriaList(request):
    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials
    avui = datetime.now().date()
    sortides = list(Sortida
                    .objects
                    .filter(calendari_finsa__gte=avui, estat__in=['R','G'])
                    .distinct()
                    )

    table = Table2_Sortides(data=sortides, origen="Consergeria")
    table.order_by = 'calendari_desde'

    RequestConfig(request, paginate={"paginator_class": DiggPaginator, "per_page": 10}).configure(table)

    url = r"{0}{1}".format(settings.URL_DJANGO_AULA, reverse('sortides__sortides__ical'))

    return render(
        request,
        'table2.html',
        {'table': table,
         'url': url,
         }
    )

@login_required
@group_required(['professors'])  # TODO: i grup sortides
def sortidaEdit(request, pk=None, clonar=False, origen=False):
    from aula.apps.sortides.forms import SortidaForm

    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    es_post = (request.method == "POST")

    professor = User2Professor(user)

    professors_acompanyen_abans = set()
    professors_acompanyen_despres = set()

    professors_organitzen_abans = set()
    professors_organitzen_despres = set()

    fEsDireccioOrGrupSortides = request.user.groups.filter(name__in=[u"direcció", u"sortides"]).exists()
    if bool(pk) and not clonar:
        instance = get_object_or_404(Sortida, pk=pk)
        potEntrar = (professor in instance.professors_responsables.all() or
                     professor in instance.altres_professors_acompanyants.all() or
                     fEsDireccioOrGrupSortides)
        if not potEntrar:
            raise Http404
        professors_acompanyen_abans = set(instance.altres_professors_acompanyants.all())
        professors_organitzen_abans = set(instance.professors_responsables.all())
    elif bool(pk) and clonar:
        instance = get_object_or_404(Sortida, pk=pk)
        instance.pk = None
        instance.estat = 'E'
        instance.titol_de_la_sortida = u"**CLONADA** " + instance.titol_de_la_sortida
        instance.esta_aprovada_pel_consell_escolar = 'P'
        instance.professor_que_proposa = professor
    # instance.professors_responsables = None
    #         instance.altres_professors_acompanyants = None
    #         instance.tutors_alumnes_convocats = None
    #         instance.alumnes_convocats = None
    #         instance.alumnes_que_no_vindran = None
    #         instance.alumnes_justificacio = None
    #         instance.professor_que_proposa_id = None

    else:
        instance = Sortida()
        instance.professor_que_proposa = professor
        instance.tipus_de_pagament = "ON" if settings.CUSTOM_SORTIDES_PAGAMENT_ONLINE else "NO"

    instance.credentials = credentials

    # És un formulari reduit?
    if settings.CUSTOM_FORMULARI_SORTIDES_REDUIT:
        exclude = ('alumnes_convocats', 'alumnes_que_no_vindran', 'alumnes_justificacio', 'data_inici', 'franja_inici', 'data_fi',
                   'franja_fi', 'codi_de_barres', 'empresa_de_transport', 'pagament_a_empresa_de_transport',
                   'pagament_a_altres_empreses', 'feina_per_als_alumnes_aula', 'pagaments', 'tpv')
    else:
        exclude = ('alumnes_convocats', 'alumnes_que_no_vindran', 'alumnes_justificacio', 'pagaments', 'tpv')

    formIncidenciaF = modelform_factory(Sortida, form=SortidaForm, exclude=exclude,
                                        widgets = {
                                            'professors_responsables': ModelSelect2MultipleWidget(
                                                queryset=Professor.objects.all(),
                                                search_fields=('last_name__icontains', 'first_name__icontains',),
                                                attrs={'style': "'width': '100%'"}
                                                ),
                                            'altres_professors_acompanyants': ModelSelect2MultipleWidget(
                                                queryset=Professor.objects.all(),
                                                search_fields=('last_name__icontains', 'first_name__icontains',),
                                                attrs={'style': "'width': '100%'"}
                                                )
                                            }
                                        )

    if request.method == "POST":
        post_mutable = request.POST.copy()
        if 'esta_aprovada_pel_consell_escolar' not in post_mutable:
            post_mutable['esta_aprovada_pel_consell_escolar'] = 'P'

        form = formIncidenciaF(post_mutable, instance=instance)

        if form.is_valid():
            if form.cleaned_data['tipus_de_pagament']=='NO': instance.preu_per_alumne=0
            # Omplir camps de classes afectades
            if settings.CUSTOM_FORMULARI_SORTIDES_REDUIT:

                #Buscar primera impartició afectada
                primeraimparticio = ( 
                    Impartir
                    .objects
                    .filter(dia_impartir=instance.calendari_desde.date(),
                            horari__hora__hora_inici__gte=instance.calendari_desde.time()).order_by(
                            'dia_impartir', 'horari__hora__hora_inici')
                    .first() )
                primerafranja = primeraimparticio.horari.hora if primeraimparticio else None

                if primeraimparticio is None:
                    primeraimparticio = (
                        Impartir
                        .objects.filter(
                            dia_impartir__gt=instance.calendari_desde.date()).order_by(
                            'dia_impartir', 'horari__hora__hora_inici')
                        .first() )
                    primerafranja = primeraimparticio.horari.hora if primeraimparticio else None

                if primeraimparticio is not None:
                    instance.data_inici = primeraimparticio.dia_impartir
                    instance.franja_inici = primerafranja


                # Buscar darrera impartició afectada
                darreraimparticio = (
                    Impartir
                    .objects
                    .filter(dia_impartir=instance.calendari_finsa.date(),
                            horari__hora__hora_fi__lte=instance.calendari_finsa.time()).order_by(
                            'dia_impartir', 'horari__hora__hora_fi')
                    .last()
                )
                darrerafranja = darreraimparticio.horari.hora if darreraimparticio else None

                if darreraimparticio is None:
                    darreraimparticio = (
                        Impartir
                        .objects
                        .filter(dia_impartir__lt=instance.calendari_finsa.date())
                        .order_by('dia_impartir', 'horari__hora__hora_fi')
                        .last()
                    )
                    darrerafranja = darreraimparticio.horari.hora if darreraimparticio else None

                if darreraimparticio is not None:
                    instance.data_fi = darreraimparticio.dia_impartir
                    instance.franja_fi = darrerafranja

                # Comprovem si la sortida en realitat no afecta cap hora d'impartició, això passa quan la data inicial > data final
                if ( instance.data_fi and instance.data_inici and instance.data_fi < instance.data_inici):
                    instance.data_inici = None
                    instance.data_fi = None
                    instance.franja_inici = None
                    instance.franja_fi = None

            form.save()

            if origen == "Meves":
                messages.warning(request,
                                 SafeText(u"""RECORDA: Una vegada enviades les dades, 
                                  has de seleccionar els <a href="{0}">alumnes convocats</a> i els 
                                  <a href="{1}">alumnes que no hi van</a> 
                                  des del menú desplegable ACCIONS""".format(
                                     "/sortides/alumnesConvocats/{id}".format(id=instance.id),
                                     "/sortides/alumnesFallen/{id}".format(id=instance.id),
                                 )
                                 ))

            professors_acompanyen_despres = set(instance.altres_professors_acompanyants.all())
            professors_organitzen_despres = set(instance.professors_responsables.all())

            acompanyen_nous = professors_acompanyen_despres - professors_acompanyen_abans
            organitzen_nous = professors_organitzen_despres - professors_organitzen_abans

            # helper missatges:
            data_inici = u"( data activitat encara no informada )"
            if instance.data_inici is not None:
                data_inici = """del dia {dia}""".format(dia=instance.data_inici.strftime('%d/%m/%Y'))

                # missatge a acompanyants:
            missatge = ACOMPANYANT_A_ACTIVITAT
            txt = missatge.format(sortida=instance.titol_de_la_sortida, dia=data_inici)
            enllac = reverse('sortides__sortides__edit_by_pk', kwargs={'pk': instance.id})
            tipus_de_missatge = tipusMissatge(missatge)
            msg = Missatge(remitent=user, text_missatge=txt, enllac=enllac, tipus_de_missatge=tipus_de_missatge)
            for nou in acompanyen_nous:
                importancia = 'VI'
                msg.envia_a_usuari(nou, importancia)

                # missatge a responsables:
            missatge = RESPONSABLE_A_ACTIVITAT
            txt = missatge.format(sortida=instance.titol_de_la_sortida, dia=data_inici)
            tipus_de_missatge = tipusMissatge(missatge)
            msg = Missatge(remitent=user, text_missatge=txt, tipus_de_missatge=tipus_de_missatge)
            for nou in organitzen_nous:
                importancia = 'VI'
                msg.envia_a_usuari(nou, importancia)

            nexturl = r"/sortides/sortides{origen}".format(origen=origen)
            return HttpResponseRedirect(nexturl)

    else:

        form = formIncidenciaF(instance=instance)

    # form.fields['estat'].widget = forms.RadioSelect( choices = form.fields['estat'].widget.choices )
    widgetBootStrapButtonSelect = bootStrapButtonSelect()
    widgetBootStrapButtonSelect.choices = form.fields['estat'].widget.choices
    form.fields['estat'].widget = widgetBootStrapButtonSelect

    form.fields["alumnes_a_l_aula_amb_professor_titular"].widget.attrs['style'] = u"width: 3%"
    form.fields["calendari_public"].widget.attrs['style'] = u"width: 3%"
    for f in form.fields:
        form.fields[f].widget.attrs['class'] = ' form-control ' + form.fields[f].widget.attrs.get('class', "")

    form.fields['calendari_desde'].widget = DateTimeTextImput()
    form.fields['calendari_finsa'].widget = DateTimeTextImput()
    form.fields['termini_pagament'].widget = DateTimeTextImput()

    if not fEsDireccioOrGrupSortides:
        form.fields["esta_aprovada_pel_consell_escolar"].widget.attrs['disabled'] = u"disabled"
        if not settings.CUSTOM_FORMULARI_SORTIDES_REDUIT:
            form.fields["codi_de_barres"].widget.attrs['disabled'] = u"disabled"
        form.fields["informacio_pagament"].widget.attrs['disabled'] = u"disabled"
        form.fields["preu_per_alumne"].widget.attrs['disabled'] = u"disabled"

    # si no és propietari tot a disabled
    deshabilitat = (instance.id and
                    not (professor in instance.professors_responsables.all() or
                         fEsDireccioOrGrupSortides)
                    )

    if deshabilitat:
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = u"disabled"
        form.fields['estat'].label += u": {0} ".format(instance.get_estat_display())

    return render(
        request,
        'formSortida.html',
        {'form': form,
         'head': 'Sortides',
         'missatge': 'Sortides',
         'deshabilitat': '1==1' if deshabilitat else '1==2',
         },
    )


#-------------------------------------------------------------------
    
@login_required
@group_required(['professors'])   
def alumnesConvocats( request, pk , origen ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    instance = get_object_or_404( Sortida, pk = pk )
    fEsDireccioOrGrupSortides = request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists()
    potEntrar = ( professor in instance.professors_responsables.all() or 
                  professor in instance.altres_professors_acompanyants.all() or 
                  fEsDireccioOrGrupSortides
                   )
    if not potEntrar:
        raise Http404
    
    instance.credentials = credentials
    instance.flag_clean_nomes_toco_alumnes = True
    formIncidenciaF = modelform_factory(Sortida, fields=( 'alumnes_convocats',  ) )

    if request.method == "POST":
        form = formIncidenciaF(request.POST, instance = instance)
        
        if form.is_valid():
            try: 

                nous=set([ x.pk for x in form.cleaned_data['alumnes_convocats'] ] )
                ante=set([ x.pk for x in instance.alumnes_convocats.all() ] )
                #afegir
                for alumne in nous - ante:
                    #aquest if no caldria però per algun motiu falla per clau duplicada.
                    try:
                        instance.alumnes_convocats.add( alumne )
                        if instance.tipus_de_pagament == 'ON':
                            # Comprova si ja existeix el pagament
                            pag=SortidaPagament.objects.filter(alumne=alumne, sortida=instance)
                            if not pag:
                                instance.pagaments.add(alumne)
                    except IntegrityError:
                        pass
                    
                #treure
                for alumne in ante - nous:
                    #aquest if no caldria. és només per seguretat.
                    try:
                        instance.alumnes_convocats.remove( alumne )
                        if instance.tipus_de_pagament == 'ON':
                            # Comprova si ja ha pagat
                            pag=SortidaPagament.objects.filter(alumne=alumne, sortida=instance, pagament_realitzat=True)
                            if not pag:
                                instance.pagaments.remove(alumne)
                            instance.notificasortida_set.filter( alumne = alumne ).delete()
                    except IntegrityError:
                        pass

                nexturl =  r'/sortides/sortides{origen}'.format(origen=origen)
                return HttpResponseRedirect( nexturl )
            except ValidationError as e:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  e.messages )
            
    else:

        form = formIncidenciaF( instance = instance  )
        
        
    from itertools import groupby
    q_base = ( AlumneGrupNom
              .objects
              .order_by( 'grup__curs__nivell__ordre_nivell', 
                         'grup__curs__nom_curs', 
                         'grup__descripcio_grup',
                         'cognoms',
                         'nom')
              .all()
             ) 
    
    choices = []
    for k, g in groupby(q_base, lambda x: x.grup.descripcio_grup):
        choices.append(( k , [ ( o.id, unicode(o) ) for o in g] ))
        
    form.fields['alumnes_convocats'].queryset = q_base
    form.fields['alumnes_convocats'].widget.choices = choices

    for f in form.fields:
        form.fields[f].widget.attrs['class'] = ' form-control ' + form.fields[f].widget.attrs.get('class',"") 

    #form.fields['alumnes_convocats'].widget.attrs['style'] = "height: 500px;"

    #si no és propietari tot a disabled
    deshabilitat = ( instance.id and 
                     not ( professor in instance.professors_responsables.all() or 
                         fEsDireccioOrGrupSortides )
                    )
    
    if deshabilitat:
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = u"disabled"    
        
    return render(
                request,
                'formSortidesAlumnes.html',
                    {'form': form,
                     'head': 'Sortides' ,
                     'missatge': 'Sortides',
                     'deshabilitat': '1==1' if deshabilitat else '1==2',
                    },
                )




#-------------------------------------------------------------------
    
@login_required
@group_required(['professors'])   
def alumnesFallen( request, pk , origen ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    instance = get_object_or_404( Sortida, pk = pk )
    instance.flag_clean_nomes_toco_alumnes = True
    fEsDireccioOrGrupSortides = request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists()
    potEntrar = ( professor in instance.professors_responsables.all() or 
                  professor in instance.altres_professors_acompanyants.all() or 
                  fEsDireccioOrGrupSortides
                   )
    
    if not potEntrar:
        raise Http404 
    
    instance.credentials = credentials
   
    formIncidenciaF = modelform_factory(Sortida, fields=( 'alumnes_que_no_vindran',  ) )

    if request.method == "POST":
        form = formIncidenciaF(request.POST, instance = instance)
        
        if form.is_valid(): 
            try:
                nous=set([ x.pk for x in form.cleaned_data['alumnes_que_no_vindran'] ] )
                ante=set([ x.pk for x in instance.alumnes_que_no_vindran.all().distinct() ] )
                #afegir
                for alumne in nous - ante:
                    instance.alumnes_que_no_vindran.add( alumne )
                #treure
                for alumne in ante - nous:
                    instance.alumnes_que_no_vindran.remove( alumne )
                
                nexturl =  r'/sortides/sortides{origen}'.format( origen = origen )
                return HttpResponseRedirect( nexturl )
            except ValidationError as e:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  e.messages )

                nexturl =  r'/sortides/sortides{origen}'.format( origen = origen )
                return HttpResponseRedirect( nexturl )
            except ValidationError as e:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  e.messages )


    else:

        form = formIncidenciaF( instance = instance  )
        
    ids_alumnes_que_venen = [ a.id for a in instance.alumnes_convocats.all()  ]
    form.fields['alumnes_que_no_vindran'].queryset = AlumneGrupNom.objects.filter( id__in = ids_alumnes_que_venen ) 

    for f in form.fields:
        form.fields[f].widget.attrs['class'] = ' form-control ' + form.fields[f].widget.attrs.get('class',"") 

    #form.fields['alumnes_que_no_vindran'].widget.attrs['style'] = "height: 500px;"
    #si no és propietari tot a disabled
    deshabilitat = ( instance.id and 
                     not ( professor in instance.professors_responsables.all() or 
                         fEsDireccioOrGrupSortides )
                    )
    
    if deshabilitat:
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = u"disabled" 

        
    return render(
                request,
                'formSortidesAlumnesFallen.html',
                    {'form': form,
                     'head': 'Sortides' ,
                     'missatge': 'Sortides',
                     'deshabilitat': '1==1' if deshabilitat else '1==2',
                    },
                )

#-------------------------------------------------------------------
    
@login_required
@group_required(['professors'])   
def alumnesJustificats( request, pk , origen ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    instance = get_object_or_404( Sortida, pk = pk )
    instance.flag_clean_nomes_toco_alumnes = True
    fEsDireccioOrGrupSortides = request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists()
    potEntrar = ( professor in instance.professors_responsables.all() or 
                  professor in instance.altres_professors_acompanyants.all() or 
                  fEsDireccioOrGrupSortides
                   )

    if not potEntrar:
        raise Http404 
        
    instance.credentials = credentials
   
    formIncidenciaF = modelform_factory(Sortida, fields=( 'alumnes_justificacio',  ) )

    if request.method == "POST":
        form = formIncidenciaF(request.POST, instance = instance)
        
        if form.is_valid(): 
               
            try:
                nous=set([ x.pk for x in form.cleaned_data['alumnes_justificacio'] ] )
                ante=set([ x.pk for x in instance.alumnes_justificacio.all() ] )
                #afegir
                for alumne in nous - ante:
                    instance.alumnes_justificacio.add( alumne )
                #treure
                for alumne in ante - nous:
                    instance.alumnes_justificacio.remove( alumne )
                
                nexturl =  r'/sortides/sortides{origen}'.format( origen = origen )
                return HttpResponseRedirect( nexturl )
            except ValidationError as e:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  e.messages )

    else:

        form = formIncidenciaF( instance = instance  )
        
    #ids_alumnes_no_vindran = [ a.id for a in instance.alumnes_que_no_vindran.all()  ]
    ids_alumnes_que_venen = [ a.id for a in instance.alumnes_convocats.all()  ]
    form.fields['alumnes_justificacio'].queryset = AlumneGrupNom.objects.filter( id__in = ids_alumnes_que_venen ) 

    for f in form.fields:
        form.fields[f].widget.attrs['class'] = ' form-control ' + form.fields[f].widget.attrs.get('class',"") 

    #form.fields['alumnes_que_no_vindran'].widget.attrs['style'] = "height: 500px;"

    #si no és propietari tot a disabled
    deshabilitat = ( instance.id and 
                     not ( professor in instance.professors_responsables.all() or 
                         fEsDireccioOrGrupSortides )
                    )
    
    if deshabilitat:
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = u"disabled" 
                    
    return render(
                request,
                'formSortidesAlumnesFallen.html',
                    {'form': form,
                     'head': 'Sortides' ,
                     'missatge': 'Sortides',
                     'deshabilitat': '1==1' if deshabilitat else '1==2',
                    },
                )


#-------------------------------------------------------------------
    
@login_required
@group_required(['professors'])   
def professorsAcompanyants( request, pk , origen ):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    instance = get_object_or_404( Sortida, pk = pk )
    instance.flag_clean_nomes_toco_alumnes = True
    
    professors_acompanyen_despres = set( ) 
    professors_organitzen_despres = set( )     
    
    professors_acompanyen_abans = set( instance.altres_professors_acompanyants.all() )
    professors_organitzen_abans = set( instance.professors_responsables.all() )
    estat_abans = instance.estat
    
    fEsDireccioOrGrupSortides = request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists()
    potEntrar = ( professor in instance.professors_responsables.all() or 
                  professor in instance.altres_professors_acompanyants.all() or 
                  fEsDireccioOrGrupSortides
                   )

    if not potEntrar:
        raise Http404 
    
    
    instance.credentials = credentials    
   
    formIncidenciaF = modelform_factory(Sortida, fields=( 'altres_professors_acompanyants',  ) ,
                                        widgets = {
                                            'altres_professors_acompanyants': ModelSelect2MultipleWidget(
                                                queryset=Professor.objects.all(),
                                                search_fields=('last_name__icontains', 'first_name__icontains',),
                                                attrs={'style': "'width': '100%'"}
                                                )
                                            }
                                      )
    if request.method == "POST":
        form = formIncidenciaF(request.POST, instance = instance)
        
        if form.is_valid(): 
            try:
                form.save()

                if instance.estat in ['R','G']:
                    professors_acompanyen_despres = set( instance.altres_professors_acompanyants.all() )
                    professors_organitzen_despres = set( instance.professors_responsables.all() )
                    
                    acompanyen_nous = professors_acompanyen_despres - professors_acompanyen_abans
                    organitzen_nous = professors_organitzen_despres - professors_organitzen_abans
                    
                    #missatge a acompanyants:
                    missatge = ACOMPANYANT_A_ACTIVITAT
                    txt = missatge.format( sortida = instance.titol_de_la_sortida, dia = instance.data_inici.strftime( '%d/%m/%Y' ) )
                    tipus_de_missatge = tipusMissatge(missatge)
                    msg = Missatge( remitent = user, text_missatge = txt, tipus_de_missatge = tipus_de_missatge )
                    for nou in acompanyen_nous:                
                        importancia = 'VI'
                        msg.envia_a_usuari(nou, importancia)                
        
                    #missatge a responsables:
                    missatge = RESPONSABLE_A_ACTIVITAT
                    txt = RESPONSABLE_A_ACTIVITAT.format( sortida = instance.titol_de_la_sortida, dia = instance.data_inici.strftime( '%d/%m/%Y' ) )
                    tipus_de_missatge = tipusMissatge(missatge)
                    msg = Missatge( remitent = user, text_missatge = txt, tipus_de_missatge = tipus_de_missatge )
                    for nou in organitzen_nous:                
                        importancia = 'VI'
                        msg.envia_a_usuari(nou, importancia) 
                                    
                nexturl =  r'/sortides/sortides{origen}'.format( origen=origen )                
                return HttpResponseRedirect( nexturl )
            except ValidationError as e:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  e.messages )

    else:

        form = formIncidenciaF( instance = instance  )
        
    for f in form.fields:
        form.fields[f].widget.attrs['class'] = ' form-control ' + form.fields[f].widget.attrs.get('class',"") 

    #form.fields['altres_professors_acompanyants'].widget.attrs['style'] = "height: 500px;"
    #si no és propietari tot a disabled
    deshabilitat = ( instance.id and 
                     not ( professor in instance.professors_responsables.all() or 
                         fEsDireccioOrGrupSortides )
                    )
    
    if deshabilitat:
        for field in form.fields:
            form.fields[field].widget.attrs['disabled'] = u"disabled" 
    
    return render(
                request,
                'formSortidaProfessorAcompanyant.html',
                    {'form': form,
                     'head': 'Sortides' ,
                     'missatge': 'Sortides',
                     'deshabilitat': '1==1' if deshabilitat else '1==2',
                    },
                )


#-------------------------------------------------------------------
    
@login_required
@group_required(['professors'])   #TODO: i grup sortides
def esborrar( request, pk , origen):

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user )     
    
    instance = get_object_or_404( Sortida, pk = pk )
    
    mortalPotEntrar = (  instance.professor_que_proposa == professor  and  not instance.estat in [ 'R', 'G' ] )
    direccio = ( request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists() )
    
    potEntrar = mortalPotEntrar or direccio
    if not potEntrar:
        messages.warning(request, u"No pots esborrar aquesta activitat." )
        return HttpResponseRedirect( request.META.get('HTTP_REFERER') )
    
    instance.credentials = credentials
   
    try:
        instance.delete()
    except:
        messages.warning(request, u"Error esborrant la activitat." )
    
    nexturl =  r'/sortides/sortides{origen}'.format( origen=origen )
    return HttpResponseRedirect( nexturl )

#-------------------------------------------------------------------
    
def sortidaiCal( request):

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    cal = Calendar()
    cal.add('method','PUBLISH' ) # IE/Outlook needs this

    for instance in Sortida.objects.filter( calendari_desde__isnull = False ).exclude(estat__in = ['E', 'P', ]).all():
        event = Event()
        
#         d=instance.data_inici
#         t=instance.franja_inici.hora_inici
#         dtstart = datetime( d.year, d.month, d.day, t.hour, t.minute  )
#         d=instance.data_fi
#         t=instance.franja_fi.hora_fi
#         dtend = datetime( d.year, d.month, d.day, t.hour, t.minute  )
        
        
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
        event.add('uid', 'djau-ical-{0}'.format( instance.id ) )
        event['location'] = vText( instance.ciutat )

        
        cal.add_component(event)

#     response = HttpResponse( cal.to_ical() , content_type='text/calendar')
#     response['Filename'] = 'shifts.ics'  # IE needs this
#     response['Content-Disposition'] = 'attachment; filename=shifts.ics'
#     return response

    return HttpResponse( cal.to_ical() )
    
    
    

@login_required
@group_required(['professors'])  
def sortidaExcel( request, pk ):
    """
    Generates an Excel spreadsheet for review by a staff member.
    """
    sortida = get_object_or_404( Sortida, pk = pk )

    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    professor = User2Professor( user )     
    fEsDireccioOrGrupSortides = request.user.groups.filter(name__in=[u"direcció", u"sortides"] ).exists()
    potEntrar = ( professor in sortida.professors_responsables.all() or 
                  professor in sortida.altres_professors_acompanyants.all() or 
                  fEsDireccioOrGrupSortides
                   )

    if not potEntrar:
        raise Http404 

    
    no_assisteixen = list( sortida.alumnes_que_no_vindran.all() )
    
    #capcelera
    capcelera = []
    
    #Dades de la sortida
    detall = [
                [ sortida.get_tipus_display() , sortida.get_estat_display(),  ],
                [],
                [ sortida.titol_de_la_sortida  ,   ],
                [],
                [ u"Comença ", u"Finalitza", ],
                [ sortida.calendari_desde.strftime( '%d/%m/%Y %H:%M' ) , sortida.calendari_finsa.strftime( '%d/%m/%Y %H:%M' )  ],              
                [],
    ]
    detall += [[ u"Organitzen", ]] + [[unicode( p )] for p in sortida.professors_responsables.all()] + [[]]
    detall += [[ u"Acompanyen", ]] + [[unicode( p )] for p in sortida.altres_professors_acompanyants.all()] + [[]]
    
    #Alumnes
    alumnes = [ [ u'Alumne', u'Grup', u'Nivell', u"Assistència"], ]
    if sortida.tipus_de_pagament == 'ON':
        alumnes[0].extend([u"Pagat", u"Data Pagament", u"Codi Pagament"])

    for alumne in sortida.alumnes_convocats.all():
        row = [alumne,
               alumne.grup.descripcio_grup,
               alumne.grup.curs.nivell,
               u"No assisteix a la sortida" if alumne in no_assisteixen else u""
               ]
        if sortida.tipus_de_pagament=='ON':
            pagament = SortidaPagament.objects.get(alumne=alumne, sortida=sortida)
            pagament_realitzat = pagament.pagament_realitzat
            ordre = pagament.ordre_pagament if pagament.ordre_pagament and pagament.pagament_realitzat else ''
            observacions = pagament.observacions if pagament.observacions and pagament.pagament_realitzat else ''
            row.extend([u"Si" if pagament_realitzat else u"No",
                        pagament.data_hora_pagament.strftime('%d/%m/%Y %H:%M') if pagament_realitzat else u"",
                        "{0} - {1}".format(ordre, observacions) if observacions else ordre])
        alumnes += [ row ]

    dades_sortida = detall + alumnes

    template = loader.get_template("export.csv")
    context = Context({
                         'capcelera':capcelera,
                         'dades':dades_sortida,
    })

    import os
    import html
    import time
    from django import http
    import xlsxwriter

    resultat = "/tmp/DjangoAula-temp-{0}-{1}.xlsx".format(time.time(), request.session.session_key)
    workbook = xlsxwriter.Workbook(resultat)
    worksheet = workbook.add_worksheet()
    worksheet.set_column(0, 0, 40)

    nun_row = 0
    for row in capcelera:
        num_col = 0
        for item in row:
            worksheet.write(nun_row, num_col, unicode( item) )
            num_col += 1
        nun_row += 1

    nun_row = 0
    for row in dades_sortida:
        num_col = 0
        for item in row:
            worksheet.write(nun_row, num_col, unicode( item) )
            num_col += 1
        nun_row += 1

    workbook.close()

    excepcio = None

    docFile = open(resultat, 'rb')
    contingut = docFile.read()
    docFile.close()
    os.remove(resultat)

    if True:  # not excepcio:
        response = http.HttpResponse(contingut, content_type='application/vnd.oasis.opendocument.text')
        response['Content-Disposition'] = u'attachment; filename="sortida-{0}.xlsx"'.format( slugify( sortida.titol_de_la_sortida ))

    else:
        response = http.HttpResponse('''Als Gremlin no els ha agradat aquest fitxer! %s''' % html.escape(excepcio))

    return response


    # response = HttpResponse()
    # filename = "sortida-{0}.csv".format( slugify( sortida.titol_de_la_sortida ))
    #
    #
    # response['Content-Disposition'] = 'attachment; filename='+filename
    # response['Content-Type'] = 'text/csv; charset=utf-8'
    # #response['Content-Type'] = 'application/vnd.ms-excel; charset=utf-8'
    # # Add UTF-8 'BOM' signature, otherwise Excel will assume the CSV file
    # # encoding is ANSI and special characters will be mangled
    # #response.write("\xEF\xBB\xBF")
    # response.write(codecs.BOM_UTF8)
    # response.write(  template.render(context)   )
    #
    # return response


    
    
    
#-----------------
def clonePagament(pagament):
    '''
    Crea un nou Pagament , tot igual al pagament indicat 
    menys l'estat, ordre_pagament i pagament_realitzat.
    El pagament actual queda marcat com ERROR
    retorna el Pagament creat.
    '''
    
    pagament.estat='E'  # ERROR
    pagament.save()
    noupagament = Pagament()
    noupagament.data_hora_pagament = pagament.data_hora_pagament
    noupagament.alumne = pagament.alumne
    noupagament.sortida = pagament.sortida
    noupagament.quota = pagament.quota
    noupagament.fracciona = pagament.fracciona
    noupagament.importParcial = pagament.importParcial
    noupagament.dataLimit = pagament.dataLimit
    noupagament.save()
    return noupagament

def generaOrdre(pagament):
    '''
    L'ordre de pagament queda formada per l'identificador d'alumne (5 dígits)
    concatenat amb l'identificador de pagament (7 dígits)
    '''
    
    return (str(pagament.alumne.pk) + ('0000000'+str(pagament.pk))[-7:])[-12:]

def esRecent(datahora, minuts=7):
    '''
    Retorna True si la datahora és anterior en menys de minuts de l'hora actual.
    '''
    
    from dateutil.relativedelta import relativedelta
    
    ara=datetime.now()
    return datahora + relativedelta(minutes=minuts) > ara

def logPagaments(txt, tipus="ADMINISTRACIO"):
    '''
    Comunica incident relacionat amb pagament, només per als administradors
    '''
    msg = Missatge(remitent=User.objects.filter(groups__name__contains='administradors').first(), text_missatge=txt, tipus_de_missatge=tipus)
    importancia = 'VI'
    administradors = get_object_or_404(Group, name='administradors')
    msg.envia_a_grup(administradors, importancia=importancia)
        
@login_required
def pagoOnline(request, pk):
    from aula.apps.sortides.forms import PagamentForm

    '''
    Mostra la informació del pagament i el botó per pagar o 
    el missatge Pagament Realitzat!!!
    '''
    
    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    pagament = get_object_or_404(Pagament, pk=pk)
    nexturl=request.GET.get('next')
    if not nexturl:
        nexturl='/'
    if pagament.estat=='E':
        '''
        Pagament erroni, es pot donar el cas si l'usuari ha obert diverses finestres de pagament
        No s'ha de fer res.
        '''
        return HttpResponseRedirect(reverse('relacio_families__informe__el_meu_informe'))

    alumne = pagament.alumne
    fEsDireccioOrGrupSortides = request.user.groups.filter(name__in=[u"direcció", u"sortides"]).exists()

    potEntrar = (alumne.user_associat.getUser() == user or fEsDireccioOrGrupSortides)
    if not potEntrar:
        return render(
                    request,
                    'resultat.html', 
                    {'msgs': {'errors': [], 'warnings': [], 'infos': ['AQUEST USUARI NO TÉ AUTORITZACIÓ PER ACCEDIR AL PAGAMENT.']} },
                 )
    
    if not pagament.pagament_realitzat:
        # Pagament pendent
        if pagament.estat=='T':
            '''
            Pagament que no ha finalitzat d'una transacció anterior o simultània en cas
            d'usuari amb varis logins actius.
            Si l'hora és recent --> podria ser vàlid en un altre login, ha d'esperar-se.
            en altre cas s'elimina i es crea un nou
            '''
            if esRecent(pagament.data_hora_pagament):
                return render(
                            request,
                            'resultat.html', 
                            {'msgs': {'errors': [], 'warnings': [], 'infos': ['PAGAMENT JA OBERT EN UN ALTRE CONNEXIÓ. CANCEL·LA O ESPERA UNS MINUTS.']} },
                         )
            else:
                # es considera que ha caducat
                #  Crea nou pagament
                noup=clonePagament(pagament)
                #logPagaments('Pagament caducat: '+str(pagament.pk)+' alumne: '+str(pagament.alumne.id))
                if not pagament.ordre_pagament and pagament.alumne:
                    # es genera ordre_pagament si fa falta
                    pagament.ordre_pagament=generaOrdre(pagament)
                # marca com erroni
                pagament.alumne=None
                pagament.data_hora_pagament=datetime.now()
                #guarda pagament caducat
                pagament.save()
                #Nou pagament
                pagament=noup
                pk=pagament.pk
    
    if pagament.sortida:
        sortida = pagament.sortida
        preu = sortida.preu_per_alumne
        descripcio_sortida = sortida.programa_de_la_sortida
        data_limit_pagament = sortida.termini_pagament
    else:
        sortida = pagament.quota
        preu = pagament.importReal
        descripcio_sortida = sortida.descripcio
        data_limit_pagament = pagament.getdataLimit
    
    if request.method == 'POST':
        form = PagamentForm(request.POST, initial={
            'sortida': sortida,
        })

    else:
        form = PagamentForm(initial={
            'sortida': sortida,
            'acceptar_condicions': False
        })
    return render(request, 'formPagamentOnline.html', {'form': form, 'alumne':alumne, 'pk':pk, 
                                                       'sortida':sortida if pagament.sortida else descripcio_sortida + "("+str(pagament.quota.any)+")", 
                                                       'descripcio':descripcio_sortida, 'preu':preu, 'limit':data_limit_pagament,'pagat':pagament.pagament_realitzat, 'next': nexturl,})

@login_required
def pagoOnlineKO(request, pk):
    '''
    Pagament amb errors
    '''
    
    pagament = get_object_or_404(Pagament, pk=pk)

    if pagament.estat=='T':
        '''
        Pagament que no ha finalitzat d'una transacció anterior o simultània en cas
        d'usuari amb varis logins actius.

        Es considera error en pagament, no es pot fer servir un altre cop el mateix ordre_pagament.
        Crea un pagament clone, com és un pagament diferent tindrà un ordre_pagament nou.
        El pagament cancel·lat es guarda amb alumne NULL
        '''
        noup=clonePagament(pagament)
        pagament.pagament_realitzat = False
        pagament.data_hora_pagament = datetime.now()
        pagament.alumne=None
        pagament.save()
    
    return render(
                request,
                'resultat.html', 
                {'msgs': {'errors': [], 'warnings': [], 'infos': ['PAGAMENT NO EFECTUAT']} },
             )

@login_required
def passarella(request, pk):
    '''
    Connecta amb la passarel·la redsys
    '''
    
    pagament = get_object_or_404(Pagament, pk=pk)
    if pagament.pagament_realitzat:
        # Ja completat, pot pasar si un usuari té diversos logins i paga des de tots.
        return HttpResponseRedirect(reverse('sortides__sortides__pago_on_line', kwargs={'pk': pk})+'?next='+request.GET.get('next'))
    
    if pagament.estat=='E':
        '''
        Pagament erroni, es pot donar el cas si diversos logins actius
        No s'ha de fer res.
        '''
        return HttpResponseRedirect(reverse('relacio_families__informe__el_meu_informe'))

    # Pagament pendent
    if pagament.estat=='T':
        '''
        Pagament que no ha finalitzat d'una transacció anterior o simultània en cas
        d'usuari amb varis logins actius.
        '''
        return render(
                    request,
                    'resultat.html', 
                    {'msgs': {'errors': [], 'warnings': [], 'infos': ['PAGAMENT JA OBERT EN UN ALTRE CONNEXIÓ. CANCEL·LA O ESPERA UNS MINUTS.']} },
                 )
            
    # Marca el pagament com Transmés a la passarella
    pagament.estat='T'
    # Marca l'hora d'inici
    pagament.data_hora_pagament=datetime.now()
    pagament.save()
    
    if pagament.sortida:
        sortida = pagament.sortida
        preu = sortida.preu_per_alumne
        titol = sortida.titol_de_la_sortida
        c,k,e = TPVsettings(request.user)
        codiComerç = sortida.tpv.codi if sortida.tpv else c
        keyComerç = sortida.tpv.key if sortida.tpv else k
        entorn_real = sortida.tpv.entornReal if sortida.tpv else e
        
    else:
        quota = pagament.quota
        preu = pagament.importReal
        titol = quota.descripcio
        c,k,e = TPVsettings(request.user)
        codiComerç = quota.tpv.codi if quota.tpv else c
        keyComerç = quota.tpv.key if quota.tpv else k
        entorn_real = quota.tpv.entornReal if quota.tpv else e

    #preparar parametres per redsys   --------------------------------------------
    #adaptació del codi existent al següent mòdul https://pypi.org/project/odoo11-addon-payment-redsys/

    values = {
        'DS_MERCHANT_AMOUNT': str(int(round(preu * 100))),
        # Es genera un ordre de pagament concret, segons les seves dades
        'DS_MERCHANT_ORDER': generaOrdre(pagament),
        'DS_MERCHANT_MERCHANTCODE': codiComerç,
        'DS_MERCHANT_CURRENCY': '978',
        'DS_MERCHANT_TRANSACTIONTYPE': '0',
        'DS_MERCHANT_TERMINAL': '001',
        'DS_MERCHANT_MERCHANTURL': URL_DJANGO_AULA + reverse('sortides__sortides__retorn_transaccio', kwargs={'pk':pk}),
        'Ds_Merchant_ProductDescription': titol,
        'Ds_Merchant_ConsumerLanguage': '003',
        'DS_MERCHANT_URLOK': URL_DJANGO_AULA.replace('/','\/') + reverse('sortides__sortides__pago_on_line',
                                                                          kwargs={'pk': pk})+'?next='+request.GET.get('next'),
        'DS_MERCHANT_URLKO': URL_DJANGO_AULA.replace('/','\/') + reverse('sortides__sortides__pago_on_lineKO',
                                                                          kwargs={'pk': pk})+'?next='+request.GET.get('next'),
        #'Ds_Merchant_Paymethods': 'T',
    }
    data = json.dumps(values)
    data = base64.b64encode(data.encode())
    params = data.decode("utf-8")
    #-----------------------------------------------------------------------------

    #pagament.ordre_pagament = values['DS_MERCHANT_ORDER']
    #pagament.save()

    # preparar firma per redsys -------------------------------------------
    #adaptació del codi existent al següent mòdul https://pypi.org/project/odoo11-addon-payment-redsys/

    params_dic = json.loads(base64.b64decode(params).decode())

    cipher = DES3.new(
        key=base64.b64decode(keyComerç),
        mode=DES3.MODE_CBC,
        IV=b'\0\0\0\0\0\0\0\0')
    ordre = str(params_dic['DS_MERCHANT_ORDER'])
    diff_block = len(ordre) % 8
    zeros = diff_block and (b'\0' * (8 - diff_block)) or b''
    key = cipher.encrypt(str.encode(ordre + zeros.decode()))
    params64 = params.encode()
    dig = hmac.new(
        key=key,
        msg=params64,
        digestmod=hashlib.sha256).digest()
    signature = base64.b64encode(dig).decode()
    # ----------------------------------------------------------------------------


    return render(request, 'formredsys.html', {'entorn_real': entorn_real,
                                                'Ds_MerchantParameters': params,
                                                'Ds_Signature': signature,
                                               })


@csrf_exempt
def retornTransaccio(request,pk):
    '''
    Comprova el resultat i actualitza el pagament.
    '''

    ips_permeses = ['195.76.9.117',
                    '195.76.9.149',
                    '193.16.243.13',
                    '193.16.243.173',
                    '195.76.9.187',
                    '195.76.9.222',
                    '194.224.159.47',
                    '194.224.159.57']  # ip's Banc Sabadell
    ip = request.META.get('REMOTE_ADDR')
    if ip not in ips_permeses:
        missatge = ERROR_IP_NO_PERMESA_REPORT_PAGAMENT_ONLINE
        txt = missatge.format(ip)
        tipus_de_missatge = tipusMissatge(missatge)
        logPagaments(txt, tipus_de_missatge)
        return HttpResponseServerError()

    # rebent dades de redsys   --------------------------------------------
    #adaptació del codi existent al següent mòdul https://pypi.org/project/odoo11-addon-payment-redsys/

    version = request.POST.get('Ds_SignatureVersion', '')
    parameters = request.POST.get('Ds_MerchantParameters', '')
    firma_rebuda = request.POST.get('Ds_Signature', '')

    parameters_dic = json.loads(base64.b64decode(parameters).decode())
    reference = urllib.parse.unquote(parameters_dic.get('Ds_Order', ''))
    pay_id = parameters_dic.get('Ds_AuthorisationCode')
    shasign = firma_rebuda.replace('_', '/').replace('-', '+')
    if not reference or not pay_id or not shasign:
        missatge = ERROR_FALTEN_DADES_REPORT_PAGAMENT_ONLINE
        txt = missatge.format(reference, pay_id, shasign)
        tipus_de_missatge = tipusMissatge(missatge)
        logPagaments(txt, tipus_de_missatge)
        return HttpResponseServerError()

    # -------------------------------------------------------------------------

    # verificant conincidència signatures --------------------------------------
    #adaptació del codi existent al següent mòdul https://pypi.org/project/odoo11-addon-payment-redsys/
    pagament = get_object_or_404(Pagament, pk=pk)
    if pagament.sortida:
        sortida = pagament.sortida
        _,k,_ = TPVsettings(request.user)
        keyComerç = sortida.tpv.key if sortida.tpv else k
    else:
        quota = pagament.quota
        _,k,_ = TPVsettings(request.user)
        keyComerç = quota.tpv.key if quota.tpv else k
    
    cipher = DES3.new(
        key=base64.b64decode(keyComerç),
        mode=DES3.MODE_CBC,
        IV=b'\0\0\0\0\0\0\0\0')
    ordre = str(parameters_dic['Ds_Order'])
    diff_block = len(ordre) % 8
    zeros = diff_block and (b'\0' * (8 - diff_block)) or b''
    key = cipher.encrypt(str.encode(ordre + zeros.decode()))
    params64 = parameters.encode()
    dig = hmac.new(
        key=key,
        msg=params64,
        digestmod=hashlib.sha256).digest()
    shasign_check = base64.b64encode(dig).decode()

    if shasign_check != shasign:
        missatge = ERROR_SIGNATURES_REPORT_PAGAMENT_ONLINE
        txt = missatge.format(shasign, shasign_check, request.POST)
        tipus_de_missatge = tipusMissatge(missatge)
        logPagaments(txt, tipus_de_missatge)
        return HttpResponseServerError()

    # -------------------------------------------------------------------------
    try:
        ds_response = parameters_dic.get('Ds_Response')
        if int(ds_response) in range(0,100):
            # Pagament OK
            pagament.pagament_realitzat = True
            try:
                data = urllib.parse.unquote(parameters_dic['Ds_Date'])
                hora = urllib.parse.unquote(parameters_dic['Ds_Hour'])
                pagament.data_hora_pagament = datetime.strptime(data + ' ' + hora, '%d/%m/%Y %H:%M')
            except Exception as e:
                pagament.data_hora_pagament = datetime.now()
            pagament.ordre_pagament = reference
            pagament.estat='F'
            if not pagament.alumne:
                # S'han generat varis pagaments des de sessions diferents
                # i aquest ha quedat marcat com error.
                # Determina alumne segons ordre de pagament i comunica als Administradors.
                pagament.alumne=Alumne.objects.get(pk=int(pagament.ordre_pagament[:-7]))
                logPagaments('Pagament caducat pasa a ok: '+str(pagament.pk)+' alumne: '+str(pagament.alumne.id))
            pagament.save()
        else:
            '''
             Error en pagament o cancel·lat, no es pot fer servir un altre cop el mateix ordre_pagament.
             Si estat diferent a 'E', crea un pagament clone, com és un pagament diferent tindrà un ordre_pagament nou.
             Si estat ja és 'E' aleshores no fa falta fer clone.
             El pagament cancel·lat es guarda amb alumne NULL
            '''
            if pagament.estat!='E': noup=clonePagament(pagament)
            pagament.pagament_realitzat = False
            
            try:
                data = urllib.parse.unquote(parameters_dic['Ds_Date'])
                hora = urllib.parse.unquote(parameters_dic['Ds_Hour'])
                pagament.data_hora_pagament = datetime.strptime(data + ' ' + hora, '%d/%m/%Y %H:%M')
            except Exception as e:
                pagament.data_hora_pagament = datetime.now()
            pagament.ordre_pagament = reference
            pagament.alumne=None
            pagament.save()
    except Exception as e:
        txt = 'Pagament: '+str(pk)+'\n' + str(e) + ' apps.sortides.views.retornTransaccio'
        logPagaments(txt)
    
    return HttpResponse('')

@login_required
def pagoEfectiu(request, pk):
    from aula.apps.sortides.forms import PagamentEfectiuForm
    
    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials

    pagament = get_object_or_404(Pagament, pk=pk)
    sortida = pagament.sortida
    preu = sortida.preu_per_alumne
    alumne = pagament.alumne
    fEsGrupSecrretaria = request.user.groups.filter(name__in=[u"secretaria"]).exists()

    potEntrar = (fEsGrupSecrretaria)
    if not potEntrar:
        raise Http404

    if request.method == 'POST':
        form = PagamentEfectiuForm(request.POST, initial={
            'sortida': sortida,
            'ordre_pagament': "Efectiu-{0}".format(random.randint(0, 9999)),
            'data_hora_pagament': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'alumne': alumne,
            'preu': preu,
        })
        if form.is_valid():
            try:
                pagament.data_hora_pagament = form.cleaned_data['data_hora_pagament']
                pagament.ordre_pagament = form.cleaned_data['ordre_pagament']
                pagament.pagament_realitzat = True
                pagament.observacions = form.cleaned_data['observacions']
                pagament.save()
                return HttpResponseRedirect(reverse('sortides__sortides__detall_pagament', kwargs={'pk': sortida.pk}))
            except ValidationError as e:
                for _, v in e.message_dict.items():
                    form._errors.setdefault(NON_FIELD_ERRORS, []).extend(v)
    else:
        form = PagamentEfectiuForm(initial={
            'sortida': sortida,
            'ordre_pagament': "Efectiu-{0}".format(random.randint(0, 9999)),
            'data_hora_pagament': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'alumne' : alumne,
            'preu': preu,
        })

    return render(request,
                  'form.html',
                  {'form': form, 'head': u'Pagament Efectiu',
                   'titol_formulari': u"Es realitza el pagament en efectiu d'una activitat programada per pagar online",
                                                        })


@login_required()
@group_required(['professors'])
def detallPagament(request, pk):

    credentials = tools.getImpersonateUser(request)
    (user, _) = credentials
    professor = User2Professor(user)
    fEsDireccioOrGrupSortides = request.user.groups.filter(name__in=[u"direcció", u"sortides"]).exists()
    sortida = get_object_or_404(Sortida, pk=pk)
    potEntrar = (sortida.tipus_de_pagament == 'ON' and (professor in sortida.professors_responsables.all()
                                                        or fEsDireccioOrGrupSortides
                                                        or professor in sortida.altres_professors_acompanyants.all()))
    if not potEntrar:
        raise Http404

    head = 'Sortida: {0}  ({1} €)'.format(sortida.titol_de_la_sortida, str(sortida.preu_per_alumne))


    report = []

    taula = tools.classebuida()

    taula.capceleres = []

    capcelera = tools.classebuida()
    capcelera.amplade = 40
    capcelera.contingut = 'Alumne'
    capcelera.enllac = ""
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 40
    capcelera.contingut = u'Pagat'
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = u'Codi Pagament'
    taula.capceleres.append(capcelera)

    taula.fileres = []

    for pagament in SortidaPagament.objects.filter(sortida=sortida).order_by('alumne'):
        filera = []

        # -Alumne--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = pagament.alumne
        filera.append(camp)

        # -Pagat--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = pagament.data_hora_pagament.strftime('%d/%m/%Y %H:%M') if pagament.data_hora_pagament and pagament.pagament_realitzat else 'No'
        filera.append(camp)

        # -Codi--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        ordre= pagament.ordre_pagament if pagament.ordre_pagament and pagament.pagament_realitzat else ''
        observacions = pagament.observacions if pagament.observacions and pagament.pagament_realitzat else ''
        camp.contingut = '{0} - {1}'.format(ordre,observacions) if observacions else ordre
        filera.append(camp)

        # -Efectiu--------------------------------------------
        fEsGrupSecrretaria = request.user.groups.filter(name__in=[u"secretaria"]).exists()
        if (fEsGrupSecrretaria):
            camp = tools.classebuida()
            camp.enllac = "/sortides/pagoEfectiu/{0}/".format( pagament.pk ) if not pagament.pagament_realitzat else None
            camp.contingut = u'''Pagament/Efectiu''' if not pagament.pagament_realitzat else ''
            filera.append(camp)

        # --
        taula.fileres.append(filera)
    report.append(taula)

    return render(
        request,
        'report_detall_pagament_sortida.html',
        {'report': report,
          'head': head,
         },
    )

@login_required
@group_required(['direcció','administradors','tpvs'])
def assignaQuotes(request):
    '''
    Selecciona els paràmetres per a l'assignació de quotes
    '''
    from aula.apps.sortides.forms import EscollirCursForm

    if request.method == 'POST':
        form = EscollirCursForm(request.user, request.POST)
        if form.is_valid():
            curs=form.cleaned_data['curs_list']
            tipus=form.cleaned_data['tipus_quota']
            nany=form.cleaned_data['year']
            auto=form.cleaned_data['automatic']
            return HttpResponseRedirect(reverse_lazy("gestio__quotes__assigna", 
                                                     kwargs={"curs": curs.id, "tipus": tipus.id, "nany":nany, "auto":auto}))
    else:
        form = EscollirCursForm(request.user)
    return render(
                request,
                'form.html', 
                {'form': form, 
                 },
                )

def get_QuotaPagament(alumne, tipus, nany=None):
    '''
    alumne del que volem la quota
    tipus de quota a escollir
    nany que correspon a la quota, si None utilitza any actual
    Retorna queryset amb la quota que correspon a l'alumne, tipus de quota i any indicats.
    '''
    
    if not nany:
        nany=django.utils.timezone.now().year
    return QuotaPagament.objects.filter(alumne=alumne, quota__tipus=tipus, quota__any=nany)

@login_required
@group_required(['direcció','administradors','tpvs'])
def quotesCurs( request, curs, tipus, nany, auto ):
    '''
    Mostra les quotes corresponents i permet fer canvis.
    curs d'on es seleccionen els alumnes
    tipus de quota que es gestiona
    nany any de la quota
    auto indica si s'ha de proposar la quota per a cada alumne de manera automàtica
    
    '''
    from aula.apps.sortides.forms import PagQuotesForm
    from django.forms import formset_factory

    auto=str(auto)=='True'
    if request.method == "POST":
        formsetQuotes = formset_factory(PagQuotesForm) 
        formset = formsetQuotes(request.POST, form_kwargs={'tipus': tipus, 'any': nany}) 
        if formset.is_valid():
            fraccions_esborrades=()
            for form in formset:
                pg = form.cleaned_data
                quota = pg.get('quota')
                pkp = pg.get('pkp')
                pka = pg.get('pka')
                if pkp!='None' and int(pkp) in fraccions_esborrades:
                    continue
                pagament=QuotaPagament.objects.get(pk=pkp) if pkp!='None' else None
                a=Alumne.objects.get(pk=pka)
                if quota:
                    fracciona = pg.get('fracciona') and quota.importQuota>0
                    if pagament:
                        fet_act=pagament.pagamentFet
                        canviFracc=not pagament.fracciona and fracciona and not fet_act
                        canviQuota=pagament.quota!=quota and not fet_act and not pagament.fracciona
                        crea=canviQuota or canviFracc
                    else:
                        canviQuota=False
                        canviFracc=False
                        crea=True

                    if canviQuota or canviFracc:
                        QuotaPagament.objects.filter(alumne=a, quota__any=nany, quota__tipus=tipus).\
                            exclude(pagament_realitzat=True).delete()
                    if crea:
                        if fracciona:
                            import1=round(float(quota.importQuota)/2.00,2)
                            import2=float(quota.importQuota)-import1
                            p=QuotaPagament(alumne=a, quota=quota, fracciona=True, importParcial=import1, dataLimit=quota.dataLimit)
                            p.save()
                            p=QuotaPagament(alumne=a, quota=quota, fracciona=True, importParcial=import2, 
                                            dataLimit=quota.dataLimit + relativedelta(months=+3))
                            p.save()
                        else:
                            p=QuotaPagament(alumne=a, quota=quota)
                            p.save()
                else:
                    # Quota esborrada
                    if pagament and not pagament.pagament_realitzat:
                        #esborrar pagament o pagaments
                        #si fracciona depén dels pagaments previs ja fets
                        if not pagament.fracciona:
                            pagament.delete()
                        else:
                            p=get_QuotaPagament(a, tipus, nany).filter(fracciona=True)
                            # Esborra només si no s'ha pagat cap fracció
                            if p and not p.filter(pagament_realitzat=True):
                                fraccions_esborrades=fraccions_esborrades+tuple(p.values_list('pk', flat = True))
                                p.delete()

            llista=Alumne.objects.filter(grup__curs__id=curs,
                                 data_baixa__isnull=True,
                                ).order_by('grup__nom_grup', 'cognoms', 'nom')
    
            llistapag=[]
            for a in llista:
                pagaments=get_QuotaPagament(a, tipus, nany)
                email=a.correu_relacio_familia_pare if a.correu_relacio_familia_pare else a.correu_relacio_familia_mare
                if pagaments:
                    for pg in pagaments:
                        llistapag.append({
                            'pkp': pg.pk,
                            'pka': a.pk,
                            'cognoms': a.cognoms,
                            'nom':  a.nom ,
                            'grup': a.grup,
                            'correu': email,
                            'quota': pg.quota,
                            'estat': 'Ja pagat' if pg.pagamentFet else 'Pendent',
                            'fracciona': pg.fracciona
                            })

            if len(llistapag)==0:
                return render(
                            request,
                            'resultat.html', 
                            {'msgs': {'errors': [], 'warnings': [], 'infos': ['Sense quotes assignades']} },
                         )
            formsetQuotes = formset_factory(PagQuotesForm, extra=0)
            formset=formsetQuotes(form_kwargs={'tipus': tipus, 'any': nany}, initial= llistapag)
            
    else:
        quotacurs=None
        if auto:
            '''
            Assigna quota automàticament segons el curs, tipus i any.
            Si no n'hi ha cap, farà servir per defecte una quota del mateix tipus si només n'hi ha una possible.
            '''
            c=Curs.objects.get(id=curs)
            try:
                ncurs=str(int(c.nom_curs)+1)
                quotacurs=Quota.objects.filter(curs__nivell=c.nivell, curs__nom_curs=ncurs, any=nany, tipus=tipus)
            except:
                quotacurs=None
            
            if not quotacurs:
                # No troba una quota adequada, comprova si existeixen altres quotes del mateix tipus
                quotacurs=Quota.objects.filter(any=nany, tipus=tipus)
                if quotacurs.count()!=1:
                    # Si troba varies no selecciona cap, si només troba una aleshores la fa servir per defecte
                    quotacurs=None
            
            if quotacurs:
                quotacurs=quotacurs[0]
            else:
                quotacurs=None
        
        llista=Alumne.objects.filter(grup__curs__id=curs,
                             data_baixa__isnull=True,
                            ).order_by('grup__nom_grup', 'cognoms', 'nom')
        if not llista:
            return render(
                        request,
                        'resultat.html', 
                        {'msgs': {'errors': [], 'warnings': [], 'infos': ['Sense quotes per assignar']} },
                     )

        llistapag=[]
        for a in llista:
            pagaments=get_QuotaPagament(a, tipus, nany)
            email=a.correu_relacio_familia_pare if a.correu_relacio_familia_pare else a.correu_relacio_familia_mare
            if pagaments:
                for pg in pagaments:
                    llistapag.append({
                        'pkp': pg.pk,
                        'pka': a.pk,
                        'cognoms': a.cognoms,
                        'nom':  a.nom,
                        'grup': a.grup,
                        'correu': email,
                        'quota': pg.quota,
                        'estat': 'Ja pagat' if pg.pagamentFet else 'Pendent',
                        'fracciona': pg.fracciona
                        })
            else:
                llistapag.append({
                    'pkp': 'None',
                    'pka': a.pk,
                    'cognoms': a.cognoms,
                    'nom':  a.nom ,
                    'grup': a.grup,
                    'correu': email,
                    'quota': quotacurs,
                    'estat': 'No assignat',
                    'fracciona': False
                    })

        if len(llistapag)==0:
            return render(
                        request,
                        'resultat.html', 
                        {'msgs': {'errors': [], 'warnings': [], 'infos': ['Sense quotes per assignar']} },
                     )
        
        formsetQuotes = formset_factory(PagQuotesForm, extra=0)
        formset=formsetQuotes(form_kwargs={'tipus': tipus, 'any': nany}, initial= llistapag)  

            
    return render(
                  request,
                  "formsetgrid.html", 
                  { "formset": formset,
                    "head": "Assignació quotes",
                    }
                )

def acumulatsQuotesCurs(tpv, nany=None):
    '''
    tpv que correspon als pagaments a seleccionar
    nany que correspon a la quota, si None utilitza any actual
    Agrupa per quotes que corresponen a cursos.
    Retorna un diccionari amb tots els acumulats per quotes i mesos i quantitat pendent
    {{quota1: {'pendent':nnnnn, 1:nnnnn, 2:nnnnn, ... 12:nnnnn},
     {quota2: {'pendent':nnnnn, 1:nnnnn, 2:nnnnn, ... 12:nnnnn},
     ... }
    '''
    
    from django.db.models import Sum
    
    if not nany:
        nany=django.utils.timezone.now().year
    
    totfet=QuotaPagament.objects.filter(quota__tpv=tpv, pagament_realitzat=True, data_hora_pagament__year=nany)\
                    .exclude(quota__curs__isnull=True)\
                    .values_list('quota','data_hora_pagament__month')\
                    .annotate(total=Sum('quota__importQuota', filter=Q(fracciona=False)))\
                    .annotate(totalf=Sum('importParcial', filter=Q(fracciona=True)))
    
    totpendent=QuotaPagament.objects.filter(quota__tpv=tpv, pagament_realitzat=False, alumne__isnull=False)\
                    .exclude(quota__curs__isnull=True)\
                    .values_list('quota')\
                    .annotate(total=Sum('quota__importQuota', filter=Q(fracciona=False)))\
                    .annotate(totalf=Sum('importParcial', filter=Q(fracciona=True)))
    
    calcul={}
    
    for p in list(totfet):
        q, m, t1, t2 = p
        tot=(t1 if t1 else 0) + (t2 if t2 else 0)
        if not q in calcul:
            calcul[q]={}
        calcul[q][m]=tot
    
    for p in list(totpendent):
        q, t1, t2 = p
        tot=(t1 if t1 else 0) + (t2 if t2 else 0)
        if not q in calcul:
            calcul[q]={}
        calcul[q]['pendent']=tot
    
    return calcul

def acumulatsQuotesGen(tpv, nany=None):
    '''
    tpv que correspon als pagaments a seleccionar
    nany que correspon a la quota, si None utilitza any actual
    Selecciona quotes genèriques (sense curs), les agrupa per nivells educatius.

    Retorna un diccionari amb tots els acumulats per nivells i mesos i quantitat pendent
    {{'nivell1': {'pendent':nnnnn, 1:nnnnn, 2:nnnnn, ... 12:nnnnn},
     {'nivell2': {'pendent':nnnnn, 1:nnnnn, 2:nnnnn, ... 12:nnnnn},
     ... }
    '''
    
    from django.db.models import Sum
    
    if not nany:
        nany=django.utils.timezone.now().year
    
    totfet=QuotaPagament.objects.filter(quota__tpv=tpv, pagament_realitzat=True, 
                                        data_hora_pagament__year=nany,
                                        quota__curs__isnull=True)\
                    .values_list('alumne__grup__curs__nivell__nom_nivell','quota__tipus__nom','data_hora_pagament__month')\
                    .annotate(total=Sum('quota__importQuota', filter=Q(fracciona=False)))\
                    .annotate(totalf=Sum('importParcial', filter=Q(fracciona=True)))
    
    totpendent=QuotaPagament.objects.filter(quota__tpv=tpv, pagament_realitzat=False, alumne__isnull=False,
                                            quota__curs__isnull=True)\
                    .values_list('alumne__grup__curs__nivell__nom_nivell','quota__tipus__nom')\
                    .annotate(total=Sum('quota__importQuota', filter=Q(fracciona=False)))\
                    .annotate(totalf=Sum('importParcial', filter=Q(fracciona=True)))
    
    calcul={}
    
    for p in list(totfet):
        n, x, m, t1, t2 = p
        if not bool(n): n='Esborrats'
        n=str(n)+'-'+str(x)
        tot=(t1 if t1 else 0) + (t2 if t2 else 0)
        if not n in calcul:
            calcul[n]={}
        calcul[n][m]=tot
    
    for p in list(totpendent):
        n, x, t1, t2 = p
        n=str(n)+'-'+str(x)
        tot=(t1 if t1 else 0) + (t2 if t2 else 0)
        if not n in calcul:
            calcul[n]={}
        calcul[n]['pendent']=tot
    
    return calcul

def acumulatsActivitats(tpv, nany=None):
    '''
    tpv que correspon als pagaments a seleccionar, només s'admet tpv 'centre' o None
    nany que correspon a la sortida, si None utilitza any actual
    Selecciona pagaments d'activitats/sortides, els agrupa per activitat/sortida.

    Retorna un diccionari amb tots els acumulats per activitats i mesos i quantitat pendent
    {{'activitat': {'pendent':nnnnn, 1:nnnnn, 2:nnnnn, ... 12:nnnnn},
     {'activitat': {'pendent':nnnnn, 1:nnnnn, 2:nnnnn, ... 12:nnnnn},
     ... }
    '''
    
    from django.db.models import Sum
    
    # Només es permet afegir les activitats/sortides si tpv és el de defecte
    if tpv and tpv.nom!='centre':
        return {}
    
    if not nany:
        nany=django.utils.timezone.now().year
        
    llistaSortides=Sortida.objects.filter(preu_per_alumne__isnull=False,
                                        notificasortida__alumne__isnull=False).distinct()
    
    totfet=SortidaPagament.objects.filter(pagament_realitzat=True, sortida__in=llistaSortides,
                                        #alumne__isnull=False,
                                        data_hora_pagament__year=nany)\
                    .values_list('sortida__id','sortida__titol_de_la_sortida','data_hora_pagament__month')\
                    .annotate(total=Sum('sortida__preu_per_alumne'))
    
    totpendent=SortidaPagament.objects.filter(pagament_realitzat=False, sortida__in=llistaSortides,
                    alumne__isnull=False)\
                    .values_list('sortida__id','sortida__titol_de_la_sortida')\
                    .annotate(total=Sum('sortida__preu_per_alumne'))
    
    calcul={}
    
    for p in list(totfet):
        _, t, m, tot = p
        n='activitat: '+str(t)
        if not n in calcul:
            calcul[n]={}
        calcul[n][m]=tot
    
    for p in list(totpendent):
        _, t, tot = p
        n='activitat: '+str(t)
        if not n in calcul:
            calcul[n]={}
        calcul[n]['pendent']=tot
    
    return calcul

def fullcalculQuotes(tpv, nany=None):
    '''
    tpv que correspon als pagaments a seleccionar
    nany que correspon a la quota, si None utilitza any actual
    Retorna un full de càlcul xlsx amb els acumulats i pagaments pendents
    '''
    
    import xlsxwriter
    import io
    
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    
    if not nany:
        nany=django.utils.timezone.now().year
    
    acumulats=acumulatsQuotesCurs(tpv, nany)
    acumGen=acumulatsQuotesGen(tpv, nany)
    acumAct=acumulatsActivitats(tpv, nany)
    totes=Quota.objects.filter(importQuota__gt=0).values_list('id').order_by('curs__nom_curs_complert', 'descripcio')
    
    worksheet = workbook.add_worksheet('Acumulats')
    
    num_format = workbook.add_format()
    num_format.set_num_format('0.00')
    
    cap=['Concepte','Pendent']
    date=django.utils.timezone.now()
    for i in range(1,13):
        cap.append(date.replace(month=i, day=1).strftime('%B')[2:].strip())
    cap.append('Total Pagat')
    worksheet.set_column(0, 0, 30)
    worksheet.set_column(1, 14, 10)
    worksheet.write_string(0,0,tpv.descripcio+'-'+str(nany)+'. Dades a '+date.strftime('%d/%m/%Y %H:%M'))
    worksheet.write_row(1,0,cap)
    fila=2
    for q in totes:
        if q[0] in acumulats:
            a = acumulats[q[0]]
            quota=Quota.objects.get(id=q[0])
            worksheet.write(fila, 0, quota.descripcio+"("+quota.curs.nom_curs_complert+")")
            for m, v in a.items():
                if m=='pendent':
                    col=1
                else:
                    col=m+1 
                if v: worksheet.write_number(fila, col, v)
            worksheet.write_formula(fila, 14, '=SUM(C{0}:N{0})'.format(fila+1), num_format)
            fila=fila+1
    
    for t,a in acumGen.items():
        worksheet.write(fila, 0, t)
        for m, v in a.items():
            if m=='pendent':
                col=1
            else:
                col=m+1 
            if v: worksheet.write_number(fila, col, v)
        worksheet.write_formula(fila, 14, '=SUM(C{0}:N{0})'.format(fila+1), num_format)
        fila=fila+1
    
    for t,a in acumAct.items():
        worksheet.write(fila, 0, t)
        for m, v in a.items():
            if m=='pendent':
                col=1
            else:
                col=m+1 
            if v: worksheet.write_number(fila, col, v)
        worksheet.write_formula(fila, 14, '=SUM(C{0}:N{0})'.format(fila+1), num_format)
        fila=fila+1
    
    if fila>2:
        for t in range(ord('B'),ord('P')):
            worksheet.write_formula(fila, t-ord('A'), '=SUM({0}3:{0}{1})'.format(chr(t),fila), num_format)
    
    worksheet = workbook.add_worksheet('Pendents')
    worksheet.set_column(0, 4, 30)
    worksheet.write_string(0,0,'Pagaments pendents. Dades a '+date.strftime('%d/%m/%Y %H:%M'))
    worksheet.write_row(1,0,('Concepte','Alumne','Import','Data límit','Fraccionat'))
    fila=2
    pagq=QuotaPagament.objects.filter(quota__tpv=tpv, pagament_realitzat=False, alumne__isnull=False)\
                    .order_by('quota__dataLimit','quota__descripcio','alumne__cognoms','alumne__nom')
    # Només es permet afegir les activitats/sortides si tpv és el de defecte
    if not tpv or tpv.nom=='centre':
        pags=SortidaPagament.objects.filter(pagament_realitzat=False, sortida__preu_per_alumne__isnull=False,
                                        alumne__isnull=False, sortida__notificasortida__alumne__isnull=False)\
                                        .distinct()\
                                        .order_by('sortida__termini_pagament','sortida__titol_de_la_sortida',
                                                 'alumne__cognoms','alumne__nom')
    else:
        pags=SortidaPagament.objects.none()
    date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
    
    for p in pagq:
        worksheet.write_string(fila, 0, p.quota.descripcio )
        worksheet.write_string(fila, 1, str(p.alumne) )
        worksheet.write_number(fila, 2, p.quota.importQuota if not p.fracciona else p.importParcial )
        worksheet.write_datetime(fila, 3, p.quota.dataLimit if not p.fracciona else p.dataLimit, date_format )
        worksheet.write_string(fila, 4, 'SI' if p.fracciona else 'NO' )
        fila=fila+1
    for p in pags:
        if bool(p.sortida.preu_per_alumne) and p.sortida.preu_per_alumne>0:
            worksheet.write_string(fila, 0, 'activitat: '+p.sortida.titol_de_la_sortida )
            worksheet.write_string(fila, 1, str(p.alumne) )
            worksheet.write_number(fila, 2, p.sortida.preu_per_alumne )
            if p.sortida.termini_pagament: worksheet.write_datetime(fila, 3, p.sortida.termini_pagament, date_format )
            fila=fila+1
    
    if fila>2:
        worksheet.write_formula(fila, 2, '=SUM(C3:C{0})'.format(fila), num_format)
    
    workbook.close()
    return output

@login_required
@group_required(['direcció','administradors','tpvs'])
def totalsQuotes(request):
    '''
    Selecciona els paràmetres per a la descàrrega del full de càlcul
    '''
    
    from aula.apps.sortides.forms import EscollirTPV

    
    if request.method == 'POST':
        form = EscollirTPV(request.user, request.POST)
        if form.is_valid():
            nany=form.cleaned_data['year']
            tpv=form.cleaned_data['tpv']
            output=fullcalculQuotes(tpv,nany)
            output.seek(0)
            filename = tpv.descripcio+'-'+str(nany)+'-quotes.xlsx'
            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    
            return response

    else:
        form = EscollirTPV(request.user)
    return render(
                request,
                'form.html', 
                {'form': form, 
                 },
                )

@login_required
@group_required(['direcció','administradors','tpvs'])
def blanc( request ):
    return render(
                request,
                'blanc.html',
                    {},
                )
