# This Python file uses the following encoding: utf-8
from itertools import count
import random
from django.conf import settings
#templates
from django.forms.utils import ErrorDict

#formularis
from aula.apps.aules.models import ReservaAula
from aula.apps.presencia.forms import regeneraImpartirForm,ControlAssistenciaForm,\
    alertaAssistenciaForm, faltesAssistenciaEntreDatesForm,\
    marcarComHoraSenseAlumnesForm, passaLlistaGrupDataForm,\
    llistaLesMevesHoresForm, ControlAssistenciaFormFake
from aula.apps.presencia.forms import afegeixTreuAlumnesLlistaForm, afegeixAlumnesLlistaExpandirForm
from aula.apps.presencia.forms import afegeixGuardiaForm, calculadoraUnitatsFormativesForm

#models
from aula.apps.horaris.models import FranjaHoraria
from aula.apps.presencia.models import Impartir, ControlAssistencia
from aula.apps.alumnes.models import Alumne, AlumneNomSentit, Grup
from aula.apps.usuaris.models import User2Professor, Accio

#helpers
from aula.apps.presencia.regeneraImpartir import regeneraThread
from aula.utils.tools import getImpersonateUser, getSoftColor, executaAmbOSenseThread, unicode
from django.utils.safestring import SafeText
from django.apps import apps

#consultes
from django.db.models import Q

#auth
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

#workflow
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

#excepcions
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.http import Http404

#other
from django.utils.datetime_safe import datetime, date
from django import forms
from aula.apps.assignatures.models import Assignatura
from aula.apps.presencia.reports import alertaAssitenciaReport, indicadorsReport
from aula.apps.presencia.rpt_faltesAssistenciaEntreDatesProfessor import faltesAssistenciaEntreDatesProfessorRpt
from django.forms.models import modelformset_factory
from django.forms.widgets import RadioSelect, HiddenInput, TextInput
from aula.apps.BI.utils import dades_dissociades
from aula.apps.BI.prediccio_assistencia import predictTreeModel
from aula.apps.presencia.business_rules.impartir import impartir_despres_de_passar_llista
from aula.apps.alumnes.gestioGrups import grupsPotencials

#template filters
from django.template.defaultfilters import date as _date
from django.contrib import messages
from django.urls import reverse
from aula.apps.presenciaSetmanal.views import ProfeNoPot
  
#vistes -----------------------------------------------------------------------------------
@login_required
@group_required(['direcció','administradors'])
def regeneraImpartir(request):
    
    head=u'Reprogramar classes segons horari actual' 

    if request.method == 'POST':
        form = regeneraImpartirForm(request.POST)
        if form.is_valid():
            
            r=regeneraThread(
                            data_inici=form.cleaned_data['data_inici'], 
                            franja_inici = form.cleaned_data['franja_inici'],
                            user = request.user  
                            )
            r.start()
            errors=[]
            warnings=[]
            infos=[u'Iniciat procés regeneració']
            resultat = {   'errors': errors, 'warnings':  warnings, 'infos':  infos }
            return render(
                    request,
                    'resultat.html', 
                    {'head': head ,
                     'msgs': resultat },
            )
    else:
        form = regeneraImpartirForm()
    return render(
                request,
                'form.html', 
                {'form': form, 
                 'head': head},
                )


#------------------------------------------------------------------------------------------
#
#@login_required
#def mostraImpartir( request, user=None, year=None, month=None, day=None ):
#    
#    import datetime as t
#    
#    professor = None
#    #si usuari arriba a none posem l'actual
#    if not user:
#        professor = User2Professor( request.user ) 
#        user = request.user.username
#    else:
#        professor = get_object_or_404( Professor, username = user )
#        
#    if professor is None:
#        HttpResponseRedirect( '/' )

@login_required
@group_required(['professors'])
def mostraImpartir( request, year=None, month=None, day=None ):
    
    import datetime as t
    
    credentials = getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user ) 
        
    if professor is None:
        HttpResponseRedirect( '/' )
    
    #si la data arriba a none posem la data d'avui    
    if not ( year and month and day):
        today = t.date.today()
        year = today.year
        month = today.month
        day = today.day
    else:
        year= int( year)
        month = int( month )
        day = int( day)
    
    #no es tracta del dia d'avui, sino la data amb la que treballem
    data_actual = t.date( year, month, day)

    #busquem el primer dilluns    
    dia_de_la_setmana = data_actual.weekday()
    delta = t.timedelta( days = (-1 * dia_de_la_setmana ) )
    data = data_actual + delta
    
    #per cada dia i franja horaria fem un element.
    impartir_tot=[]             #això són totes les franges horàries
    impartir_pendents=[]        #aquí les que potser no posarem (si estan buides i no hi ha més)
    dies_calendari=[]
    unDia = t.timedelta( days = 1)
    primera_franja_insertada = False
    for f in FranjaHoraria.objects.all():
        impartir_franja=[ [ [( unicode(f),'','','','','','','','','', )] , None ] ]
        te_imparticions = False
        for d in range(0,5):
            dia = data + d * unDia
            if dia not in dies_calendari : dies_calendari.append( dia )
            franja_impartir = Q(horari__hora = f)
            dia_impartir = Q( dia_impartir = dia )
            user_impartir = Q( horari__professor = professor )
            guardia = Q( professor_guardia  = professor )

            #TODO: Passar només la impartició i que el template faci la resta de feina.
            imparticions = [
                            (x.horari.assignatura.nom_assignatura,          #
                             x.horari.grup if  x.horari.grup else '',       #
                             x.get_nom_aula,                             #
                             x.pk,                                          #
                             getSoftColor( str(x.horari.grup)+
                                       (x.horari.assignatura.codi_assignatura if x.horari.assignatura else '')),    #
                             x.color(),                             
                             x.resum(),
                             (x.professor_guardia  and x.professor_guardia.pk == professor.pk),
                             x.hi_ha_alumnes_amb_activitat_programada,
                             x.esReservaManual,
                            )
                            for x in Impartir.objects.filter( franja_impartir & dia_impartir & (user_impartir | guardia)   ) ]
            
            impartir_franja.append( (imparticions, dia==data_actual) )
            te_imparticions = te_imparticions or imparticions   #miro si el professor ha d'impartir classe en aquesta franja
            
        if te_imparticions:                     #si ha d'impartir llavors afageixo la franja
            primera_franja_insertada = True
            impartir_tot += impartir_pendents   #afegeixo franges buides entre franges "plenes"
            impartir_pendents = []
            impartir_tot.append( impartir_franja )
        else:
            if primera_franja_insertada:
                impartir_pendents.append( impartir_franja ) #franges buides que potser caldrà afegir a l'horari
        
    nomProfessor = unicode( professor )

    qProfessor = Q(horari__professor=professor)
    qFinsAra = Q(dia_impartir__lt=datetime.today())
    qTeGrup = Q(horari__grup__isnull=False)
    imparticions = Impartir.objects.filter(qProfessor & qFinsAra & qTeGrup)
    nImparticios = imparticions.count()
    qSenseAlumnes = Q(controlassistencia__isnull=True)
    qProfeHaPassatLlista = Q(professor_passa_llista__isnull=False)
    nImparticionsLlistaPassada = \
        imparticions \
            .filter(qProfeHaPassatLlista | qSenseAlumnes) \
            .order_by()\
            .distinct()\
            .count()
    pct = ('{0:.1f}'.format(nImparticionsLlistaPassada * 100 / nImparticios) if nImparticios > 0 else 'N/A')
    msg = u'Has controlat presència en un {0}% de les teves classes'.format(pct)
    percentatgeProfessor = msg

    #navegacio pel calencari:
    altres_moments = [
           # text a mostrar, data de l'enllaç, mostrar-ho a mòbil, mostrar-ho a tablet&desktop
           [ '<< mes passat'    , data + t.timedelta( days = -30 ), False, True ],
           [ '< setmana passada' , data + t.timedelta( days = -7 ), False, True ],
           [ '< dia passat' , data_actual + t.timedelta( days = -1 ), True, False ],
           [ '< avui >'    , t.date.today, True, True ],
           [ 'dia vinent >' , data_actual + t.timedelta( days = +1 ), True, False ],
           [ 'setmana vinent >'  , data + t.timedelta( days = +7 ), False, True ],
           [ 'mes vinent >>'      , data + t.timedelta( days = +30 ), False, True ],
        ]
    
    calendari = [ (_date( d, 'D'), d.strftime('%d/%m/%Y'), d==data_actual) for d in dies_calendari]
    
    ###miscelania Sortides: ####################################################################################
    #q's sortida es ara
    data_llindar = max( data, t.date.today() )
    q_fi_sortida_menor_que_dilluns = Q( dia_impartir__lt =  data_llindar )
    q_inici_sortida_despres_divendres = Q( dia_impartir__gt = data + t.timedelta( days = 14 ) )
    q_sortida_no_inclou_setmana_vinent = ( q_fi_sortida_menor_que_dilluns | q_inici_sortida_despres_divendres  ) 
    #q es meu
    q_es_meu = Q( horari__professor = professor )
    
    imparticions_daquests_dies = Impartir.objects.filter( ~q_sortida_no_inclou_setmana_vinent & q_es_meu )
    
    alumnes_surten = any ( x.hi_ha_alumnes_amb_activitat_programada for x in imparticions_daquests_dies )
    
    if alumnes_surten:
        msg =  u"""Properament hi ha activitats previstes on els teus alumnes hi participen."""  
        messages.warning(request,  SafeText(msg ) )


    ###fi miscelania sortides.####################################################################################

    return render(
                request,
                'mostraImpartir.html', 
                {
                 'calendari': calendari,
                 'impartir_tot': impartir_tot, 
                 'professor': nomProfessor,
                 'percentatge': percentatgeProfessor,
                 'altres_moments': altres_moments,
                 } ,
                )




#------------------------------------------------------------------------------------------



#------------------------------------------------------------------------------------------

# http://streamhacker.com/2010/03/01/django-model-formsets/
@login_required
@group_required(['professors'])
def passaLlista(request, pk):
    credentials = getImpersonateUser(request)
    (user, l4) = credentials
    NoHaDeSerALAula = apps.get_model('presencia', 'NoHaDeSerALAula')

    # prefixes:
    # https://docs.djangoproject.com/en/dev/ref/forms/api/#prefixes-for-forms
    formset = []
    impartir = get_object_or_404(Impartir, pk=pk)

    # seg-------------------------------
    pertany_al_professor = user.pk in [impartir.horari.professor.pk, \
                                       impartir.professor_guardia.pk if impartir.professor_guardia else -1]
    if not (l4 or pertany_al_professor):
        raise Http404()

    head = ''
    info = {}
    info['old'] = unicode(impartir)
    info['professor'] = unicode(impartir.horari.professor)
    info['dia_setmana'] = unicode(impartir.horari.dia_de_la_setmana)
    info['dia_complet'] = impartir.dia_impartir.strftime("%d/%m/%Y")
    info['hora'] = unicode(impartir.horari.hora)
    info['assignatura'] = unicode(impartir.horari.assignatura)
    info['nom_aula'] = unicode(impartir.get_nom_aula)
    info['grup'] = unicode(impartir.horari.grup)

    ultimaReserva = ( ReservaAula
                     .objects.filter(dia_reserva = impartir.dia_impartir)
                     .filter(aula__nom_aula = impartir.get_nom_aula)
                     .filter(impartir__isnull = False)
                     .order_by('hora_fi')
                     .last()
                      )
    if ultimaReserva is not None:
        esUltimaHora = impartir.reserva_id == ultimaReserva.id
        if esUltimaHora:
            msg = u"ATENCIÓ: és l'última hora en aquesta aula. Recorda't de pujar les cadires, tancar finestres, baixar persianes i deixar l'aula ordenada."
            messages.error(request, SafeText(msg))

    url_next = '/presencia/mostraImpartir/%d/%d/%d/' % (
        impartir.dia_impartir.year,
        impartir.dia_impartir.month,
        impartir.dia_impartir.day)

    # ---------------------------------Passar llista -------------------------------
    if request.method == "POST":
        # un formulari per cada alumne de la llista
        totBe = True
        quelcomBe = False
        hiHaRetard = False
        form0 = forms.Form()
        formset.append(form0)
        for control_a in impartir.controlassistencia_set.order_by(*settings.CUSTOM_ORDER_PRESENCIA):  # .order_by( 'alumne__grup', 'alumne' )
            control_a.currentUser = user
            form = helper_tuneja_item_nohadeseralaula( request, control_a )

            control_a.professor = User2Professor(user)
            control_a.credentials = credentials

            if control_a.nohadeseralaula_set.exists():
                quelcomBe |= True
            elif form.is_valid():
                try:
                    control_aux = form.save()
                    hiHaRetard |= bool(control_aux.estat.codi_estat) and (control_aux.estat.codi_estat == "R")
                    quelcomBe |= True
                except (ProfeNoPot, ValidationError) as e:
                    totBe = False
                    # Com que no és un formulari de model cal tractar a mà les incidències del save:
                    form = helper_tuneja_item_nohadeseralaula(request, control_a,
                                                              te_error=True)
                    if form._errors is None:
                        form._errors = ErrorDict()                  #en alguns casos arriba sense _errors IDNW
                    for _, v in e.message_dict.items():
                        form._errors.setdefault(NON_FIELD_ERRORS, []).extend(v)

            else:
                totBe = False
                errors_formulari = form._errors
                # torno a posar el valor que hi havia ( per si el tutor l'ha justificat )
                form = helper_tuneja_item_nohadeseralaula(request,
                                                          control_a,
                                                          te_error=True)
                form._errors = errors_formulari

            formset.append(form)

        if quelcomBe:
            # algun control d'assistència s'ha desat. Desem també el model Impartir.
            impartir.dia_passa_llista = datetime.now()
            impartir.professor_passa_llista = User2Professor(request.user)
            impartir.currentUser = user

            try:
                impartir.save()

                # si hi ha retards, recordar que un retard provoca una incidència.
                if hiHaRetard and settings.CUSTOM_RETARD_PROVOCA_INCIDENCIA:
                    url_incidencies = reverse("aula__horari__posa_incidencia", kwargs={'pk': pk})
                    msg = u"""Has posat 'Retard', recorda que els retards provoquen incidències, 
                    s'hauran generat automàticament, valora si cal 
                    <a href="{url_incidencies}">gestionar les faltes</a>.""".format(url_incidencies=url_incidencies)
                    messages.warning(request, SafeText(msg))
                # LOGGING
                Accio.objects.create(
                    tipus='PL',
                    usuari=user,
                    l4=l4,
                    impersonated_from=request.user if request.user != user else None,
                    text=u"""Passar llista: {0}.""".format(impartir)
                )

                impartir_despres_de_passar_llista(impartir)
                if totBe:
                    return HttpResponseRedirect(url_next)
            except ValidationError as e:
                # Com que no és un formulari de model cal tractar a mà les incidències del save:
                for _, v in e.message_dict.items():
                    form0._errors.setdefault(NON_FIELD_ERRORS, []).extend(v)

    else:
        for control_a in impartir.controlassistencia_set.order_by(*settings.CUSTOM_ORDER_PRESENCIA):
            form = helper_tuneja_item_nohadeseralaula(request, control_a)
            formset.append(form)

    for form in formset:
        if hasattr(form, 'instance'):

            # 0 = present #1 = Falta
            d = dades_dissociades(form.instance)
            form.hora_anterior = (0 if d['assistenciaaHoraAnterior'] == 'Present' else
                                  1 if d['assistenciaaHoraAnterior'] == 'Absent' else
                                  2 if d['assistenciaaHoraAnterior'] == 'Online' else None)
            print (form.hora_anterior)
            prediccio, pct = predictTreeModel(d)
            form.prediccio = (0 if prediccio == 'Present' else
                              1 if prediccio == 'Absent' else  None)

            form.avis = None
            form.avis_pct = (u"{0:.2f}%".format(pct * 100)) if pct else ''
            if pct < 0.8:
                form.bcolor = '#CC0000'
                form.avis = 'danger'
            elif pct < 0.9:
                form.bcolor = '#CC9900'
                form.avis = 'warning'
            else:
                form.bcolor = '#66FFCC'
                form.avis = 'info'


    el_puc_justificar = lambda i: ( not settings.CUSTOM_NOMES_TUTOR_POT_JUSTIFICAR or
                                    User2Professor(user) in  i.alumne.tutorsDeLAlumne() )

    els_meus_tutorats = ",".join( unicode( i.pk )
                                  for i in impartir.controlassistencia_set.order_by()
                                  if el_puc_justificar(i)
                                  )

    return render(
        request,
        "passaLlista.html",
        {"formset": formset,
         "id_impartir": pk,
         "horariUrl": url_next,
         "pot_marcar_sense_alumnes": not impartir.pot_no_tenir_alumnes,
         "impartir": impartir,
         "head": head,
         "info": info,
         "feelLuckyEnabled": True,
         "permetCopiarDUnaAltreHoraEnabled": settings.CUSTOM_PERMET_COPIAR_DES_DUNA_ALTRE_HORA,
         "permetWinwheel": settings.CUSTOM_RULETA_ACTIVADA,         
         "els_meus_tutorats": els_meus_tutorats,
         "oneline": True,
         },
        )


def helper_tuneja_item_nohadeseralaula( request, control_a, te_error = False ):

    alumne = AlumneNomSentit.objects.get(pk=control_a.alumne.pk)

    NoHaDeSerALAula = apps.get_model('presencia', 'NoHaDeSerALAula')
    q_no_al_centre_expulsat = control_a.nohadeseralaula_set.filter(motiu=NoHaDeSerALAula.EXPULSAT_DEL_CENTRE)
    q_no_al_centre_sortida = control_a.nohadeseralaula_set.filter(motiu=NoHaDeSerALAula.SORTIDA)
    q_no_al_centre_altres = control_a.nohadeseralaula_set.exclude(motiu__in=[NoHaDeSerALAula.EXPULSAT_DEL_CENTRE,
                                                                             NoHaDeSerALAula.SORTIDA])
    if q_no_al_centre_expulsat.exists():
        form = ControlAssistenciaFormFake()
        form.fields['estat'].label_suffix = u""
        form.fields['estat'].label = (unicode(alumne)
                                      + u", ".join(
            [u"sanció del {0} al {1}".format(x.sancio.data_inici.strftime('%d/%m/%Y'),
                                             x.sancio.data_fi.strftime('%d/%m/%Y')
                                             )
             for x in q_no_al_centre_expulsat.all()]
        )
                                      )
    elif q_no_al_centre_sortida.exists():
        form = ControlAssistenciaFormFake()
        form.fields['estat'].label_suffix = u""
        form.fields['estat'].label = (unicode(alumne)
                                      + u" - Activitat: "
                                      + u", ".join([x.sortida.titol_de_la_sortida
                                                    for x in q_no_al_centre_sortida.all()]
                                                   )
                                      )

    elif q_no_al_centre_altres.exists():
        form = ControlAssistenciaFormFake()
        form.fields['estat'].label_suffix = u""
        form.fields['estat'].label = (unicode(alumne)
                                      + u" - ".join([x.get_motiu_display()
                                                    for x in q_no_al_centre_altres.all()]
                                                   )
                                      )

    else:
        if request.method == "POST" and not te_error:
            form = ControlAssistenciaForm(
                request.POST,
                prefix=str(control_a.pk),
                instance=control_a)
        elif request.method == "POST" and te_error:
            form = ControlAssistenciaForm(
                prefix=str(control_a.pk),
                instance=ControlAssistencia.objects.get(pk = control_a.pk))
        else:
            form = ControlAssistenciaForm(
                prefix=str(control_a.pk),
                instance=control_a)

        form.fields['estat'].label = unicode(alumne)
        avui_es_aniversari = alumne.aniversari(control_a.impartir.dia_impartir)

        missatge = ''
        if (settings.CUSTOM_MOSTRAR_MAJORS_EDAT and alumne.edat(control_a.impartir.dia_impartir)>=18):
            missatge=settings.CUSTOM_MARCA_MAJORS_EDAT

        form.fields['estat'].label = (unicode(alumne)
                                      + missatge +('(fa anys en aquesta data)' if avui_es_aniversari else '')
                                      )
    return form


#------------------------------------------------------------------------------------------

@login_required
@group_required(['direcció'])
def passaLlistaGrupDataTriaGrupDia(request):


    if request.method == "POST":
        frm = passaLlistaGrupDataForm( request.POST  )

        if frm.is_valid():
            return HttpResponseRedirect( '/presencia/passaLlistaGrupData/{0}/{1}/{2}/{3}/'.format(
                                                            frm.cleaned_data['grup'].pk,
                                                            frm.cleaned_data['dia'].day,                                      
                                                            frm.cleaned_data['dia'].month,                                      
                                                            frm.cleaned_data['dia'].year,                                      
                                                                                                  ) )
    else:
        frm = passaLlistaGrupDataForm(  )

    return render(
                request,
                  "form.html", 
                  {"form": frm,
                   "head": u"Passa llista a grup. Tria grup i data",
                   },
                )
    
    


@login_required
@group_required(['direcció'])
def passaLlistaGrupData(request, grup, dia, mes, year):
    
    credentials = getImpersonateUser(request) 
    (user, l4) = credentials
        
    data = date( year = int(year), month = int(mes), day = int(dia) )
    controls = ( ControlAssistencia.objects
                 .filter( alumne__grup = grup,  impartir__dia_impartir = data  )
                 .order_by( 'alumne', 'impartir__horari__hora__hora_inici' )
               )
    
    pendents = controls.filter(  estat__isnull = True )
    
    frmFact = modelformset_factory( 
                    ControlAssistencia, 
                    extra = 0, 
                    fields = ( 'estat', ) ,
                    #widgets={'estat': RadioSelect( attrs={'class':'presenciaEstat'} ), } 
                    )
    
    if request.method == "POST":
        formSet = frmFact( request.POST , queryset = controls  )
        
        for f in formSet.forms:
            f.instance.credentials = credentials
            
        if formSet.is_valid():
            formSet.save()
            return HttpResponseRedirect( '/' )
    else:
        formSet = frmFact( queryset = controls  )

    if bool(formSet.forms):
        f_prev = formSet.forms[0]
        for f in formSet:
            f.fields['estat'].widget = RadioSelect(
                                                choices = [x for x in f.fields['estat'].choices][1:],
                                                attrs={'class':'presenciaEstat'},                                                
                                                 )
            alumne = AlumneNomSentit.objects.get(pk = f.instance.alumne.pk)
            f.fields['estat'].label = u'{0} {1}'.format(  f.instance.alumne, f.instance.impartir.horari.hora )
            if f.instance.alumne != f_prev.instance.alumne:
                f_prev = f
                f.formSetDelimited = True

    return render(
                request,
                  "passaLlistaGrup.html", 
                  {"formset": formSet,
                   "head": u"Passa llista a grup",
                   'pendents': pendents,
                   },
            )


#---


@login_required
@group_required(['professors'])
def marcarComHoraSenseAlumnes(request, pk):
    credentials = getImpersonateUser(request) 
    (user, l4) = credentials   
    
    head=u'Afegir alumnes a la llista' 

    pk = int(pk)
    impartir = get_object_or_404(Impartir, pk=pk)
    
    #seg-------------------------------
    pertany_al_professor = user.pk in [ impartir.horari.professor.pk,   \
                                        impartir.professor_guardia.pk if impartir.professor_guardia else -1 ]
    if not ( l4 or pertany_al_professor):
        raise Http404() 

    
    if request.method == "POST":
        form = marcarComHoraSenseAlumnesForm( request.POST  )
        if form.is_valid() and form.cleaned_data['marcar_com_hora_sense_alumnes']:   
            expandir = form.cleaned_data['expandir_a_totes_les_meves_hores']
                          
            from aula.apps.presencia.afegeixTreuAlumnesLlista import marcaSenseAlumnesThread
            afegeix=marcaSenseAlumnesThread(expandir = expandir, impartir=impartir )
            afegeix.start()

            #LOGGING
            Accio.objects.create( 
                    tipus = 'LL',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Marcar classe sense alumnes {0}""".format(
                                impartir )                                                        
                        )
                
            import time
            while afegeix and not afegeix.primerDiaFet(): time.sleep(  0.5 )

            url_next = '/presencia/mostraImpartir/%d/%d/%d/'% ( 
                                    impartir.dia_impartir.year,
                                    impartir.dia_impartir.month,
                                    impartir.dia_impartir.day )    
                            
            return HttpResponseRedirect(url_next )
    else:
        form = marcarComHoraSenseAlumnesForm( initial= { 'marcar_com_hora_sense_alumnes': True, }  )

    return render(
                request,
                  "form.html", 
                  {"form": form,
                   "head": head,
                   },
                )
        

@login_required
@group_required(['professors'])
def afegeixAlumnesLlista(request, pk):
    credentials = getImpersonateUser(request) 
    (user, l4) = credentials   
    
    head=u'Afegir alumnes a la llista' 

    pk = int(pk)
    impartir = get_object_or_404(Impartir, pk=pk)
    
    #seg-------------------------------
    pertany_al_professor = user.pk in [ impartir.horari.professor.pk,   \
                                        impartir.professor_guardia.pk if impartir.professor_guardia else -1 ]
    if not ( l4 or pertany_al_professor):
        raise Http404() 
        
    alumnes_pk = [ ca.alumne.pk for ca in impartir.controlassistencia_set.all()]
    #http://www.ibm.com/developerworks/opensource/library/os-django-models/index.html?S_TACT=105AGX44&S_CMP=EDU

    #un formulari per cada grup
    grups_a_mostrar = grupsPotencials(impartir.horari)

    formset = []
    if request.method == "POST":
        
        expandir = False
        alumnes = []
        
        totBe = True
        
        #
        #primer form: expandir
        #
        formExpandir=afegeixAlumnesLlistaExpandirForm( request.POST, prefix='tots')    
        formset.append( formExpandir )    
        if formExpandir.is_valid():
            expandir = formExpandir.cleaned_data['expandir_a_totes_les_meves_hores']
            matmulla = formExpandir.cleaned_data['matmulla']
        else:
            totBe = False        
        #
        #altres forms: grups d'alumnes        
        #
        for grup in grups_a_mostrar:
            queryset=AlumneNomSentit.objects.filter(grup=grup).exclude(pk__in=alumnes_pk )
            form=afegeixTreuAlumnesLlistaForm(
                                    request.POST,
                                    prefix=str( grup.pk ),
                                    queryset=queryset,       
                                    etiqueta=unicode(grup)                             
                                     )
            formset.append( form )
            if form.is_valid():                
                alumnes += form.cleaned_data['alumnes']
            else:
                totBe = False

        #TODO: afegir error a mà

        
        if totBe:
            from aula.apps.presencia.afegeixTreuAlumnesLlista import afegeixThread
            afegeix=afegeixThread(expandir = expandir, alumnes=alumnes, impartir=impartir, usuari = user, matmulla = matmulla)
            executaAmbOSenseThread(afegeix)

            #LOGGING
            Accio.objects.create( 
                    tipus = 'LL',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Posar alumnes de la classe {0} (Forçat:{1}, Expandir:{2}): {3}""".format(
                                impartir,                                                                         
                                u'Sí' if matmulla else 'No', 
                                u'Sí' if expandir else 'No', 
                                u', '.join( [ unicode(a) for a in alumnes  ] )                                                        
                                  )
                )
                        
            #espero a que estigui fet el primer dia: abans de mostrar la pantalla de passar llista
            import time
            while afegeix and not afegeix.primerDiaFet(): time.sleep(  0.5 )
            
            return HttpResponseRedirect('/presencia/passaLlista/%s/'% pk )

    else:
        
        #primer form: expandir
        formExpandir=afegeixAlumnesLlistaExpandirForm( 
                                            prefix='tots', 
                                            initial={'expandir_a_totes_les_meves_hores':False})
        formset.append( formExpandir )

        #altres forms: grups d'alumnes        
        for grup in grups_a_mostrar:
            queryset=AlumneNomSentit.objects.filter(grup=grup).exclude(pk__in=alumnes_pk )
            form=afegeixTreuAlumnesLlistaForm(
                                    prefix=str( grup.pk ),
                                    queryset =queryset,     
                                    etiqueta = unicode( grup )                             
                                     )
            formset.append( form )
        
    return render(
                request,
                  "AfegirAlumnes.html", 
                  {"formset": formset,
                   "head": head,
                   },
                )

#------------------------------------------------------------------------------------------


@login_required
@group_required(['professors'])
def treuAlumnesLlista(request, pk):
    credentials = getImpersonateUser(request) 
    (user, l4) = credentials   
    
    head=u'Treure alumnes de la llista' 

    pk = int(pk)
    impartir = get_object_or_404(Impartir, pk=pk)
    
    #seg-------------------------------
    pertany_al_professor = user.pk in [ impartir.horari.professor.pk,   \
                                       impartir.professor_guardia.pk if impartir.professor_guardia else -1]
    if not ( l4 or pertany_al_professor):
        raise Http404() 
    

    formset = []
    alumnes = []
    if request.method == "POST":
        
        expandir = False
        
        #
        #primer form: expandir
        #
        formExpandir=afegeixAlumnesLlistaExpandirForm( request.POST, prefix='tots')  
        formExpandir.fields["matmulla"].help_text = u'''Marca aquesta opció per treure alumnes tot i que hagi passat llista (només els absents)'''
        formExpandir.fields["matmulla"].label = u'Força treure'      

        
        #
        #altres forms: grups d'alumnes        
        #
        queryset=AlumneNomSentit.objects.filter(pk__in = [ ca.alumne.pk for ca in impartir.controlassistencia_set.all()])
        form=afegeixTreuAlumnesLlistaForm(
                                request.POST,
                                prefix=str( 'alumnes' ),
                                queryset=queryset,       
                                etiqueta='Alumnes a treure:'                             
                                 )

        if form.is_valid() and formExpandir.is_valid():
            alumnes += form.cleaned_data['alumnes']
            expandir = formExpandir.cleaned_data['expandir_a_totes_les_meves_hores']
            matmulla = formExpandir.cleaned_data['matmulla']            
        
            from aula.apps.presencia.afegeixTreuAlumnesLlista import treuThread
            treu=treuThread(expandir = expandir, alumnes=alumnes, impartir=impartir, matmulla=matmulla,usuari=user)
            executaAmbOSenseThread(treu)

            #LOGGING
            Accio.objects.create( 
                    tipus = 'LL',
                    usuari = user,
                    l4 = l4,
                    impersonated_from = request.user if request.user != user else None,
                    text = u"""Treure alumnes de la classe {0} (Forçat:{1}, Expandir:{2}): {3}""".format(
                                impartir,                                                                         
                                u'Sí' if matmulla else 'No', 
                                u'Sí' if expandir else 'No', 
                                u', '.join( [ unicode(a) for a in alumnes  ] )                                                        
                                  )
                )
                        
            #espero que estigui fet el primer dia abans de mostrar la pantalla de passar llista
            import time
            while treu and not treu.primerDiaFet(): time.sleep(  0.5 )
            
            #afegeix.join()      #todo: missatge i redirecció!!!  
            #(' procés d'insertar alumnes engegat, pot trigar una estona. si no apareixen els alumnes prem el butó 'refrescar' del navegador' 
            #'/presencia/passaLlista/%s/' )
            
            return HttpResponseRedirect('/presencia/passaLlista/%s/'% pk )
        
    else:
        
        #primer form: expandir
        formExpandir=afegeixAlumnesLlistaExpandirForm( 
                                            prefix='tots', 
                                            initial={'expandir_a_totes_les_meves_hores':False})
        formExpandir.fields["matmulla"].help_text = u'''Marca aquesta opció per treure alumnes tot i que hagi passat llista (només els absents)'''
        formExpandir.fields["matmulla"].label = u'Força treure'      

        formset.append( formExpandir )

        #altres forms: grups d'alumnes   
        queryset = AlumneNomSentit.objects.filter( pk__in = [ ca.alumne.pk for ca in impartir.controlassistencia_set.all()  ] )        
        form = afegeixTreuAlumnesLlistaForm(
                                prefix=str( 'alumnes' ),
                                queryset=queryset,
                                etiqueta='Alumnes a treure:'                               
                                 )
        formset.append( form )
        
    return render(
                request,
                  "AfegirAlumnes.html", 
                  {"formset": formset,
                   "head": head,
                   "missatge":u"""Atenció, no s'esborraran els alumnes que ja s'hagi passat llista o els que tinguin
                                   alguna incidència o expulsió""",
                   },
                )


@login_required
@group_required(['professors'])
def afegeixGuardia(request, dia=None, mes=None, year=None):
    
    credentials = getImpersonateUser(request) 
    (user, _ ) = credentials
        
    head=u'Fer guardia' 

    url_next = '/presencia/mostraImpartir/%d/%d/%d/'% ( 
                                    int(year),
                                    int(mes),
                                    int(dia ) )    
    if request.method == 'POST':
        form = afegeixGuardiaForm(request.POST)
        
        if form.is_valid():
            
            professor = form.cleaned_data['professor']
            franges = form.cleaned_data['franges']
            dia_impartir = date( int(year), int(mes), int(dia)  )
            professor_guardia = User2Professor( user )
            Impartir.objects.filter( dia_impartir = dia_impartir,
                                     horari__professor = professor,
                                     horari__hora__in = franges 
                                    ).update( professor_guardia = professor_guardia  )

            return HttpResponseRedirect( url_next )
                                    
                             
    else:
        form = afegeixGuardiaForm()
    return render(
                request,
                'form.html', 
                {'form': form, 
                 'head': head},
                )

    
@login_required
@group_required(['professors'])
def esborraGuardia(request, pk):
    credentials = getImpersonateUser(request) 
    (user, l4) = credentials
    
    impartir = get_object_or_404( Impartir, pk = pk )

    url_next = '/presencia/mostraImpartir/%d/%d/%d/'% (                                     
                                    impartir.dia_impartir.year,
                                    impartir.dia_impartir.month,
                                    impartir.dia_impartir.day )
    
    #seg-------------------------------
    pertany_al_professor = ( impartir.professor_guardia is not None) and (  user.pk == impartir.professor_guardia.pk )
    if not ( l4 or pertany_al_professor):
        return HttpResponseRedirect( url_next )
    
    if impartir.professor_guardia == User2Professor(user):    
        impartir.professor_guardia = None
        impartir.currentUser = user
        impartir.save()

    return HttpResponseRedirect( url_next )


@login_required
@group_required(['professors'])
def calculadoraUnitatsFormatives(request):    

    credentials = getImpersonateUser(request) 
    (user, _ ) = credentials

    professor = User2Professor( user ) 
        
    head=u'Calculadora Unitats Formatives'
    infoForm = []
    
    grupsProfessor = Grup.objects.filter( horari__professor = professor  ).order_by('curs').distinct()
    assignaturesProfessor = Assignatura.objects.filter( 
                                        horari__professor = professor, 
                                        horari__grup__isnull = False ).order_by('curs','nom_assignatura').distinct()

    if request.method == 'POST':
        form = calculadoraUnitatsFormativesForm( request.POST, assignatures = assignaturesProfessor, grups = grupsProfessor )
        
        if form.is_valid():            
            grup = form.cleaned_data['grup']
            assignatures = form.cleaned_data['assignatura']
            dataInici = form.cleaned_data['dataInici']
            hores = form.cleaned_data['hores']
            imparticionsAssignatura = Impartir.objects.filter( dia_impartir__gte = dataInici,
                                                               horari__assignatura__in = assignatures,
                                                               horari__grup = grup,
                                                               horari__professor = professor  
                                                               ).order_by( 'dia_impartir', 'horari__hora'  )
            if imparticionsAssignatura.count() < hores:
                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  
                           [ u'''A partir de la data {0} només hi ha {1} hores,
                                   comprova que has triat bé el curs.
                                   '''.format( 
                                                dataInici,
                                                imparticionsAssignatura.count()
                                                ) ] )
            else:
                try:
                    darreraImparticio = imparticionsAssignatura[hores-1]
                    infoForm = [ ('Darrera classe', u'dia {0} a les {1}'.format( darreraImparticio.dia_impartir, darreraImparticio.horari.hora.hora_inici )), ]
                except Exception as e:
                    form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  [e]  )  
            
                
                             
    else:
        form = calculadoraUnitatsFormativesForm( assignatures = assignaturesProfessor , grups = grupsProfessor)
    return render(
                request,
                'form.html', 
                {'form': form, 
                 'infoForm': infoForm,
                 'head': head},
                )
    

#------------------------------------------------------------------------------------------

@login_required
@group_required(['direcció'])
def alertaAssistencia(request):
    credentials = getImpersonateUser(request) 
    (user, l4) = credentials   
    
    head=u'''Alerta alumnes''' 
    
    if request.method == 'POST':
        form = alertaAssistenciaForm(request.POST)
        if form.is_valid():
            report = alertaAssitenciaReport( 
                            data_inici = form.cleaned_data['data_inici'],
                            data_fi = form.cleaned_data['data_fi'],
                            nivell = form.cleaned_data['nivell'],                                         
                            tpc = form.cleaned_data['tpc']  ,
                            ordenacio = form.cleaned_data['ordenacio']  ,                      
                                             )
            
            return render(
                        request,
                        'report.html',
                            {'report': report,
                             'head': 'Informació alumnes' ,
                            },
                        )
 
    else:
        form = alertaAssistenciaForm()
        
    return render(
            request,
            'alertaAbsentisme.html', 
            {'head': head ,
             'form': form },
            )

#amorilla@xtec.cat 
@login_required
@group_required(['direcció','administradors'])
def indicadors(request):
    (report, dades) = indicadorsReport()
    if dades is None:
        menuCTX=False
    else:
        menuCTX=list({"/presencia/indcsv": "Baixa dades csv"}.items())
    return render(
            request,
            'report.html',
                {'report': report,
                 'head': 'Indicadors' ,
                 'menuCTX':menuCTX
                },
            )

#amorilla@xtec.cat 
@login_required
@group_required(['direcció','administradors'])
def indcsv(request):

    (_, dades) = indicadorsReport()
    return dades

@login_required
@group_required(['professors'])
def faltesAssistenciaEntreDates(request):    

    credentials = getImpersonateUser(request) 
    (user, _ ) = credentials

    professor = User2Professor( user ) 
        
    head=u'Calculadora %assistència entre Dates'
    infoForm = []
    
    grupsProfessor = Grup.objects.filter( horari__professor = professor  ).order_by('curs').distinct()
    assignaturesProfessor = Assignatura.objects.filter( 
                                        horari__professor = professor, 
                                        horari__grup__isnull = False ).order_by('curs','nom_assignatura').distinct()

    if request.method == 'POST':
        form = faltesAssistenciaEntreDatesForm( request.POST, assignatures = assignaturesProfessor, grups = grupsProfessor )
        
        if form.is_valid():            

            report = faltesAssistenciaEntreDatesProfessorRpt( 
                professor = professor,
                grup = form.cleaned_data['grup'],
                assignatures = form.cleaned_data['assignatura'],
                dataDesDe = form.cleaned_data['dataDesDe'],
                horaDesDe = form.cleaned_data['horaDesDe'],
                dataFinsA = form.cleaned_data['dataFinsA'],
                horaFinsA = form.cleaned_data['horaFinsA']                                       
                                         )                
            return render(
                    request,
                    'reportTabs.html',
                        {'report': report,
                         'head': 'Informació alumnes' ,
                        },
                    )
#            except Exception as e:
#                form._errors.setdefault(NON_FIELD_ERRORS, []).extend(  [e]  )  
            
                
                             
    else:
        form = faltesAssistenciaEntreDatesForm( assignatures = assignaturesProfessor , grups = grupsProfessor)
    return render(
                request,
                'form.html', 
                {'form': form, 
                 #'infoForm': [],
                 'head': head},
                )
    

# -----------------------------------------------------------------------------

@login_required
@group_required(['professors'])
def copiarAlumnesLlista(request, pk):
    credentials = getImpersonateUser(request) 
    (user, l4) = credentials   
    
    head=u'Copiar alumnes a la llista a partir d\'una altra hora' 

    pk = int(pk)
    impartir = get_object_or_404(Impartir, pk=pk)
    
    #seg-------------------------------
    pertany_al_professor = user.pk in [ impartir.horari.professor.pk,   \
                                        impartir.professor_guardia.pk if impartir.professor_guardia else -1 ]
    if not ( l4 or pertany_al_professor):
        raise Http404() 

    formset = []    

    formHores = None

    import datetime as t

    dataRef = date.today()
    dillunsSetmana = dataRef + t.timedelta(days=-dataRef.weekday())
    #4 és el divendres 0,1,2,3,4 (5é dia)
    divendresSetmana = dataRef + t.timedelta(days=4-dataRef.weekday())
    dInici = date(year=dillunsSetmana.year, month=dillunsSetmana.month, day=dillunsSetmana.day)
    dFi = date(year=divendresSetmana.year, month=divendresSetmana.month, day=divendresSetmana.day)

    horarisProfe = Impartir.objects \
                    .filter(dia_impartir__gte=dInici) \
                    .filter(dia_impartir__lte=dFi) \
                    .filter(horari__professor=user.pk) \
                    .order_by('horari')
    opcions = []
    for eH in horarisProfe:
        assistencies = ControlAssistencia.objects.filter(impartir__id=eH.id)
        opcions.append((eH.id, 
            unicode(eH.horari.assignatura) + " " + unicode(eH.horari.dia_de_la_setmana) + " " + unicode(eH.horari.hora) + 
            u'--> Alumnes: ' + unicode(len(assistencies)) + ''))

    if request.method == "POST":
        formHores = llistaLesMevesHoresForm(request.POST, llistaHoresProfe=opcions)
        if formHores.is_valid():
            #Inicio el procés de copia.
            #No deixar copiar si és la mateixa hora.
            eliminarAlumnes = formHores.cleaned_data['eliminarAlumnes']
            idHoraOrigen = formHores.cleaned_data['hores']
            idHoraDesti = pk
            horaDesti = Impartir.objects.get(id=idHoraDesti)

            if int(idHoraOrigen) == int(idHoraDesti):
                formHores._errors.setdefault(NON_FIELD_ERRORS, []).extend(
                    [ u'''No pots copiar alumnes sobre la mateixa hora.'''])
            else:
                
                #Obtenir llista d'alumnes de destí per veure solapaments.
                alumnesDesti = {}
                assistenciesDesti = ControlAssistencia.objects.filter(impartir__id=idHoraDesti)
                for ca in assistenciesDesti:
                    alumnesDesti[ca.alumne.id] = ca.alumne

                assistenciesOrigen = ControlAssistencia.objects.filter(impartir__id=idHoraOrigen)
                alumnesAAfegir = []
                for ca in assistenciesOrigen:
                    #Gravar la llista d'alumnes al destí.
                    if eliminarAlumnes:
                        #Copiem tots els alumnes perque els esborrarem tots abans.
                        alumnesAAfegir.append(ca.alumne)
                    else:
                        #Copiem només els alumnes que ens interessen.
                        if ca.alumne.id not in alumnesDesti:
                            alumnesAAfegir.append(ca.alumne)

                

   
                from aula.apps.presencia.afegeixTreuAlumnesLlista import afegeixThread, treuThread
                #Eliminem alumnes abans de copiar.
                if eliminarAlumnes:
                    treu = treuThread(expandir=None, alumnes=list(alumnesDesti.values()), impartir=horaDesti, matmulla = False
                                      ,usuari=user)
                    treu.usuari = user
                    treu.start()

                    #Espera el final de l'eliminació.
                    treu.join()

                    #LOGGING
                    Accio.objects.create( 
                            tipus = 'LL',
                            usuari = user,
                            l4 = l4,
                            impersonated_from = request.user if request.user != user else None,
                            text = u"""Copiar alumnes, eliminar alumnes de {0}: {1}""".format(
                                        horaDesti, 
                                        u', '.join( [ unicode(a) for a in alumnesDesti ])))


                #Llança el thread que expandirà a la resta del curs.
                afegeix=afegeixThread(expandir=None, alumnes=alumnesAAfegir, impartir=horaDesti, usuari=user, matmulla=False)
                afegeix.start()

                #LOGGING
                Accio.objects.create( 
                        tipus = 'LL',
                        usuari = user,
                        l4 = l4,
                        impersonated_from = request.user if request.user != user else None,
                        text = u"""Copiar alumnes de {0} a {1}: {2}""".format(
                                    impartir,                                                                         
                                    horaDesti, 
                                    u', '.join( [ unicode(a) for a in alumnesAAfegir ])))
                            
                #espero a que estigui fet el primer dia: abans de mostrar la pantalla de passar llista
                import time
                while afegeix and not afegeix.primerDiaFet(): time.sleep(  0.5 )
                return HttpResponseRedirect('/presencia/passaLlista/%s/'% pk )
    else:
        formHores = llistaLesMevesHoresForm(llistaHoresProfe=opcions)

    formset.append(formHores)
    
    return render(
                request,
                  "formset.html", 
                  {"formset": formset,
                   "head": head,
                   },
                )

    
#------------------------------------------------------------------------------------------

@login_required
@group_required(['direcció'])
def anularImpartir(request, pk):
    impartir = get_object_or_404(Impartir, pk=pk)
    controls = impartir.controlassistencia_set
    credentials = getImpersonateUser(request)
    (user, l4) = credentials

    NoHaDeSerALAula = apps.get_model('presencia', 'NoHaDeSerALAula')
    if not controls.exists():
        messages.error(request, u"Aquesta classe no té alumnes, no es pot anul·lar." )
        next_url = reverse( "aula__horari__passa_llista", kwargs={'pk': pk} )
    else:
        errors = []
        q_already_anulats = Q(nohadeseralaula__motiu = NoHaDeSerALAula.ANULLADA )
        q_sense_passar_llista = Q(estat = None)
        q_falta = Q(estat__codi_estat = "F")
        for control in controls.exclude(q_already_anulats).filter(q_sense_passar_llista|q_falta).all():
            control.nohadeseralaula_set.create(motiu=NoHaDeSerALAula.ANULLADA)
            control.estat_backup = control.estat
            control.professor_backup = control.professor
            control.swaped = True
            control.estat = None
            try:
                control.save()
            except (ProfeNoPot, ValidationError) as e:
                for _, v in e.message_dict.items():
                    errors.append(v)

        #marco com impartida:
        if user.groups.filter(name="professors").exists():
            try:
                impartir.professor_passa_llista = User2Professor( user )
                impartir.dia_passa_llista =  datetime.now()
                impartir.save()
            except ValidationError as e:
                for _, v in e.message_dict.items():
                    errors.append(v)

        if not bool(errors):
            messages.success(request, u"""Operació finalitzada. 
            S'han marcat tots els controls d'assistència d'aquesta classe com anul·lats. 
            Si el professor posa nous alumnes a la classe caldria repetir el procés. """)
        else:
            messages.error(request,u"S'han trobat errors anul·lant aquesta hora de classe: {}". format (u", ".join(errors)) )

        next_url = reverse("aula__horari__passa_llista", kwargs={'pk': pk})
    return HttpResponseRedirect(next_url)

@login_required
@group_required(['direcció'])
def desanularImpartir(request, pk):
    impartir = get_object_or_404(Impartir, pk=pk)
    controls = impartir.controlassistencia_set
    NoHaDeSerALAula = apps.get_model('presencia', 'NoHaDeSerALAula')
    if not controls.exists():
        messages.error(request, u"Aquesta classe no té alumnes, vols dir que és aquesta la que vols des-anul·lar?" )
        next_url = reverse( "aula__horari__passa_llista", kwargs={'pk': pk} )
    elif not NoHaDeSerALAula.objects.filter( control__impartir = impartir, motiu = NoHaDeSerALAula.ANULLADA ).exists():
        messages.error(request, u"Aquesta classe no està anul·lada, vols dir que és aquesta la classe que vols des-anul·lar?")
        next_url = reverse("aula__horari__passa_llista", kwargs={'pk': pk})
    else:
        errors = []
        q_already_anulats = Q(nohadeseralaula__motiu=NoHaDeSerALAula.ANULLADA)
        for control in controls.filter(q_already_anulats).all():
            control.nohadeseralaula_set.filter(motiu=NoHaDeSerALAula.ANULLADA).delete()
            if control.swaped:
                control.estat = control.estat_backup
                control.professor = control.professor_backup
                control.swaped = False
            try:
                control.save()
            except (ProfeNoPot, ValidationError) as e:
                for _, v in e.message_dict.items():
                    errors.append(v)

        # si tot a null, desmarcar d'impartida:
        if all(c.estat_id is None for c in controls.all()):
            try:
                impartir.professor_passa_llista = None
                impartir.dia_passa_llista = None
                impartir.save()
            except ValidationError as e:
                for _, v in e.message_dict.items():
                    errors.append(v)

        if not bool(errors):
            messages.success(request, u"Operació finalitzada. Classe des-anul·lada.")
        else:
            messages.error(request,
                           u"S'han trobat errors des-anul·lant aquesta hora de classe: {}".format(u", ".join(errors)))
        next_url = reverse("aula__horari__passa_llista", kwargs={'pk': pk})
    return HttpResponseRedirect(next_url)

# ------------
@login_required
@group_required(['professors'])
def winwheel(request, pk):

    """
    Aquesta pàgina mostra un ruleta i serveix per triar un alumne a l'atzar.

    La documentació de la ruleta la trobem a: https://github.com/zarocknz/javascript-winwheel
    """

    passa_llista_url = reverse("aula__horari__passa_llista", kwargs={'pk': pk})
    winwheel_url = reverse("aula__horari__winwheel", kwargs={'pk': pk})

    if not settings.CUSTOM_RULETA_ACTIVADA:        
        return HttpResponseRedirect(passa_llista_url)

    credentials = getImpersonateUser(request)
    (user, l4) = credentials
    impartir = get_object_or_404( Impartir, pk = pk)

    ControlAssistencia

    # es_present? Servirà per triar el color. Si sabem que falta el pintem en gris.
    es_present = lambda c: c is None or c.estat is None or c.estat.codi_estat != 'F'

    alumnes_i_presencialitat = [
        (c.alumne, es_present(c) )
        for c in impartir.controlassistencia_set.all()
        if (
            not c.alumne.esBaixa() and
            not c.nohadeseralaula_set.exists()
        )
    ]

    # nom_i_inicials: No hi ha gaire espai a la ruleta, pintem 'Laia B.C.'
    nom_i_inicials = lambda a: (a.nom_sentit or a.nom ) + " " + ".".join([ x[:1] for x in a.cognoms.split(" ")]) + "."

    noms_i_presencialitat = [
        (nom_i_inicials(alumne), presencialitat)
        for alumne, presencialitat in alumnes_i_presencialitat
    ]

    hi_ha_prous_alumnes = len(noms_i_presencialitat) > 1

    random.shuffle(noms_i_presencialitat)

    guanyador_no_ui = noms_i_presencialitat[0][0] if hi_ha_prous_alumnes else None

    colors = ['#eae56f', '#89f26e', '#7de6ef', '#e7706f', ]
    color_falta = ['#aaaaaa'] # color amb el que pintem els alumnes que falten

    # tria_color: Va alternant colors, pinta gris si no hi és a l'aula
    tria_color = lambda idx, present: color_falta if not present else colors[idx%4]
    
    # items_ruleta: llista de diccionaris amb el color i el nom
    items_ruleta = [
        {
            'fillStyle' : tria_color(idx, nom_i_presencialitat[1]),
            'text' : nom_i_presencialitat[0]
        }
        for idx, nom_i_presencialitat in enumerate(noms_i_presencialitat)
    ]

    return render(
                request,
                  "presencia/winwheel.html", 
                  {
                      "n": len(items_ruleta),
                      "hi_ha_prous_alumnes": hi_ha_prous_alumnes,
                      "items_ruleta": items_ruleta,
                      "guanyador_no_ui": guanyador_no_ui,
                      "passa_llista_url": passa_llista_url,
                      "winwheel_url": winwheel_url,
                   },
                )    