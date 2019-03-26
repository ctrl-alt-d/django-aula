# This Python file uses the following encoding: utf-8
from aula.apps.missatgeria.missatges_a_usuaris import ACOMPANYANT_A_ACTIVITAT, tipusMissatge, RESPONSABLE_A_ACTIVITAT
from aula.utils.widgets import DateTextImput, bootStrapButtonSelect,\
    DateTimeTextImput
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

#helpers
from aula.utils import tools
from aula.apps.usuaris.models import User2Professor
from aula.apps.presencia.models import Impartir
from aula.apps.horaris.models import FranjaHoraria
from django.shortcuts import render, get_object_or_404
from django.template.context import RequestContext, Context
from aula.apps.sortides.rpt_sortidesList import sortidesListRpt
from aula.apps.sortides.models import Sortida
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django import forms
from aula.apps.sortides.table2_models import Table2_Sortides
from django_tables2.config import RequestConfig
from aula.utils.my_paginator import DiggPaginator
from django.shortcuts import render

from icalendar import Calendar, Event
from icalendar import vCalAddress, vText
from django.http.response import HttpResponse, Http404
from django.utils.datetime_safe import datetime
from django.conf import settings
from django.core.urlresolvers import reverse
from aula.apps.alumnes.models import Alumne, AlumneGrupNom
from django.contrib import messages
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.templatetags.tz import localtime
from django.utils.safestring import SafeText
from aula.apps.missatgeria.models import Missatge
from django.contrib.auth.models import User
from django.db.models import Q
from django.template import loader
from django.template.defaultfilters import slugify
from aula.utils.tools import classebuida
import codecs
from django.db.utils import IntegrityError


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
    import cgi
    import os
    from django import http
    
    excepcio = None

    #try:
        
    #resultat = StringIO.StringIO( )
    resultat = "/tmp/DjangoAula-temp-{0}-{1}.odt".format( time.time(), request.session.session_key )
    #context = Context( {'reports' : reports, } )
    path = os.path.join( settings.PROJECT_DIR,  '../customising/docs/autoritzacio2.odt') if din==4 else os.path.join( settings.PROJECT_DIR,  '../customising/docs/autoritzacio2-A5.odt')
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
        
#     except Exception, e:
#         excepcio = unicode( e )
        
    if True: #not excepcio:
        response = http.HttpResponse( contingut, content_type='application/vnd.oasis.opendocument.text')
        response['Content-Disposition'] = u'attachment; filename="{0}-{1}.odt"'.format( "autoritzacio_sortida", pk )
                                                     
    else:
        response = http.HttpResponse('''Als Gremlin no els ha agradat aquest fitxer! %s''' % cgi.escape(excepcio))
    
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
    
    RequestConfig(request, paginate={"klass":DiggPaginator , "per_page": 10}).configure(table)
        
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
    
    RequestConfig(request, paginate={"klass":DiggPaginator , "per_page": 10}).configure(table)
        
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

    #si sóc equip directiu només les que tinguin estat 'R' (Revisada pel coordinador)
    if socEquipDirectiu:
        filtre.append('R')
    #si sóc coordinador de sortides només les que tinguin estat 'P' (Proposada)
    if socCoordinador:
        filtre.append('P')
    
    sortides = ( Sortida
                   .objects
                   .exclude( estat = 'E' )
                   .filter( estat__in = filtre )
                   .distinct()
                  )    
    
    table = Table2_Sortides( data=list( sortides ), origen="Gestio" ) 
    table.order_by = '-calendari_desde' 
    
    RequestConfig(request, paginate={"klass":DiggPaginator , "per_page": 10}).configure(table)
        
    url = r"{0}{1}".format( settings.URL_DJANGO_AULA, reverse( 'sortides__sortides__ical' ) )    
        
    return render(
                  request, 
                  'gestioDeSortides.html', 
                  {'table': table,
                   'url': url,
                   }
                 )


@login_required
@group_required(['professors'])  # TODO: i grup sortides
def sortidaEdit(request, pk=None, clonar=False, origen=False):
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

    instance.credentials = credentials

    # És un formulari reduit?
    if settings.CUSTOM_FORMULARI_SORTIDES_REDUIT:
        exclude = ('alumnes_convocats', 'alumnes_que_no_vindran', 'alumnes_justificacio', 'data_inici', 'franja_inici', 'data_fi',
                   'franja_fi', 'codi_de_barres', 'empresa_de_transport', 'pagament_a_empresa_de_transport',
                   'pagament_a_altres_empreses', 'feina_per_als_alumnes_aula')
    else:
        exclude = ('alumnes_convocats', 'alumnes_que_no_vindran', 'alumnes_justificacio',)

    formIncidenciaF = modelform_factory(Sortida, exclude=exclude)

    if request.method == "POST":
        post_mutable = request.POST.copy()
        if 'esta_aprovada_pel_consell_escolar' not in post_mutable:
            post_mutable['esta_aprovada_pel_consell_escolar'] = 'P'

        form = formIncidenciaF(post_mutable, instance=instance)

        if form.is_valid():
            # Omplir camps de classes afectades
            if settings.CUSTOM_FORMULARI_SORTIDES_REDUIT:
                # Mirar si el dia d'inici de la sortida és lectiu
                if instance.calendari_desde.date() == (Impartir.objects.filter(dia_impartir__gte =instance.calendari_desde.date())
                                                               .values_list("dia_impartir", flat=True).first()):
                    # Mirar si encara queden hores per impartir
                    if instance.calendari_desde.time() < (Impartir.objects.filter(dia_impartir__gte=instance.calendari_desde.date())
                                                                  .order_by('horari__hora__hora_fi').values_list('horari__hora__hora_fi', flat=True).last()):
                        instance.data_inici = instance.calendari_desde.date()
                        instance.franja_inici = (FranjaHoraria.objects.filter(hora_inici__gte=instance.calendari_desde.time())
                                                 .order_by('hora_inici').first())
                        # El dia i hora d'inici de la sortida no queden hores per impartir, per tant serà el següent dia lectiu
                    else:
                        instance.data_inici = (Impartir.objects.filter(dia_impartir__gt=instance.calendari_desde.date())
                                               .order_by('dia_impartir').values_list('dia_impartir', flat=True).first())
                        instance.franja_inici = (FranjaHoraria.objects.order_by('hora_inici').first())
                else:
                    instance.data_inici = (Impartir.objects.filter(dia_impartir__gt=instance.calendari_desde.date())
                                           .order_by('dia_impartir').values_list('dia_impartir', flat=True).first())
                    instance.franja_inici = (FranjaHoraria.objects.order_by('hora_inici').first())

                # Mirar si el dia final de la sortida és lectiu
                if instance.calendari_finsa.date() == (Impartir.objects.filter(dia_impartir__lte=instance.calendari_finsa.date())
                                                               .values_list("dia_impartir", flat=True).last()):
                    # Mirar si encara queden hores per impartir
                    if instance.calendari_finsa.time() < (Impartir.objects.filter(dia_impartir__lte=instance.calendari_finsa.date())
                                                                  .order_by('horari__hora__hora_inici').values_list('horari__hora__hora_inici', flat=True).last()):

                        instance.data_fi = instance.calendari_finsa.date()
                        instance.franja_fi = (FranjaHoraria.objects.filter(hora_fi__lte=instance.calendari_finsa.time())
                                              .order_by('hora_fi').last())

                    # El dia i hora de fi de la sortida no queden hores per impartir, per tant serà la darrera impartició del dia
                    else:
                        instance.data_fi = (
                            Impartir.objects.filter(dia_impartir = instance.calendari_finsa.date()).values_list('dia_impartir', flat=True).last())
                        instance.franja_fi = (
                            FranjaHoraria.objects.order_by(
                                'hora_fi').last())
                else:
                    instance.data_fi = (
                        Impartir.objects.filter(dia_impartir__lt=instance.calendari_finsa.date())
                            .order_by('dia_impartir').values_list('dia_impartir', flat=True).last())
                    instance.franja_fi = (FranjaHoraria.objects.order_by('hora_fi').last())

                # Comprovem si la sortida en realitat no afecta cap hora d'impartició, això passa quan la data inicial > data final
                if (instance.data_fi < instance.data_inici):
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
                    except IntegrityError:
                        pass
                    
                #treure
                for alumne in ante - nous:
                    #aquest if no caldria. és només per seguretat.
                    try:
                        instance.alumnes_convocats.remove( alumne )
                    except IntegrityError:
                        pass

                nexturl =  r'/sortides/sortides{origen}'.format(origen=origen)
                return HttpResponseRedirect( nexturl )
            except ValidationError, e:
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
            except ValidationError, e:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  e.messages )

                nexturl =  r'/sortides/sortides{origen}'.format( origen = origen )
                return HttpResponseRedirect( nexturl )
            except ValidationError, e:
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
            except ValidationError, e:
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
   
    formIncidenciaF = modelform_factory(Sortida, fields=( 'altres_professors_acompanyants',  ) )

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
            except ValidationError, e:
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
    alumnes = [ [ u'Alumne', u'Grup', u'Nivell', u"Assistència" ], ]
    alumnes += [
                        [e,
                         e.grup.descripcio_grup,
                         e.grup.curs.nivell,
                         u"No assisteix a la sortida" if e in no_assisteixen else u"",
                        ]
                        for e in sortida.alumnes_convocats.all() 
                ]
    
    dades_sortida = detall + alumnes

    template = loader.get_template("export.csv")
    context = Context({
                         'capcelera':capcelera,
                         'dades':dades_sortida,
    })

    import os
    import cgi
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
        response = http.HttpResponse('''Als Gremlin no els ha agradat aquest fitxer! %s''' % cgi.escape(excepcio))

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
    
    

    
    
    
