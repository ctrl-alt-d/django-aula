# This Python file uses the following encoding: utf-8

#templates
from django.db.utils import IntegrityError
from django.template import RequestContext

#auth
from django.contrib.auth.decorators import login_required
from aula.utils.decorators import group_required

#workflow
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

#excepcions
#from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
#from django.http import Http404

#otherfrom alumnes.forms import grupfrom alumnes.forms import grup

from django.contrib import messages
from django.utils.safestring import SafeText

from django.forms.models import modelformset_factory, modelform_factory
from aula.apps.avaluacioQualitativa.models import ItemQualitativa, AvaluacioQualitativa, RespostaAvaluacioQualitativa
from aula.utils import tools
from aula.utils.tools import unicode
from aula.apps.usuaris.models import User2Professor
from aula.apps.assignatures.models import Assignatura
from aula.apps.alumnes.models import Grup, Alumne
from django.db.models import Q
from aula.apps.avaluacioQualitativa.forms import qualitativaItemsForm, alumnesGrupForm,\
    triaQualitativaForm
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from aula.apps.presencia.models import ControlAssistencia, Impartir


@login_required
@group_required(['direcció'])
def items( request ):

    head=u'Items Qualitativa' 
    
    formset_f = modelformset_factory(  ItemQualitativa, extra=20, exclude=[], )
    missatge = ''

    if request.method == 'POST':
        formset = formset_f(request.POST)
        if formset.is_valid():
            
            formset.save()
            missatge = u'''Actualització realitzada.'''
        else:
            missatge = u'''Actualització no realitzada.'''
                                   
    else:
        formset = formset_f()
    
    for form in formset:
        form.fields['text'].widget.attrs['size'] = 70
        
    return render(
                request,
                'formset.html', 
                {'formset': formset, 
                 'head': head,
                 "missatge": missatge,
                 'formSetDelimited':True},
                )
    
@login_required
@group_required(['direcció'])
def avaluacionsQualitatives( request ):

    head=u'Avaluacions qualitatives' 
    
    formset_f = modelformset_factory(  AvaluacioQualitativa, extra=5, exclude=() )
    missatge = ''

    if request.method == 'POST':
        formset = formset_f(request.POST)
        if formset.is_valid():
            
            formset.save()
            missatge = u'''Actualització realitzada.'''
        else:
            missatge = u'''Actualització no realitzada.'''
                                   
    else:
        formset = formset_f()

    for form in formset:
        form.fields['data_obrir_avaluacio'].widget.attrs['class'] = 'datepicker'
        form.fields['data_tancar_avaluacio'].widget.attrs['class'] = 'datepicker'
        
    return render(
                request,
                'formset.html', 
                {'formset': formset, 
                 'head': head,
                 "missatge": missatge,
                 'formSetDelimited':True},
                )
    

#---------------------  --------------------------------------------#

    
@login_required
@group_required(['professors'])
def lesMevesAvaluacionsQualitatives( request ):

    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor( user )     
    
    report = []
    
    

    for qualitativa in AvaluacioQualitativa.objects.all():
 
        taula = tools.classebuida()
        taula.titol = tools.classebuida()
        taula.titol.contingut = ""
        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 40
        capcelera.contingut = u'{0}'.format(unicode( qualitativa ) )
        taula.capceleres.append(capcelera)
        
        capcelera = tools.classebuida()
        capcelera.amplade = 60
        obertaLaQualitativa =  qualitativa.data_obrir_avaluacio <=  date.today() <= qualitativa.data_tancar_avaluacio
        estat = '(Oberta)' if obertaLaQualitativa else '(Tancada)'
        capcelera.contingut = u'del {0} al {1} {2}'.format( qualitativa.data_obrir_avaluacio, qualitativa.data_tancar_avaluacio, estat)
        taula.capceleres.append(capcelera)
        
        taula.fileres = []
    
        #Només pels que tenen items o respostes
        #teFrases = Q(  horari__grup__curs__nivell__itemqualitativa__isnull  = False )
        #teRespostes = Q( respostaavaluacioqualitativa__isnull = False )
        assignatura_grup = set()
        for ca in Impartir.objects.filter( horari__professor = professor, 
                                                     dia_impartir__gte = qualitativa.data_obrir_avaluacio ,
                                                     dia_impartir__lte = qualitativa.data_tancar_avaluacio ):
            if ca.horari.grup is not None: 
                assignatura_grup.add( (ca.horari.assignatura, ca.horari.grup )  )
                
        for (assignatura, grup,) in  assignatura_grup: 
            if qualitativa in grup.avaluacioqualitativa_set.all():
                
                teFrases = grup.curs.nivell.itemqualitativa_set.exists()
                
                aquestaQualitativa = Q( qualitativa = qualitativa ) and  \
                                    Q( professor = professor ) and \
                                    Q( alumne__grup = grup ) and \
                                    Q( assignatura = assignatura)
                teResostes = RespostaAvaluacioQualitativa.objects.filter( aquestaQualitativa).exists()
                
                if teFrases or teResostes:
                    
                    filera = []
                    
                    camp = tools.classebuida()
                    camp.contingut = u'{0} - {1}'.format(unicode( assignatura ) , unicode( grup ) )
                    filera.append(camp)
                    
                    q_mateix_grup = Q(controlassistencia__impartir__horari__grup = grup)
                    q_mateixa_assignatura = Q(controlassistencia__impartir__horari__assignatura = assignatura)
                    q_mateix_professor = Q(controlassistencia__impartir__horari__professor = professor)
                    q_liPassemLlistaDesDe = Q( controlassistencia__impartir__dia_impartir__gte = ( qualitativa.data_obrir_avaluacio - timedelta( days = 7 ) ) )
                    q_liPassemLlistaFinsA = Q( controlassistencia__impartir__dia_impartir__lte = qualitativa.data_tancar_avaluacio )
                    
                    q_alumnes_a_avaluar = q_mateix_grup & q_mateixa_assignatura & q_mateix_professor & q_liPassemLlistaDesDe & q_liPassemLlistaFinsA
                    
                    q_te_respostes = Q(respostaavaluacioqualitativa__isnull = False)
                    q_mateixa_qualitativa = Q(respostaavaluacioqualitativa__qualitativa = qualitativa)
                    q_mateix_professor_qualitativa = Q(respostaavaluacioqualitativa__professor = professor)
                    q_mateixa_assiganatura_qualitativa = Q(respostaavaluacioqualitativa__assignatura = assignatura)
                    
                    q_alumnes_avaluats = q_alumnes_a_avaluar & q_te_respostes & q_mateixa_qualitativa & q_mateix_professor_qualitativa & q_mateixa_assiganatura_qualitativa
                    
                    camp = tools.classebuida()                
                    nTotalAlumnes = Alumne.objects.filter( q_alumnes_a_avaluar ).distinct().count()
                    nAlumnesAvaluats = Alumne.objects.filter(q_alumnes_avaluats ).distinct().count() if nTotalAlumnes > 0 else 0
                    camp.contingut = u'{0}'.format(u'{0} / {1}'.format(nAlumnesAvaluats,nTotalAlumnes)  )  
                    if nTotalAlumnes > 0:
                        camp.enllac = '/avaluacioQualitativa/entraQualitativa/{0}/{1}/{2}'.format( qualitativa.pk, assignatura.pk, grup.pk )
                    filera.append( camp )
                    
                    taula.fileres.append( filera )
                
                
        report.append(taula)
        
    return render(
                request,
                'report.html',
                    {'report': report,
                     'head': u'Avaluacions Qualitatives' ,
                    },
                )


    
    
@login_required
@group_required(['professors'])
def entraQualitativa( request, qualitativa_pk, assignatura_pk, grup_pk  ):
    #FormSet: Una opció seria fer servir formSet, però em sembla que
    #com ho estic fent ara és més fàcil per l'usuari
    #https://docs.djangoproject.com/en/dev/topics/forms/formsets
    
    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor( user )

    missatge = ''
    tipusForm = "formset.html"
    errors = set()
        
    qualitativa_pk = int(qualitativa_pk)
    qualitativa = get_object_or_404( AvaluacioQualitativa, pk = qualitativa_pk )
    
    assignatura_pk = int( assignatura_pk)
    assignatura = get_object_or_404( Assignatura, pk = assignatura_pk )

    hi_ha_tipus_assignatura = (assignatura.tipus_assignatura is not None
                               and assignatura.tipus_assignatura.capcelera
                               )
    assignatura_label = assignatura.tipus_assignatura.capcelera if hi_ha_tipus_assignatura else u"Matèria"

    grup_pk = int( grup_pk )
    grup = get_object_or_404( Grup, pk = grup_pk )
    
    itemsQualitativa = ItemQualitativa.objects.filter( nivells__in = [ grup.curs.nivell ] )
    
    aquestaQualitativa = Q( qualitativa__pk = qualitativa_pk ) and  Q( professor = professor ) and Q( assignatura = assignatura)
    
    
#    alumneAlta = Q( data_alta__lte = qualitativa.data_tancar_avaluacio ) & (
#                            Q(data_baixa__isnull = True) |
#                            Q(data_baixa__gte = qualitativa.data_tancar_avaluacio )  
#                                                        )
#    alumnes = Alumne.objects.filter( 
#                controlassistencia__impartir__horari__grup__pk = grup_pk,
#                controlassistencia__impartir__horari__assignatura__pk = assignatura_pk, 
#                controlassistencia__impartir__horari__professor = professor,
#                controlassistencia__impartir__dia_impartir__gte = ( qualitativa.data_obrir_avaluacio - timedelta( days = 7 ) ),
#                controlassistencia__impartir__dia_impartir__lte = qualitativa.data_tancar_avaluacio
#                                ).filter(alumneAlta).distinct().order_by('cognoms')
    
    q_mateix_grup = Q(controlassistencia__impartir__horari__grup = grup)
    q_mateixa_assignatura = Q(controlassistencia__impartir__horari__assignatura = assignatura)
    q_mateix_professor = Q(controlassistencia__impartir__horari__professor = professor)
    q_liPassemLlistaDesDe = Q( controlassistencia__impartir__dia_impartir__gte = ( qualitativa.data_obrir_avaluacio - timedelta( days = 7 ) ) )
    q_liPassemLlistaFinsA = Q( controlassistencia__impartir__dia_impartir__lte = qualitativa.data_tancar_avaluacio )
    
    q_alumnes_a_avaluar = q_mateix_grup & q_mateixa_assignatura & q_mateix_professor & q_liPassemLlistaDesDe & q_liPassemLlistaFinsA
    
    alumnes = Alumne.objects.filter( q_alumnes_a_avaluar ).distinct().order_by('cognoms')


    obertaLaQualitativa =  qualitativa.data_obrir_avaluacio <=  date.today() <= qualitativa.data_tancar_avaluacio
            
    formset = []
    if request.method == "POST":
        #un formulari per cada grup
        totBe = True
        formF=modelform_factory( Assignatura, fields=[ 'nom_assignatura' ]  )
    
        form = formF( request.POST, instance = assignatura , prefix = str( assignatura.pk ) )

        form.fields['nom_assignatura'].label = assignatura_label

        if form.is_valid():
            assignatura=form.save(commit=False)
            if not bool(assignatura.nom_assignatura):
                errors.add( u"Cal posar un nom a l'assignatura." )
                totBe = False
            else:             
                assignatura=form.save()
        else:
            errors.add( u"Error canviant el nom de l'assignatura." )
            totBe = False
        
        for alumne in alumnes:
            form=qualitativaItemsForm(
                                    request.POST,
                                    prefix=str( alumne.pk ),
                                    itemsQualitativa = itemsQualitativa
                            )
            if form.is_valid():
                try:
                    #--- TODO: Begin TX ----------------------------------------------------------------
                    for resposta in RespostaAvaluacioQualitativa.objects.filter( alumne = alumne).filter( aquestaQualitativa ):
                        resposta.credentials = (user, l4)
                        resposta.delete()
                    respostes = set()
                    if form.cleaned_data['q1']: respostes.add(form.cleaned_data['q1'])
                    if form.cleaned_data['q2']: respostes.add(form.cleaned_data['q2'])
                    if form.cleaned_data['q3']: respostes.add(form.cleaned_data['q3'])
                    #if form.cleaned_data['q4']: respostes.add(form.cleaned_data['q4'])
                    for resposta in respostes:
                        try:
                            novaResposta = RespostaAvaluacioQualitativa()
                            novaResposta.alumne = alumne
                            novaResposta.item = resposta
                            novaResposta.professor = professor
                            novaResposta.qualitativa = qualitativa
                            novaResposta.assignatura = assignatura
                            novaResposta.credentials = (user, l4)
                            novaResposta.save()
                        except IntegrityError as e:
                            errors.add(u"Hi ha hagut un error assignant qualitativa a {alumne}. Comprova-ho.".format(alumne))

                    if form.cleaned_data['qo']: 
                        novaResposta = RespostaAvaluacioQualitativa()
                        novaResposta.alumne = alumne
                        novaResposta.frase_oberta = form.cleaned_data['qo']
                        novaResposta.professor = professor
                        novaResposta.qualitativa = qualitativa
                        novaResposta.assignatura = assignatura 
                        novaResposta.credentials = (user, l4)
                        novaResposta.save()
                #---Fi TX---------------------------------------------------------------
                except ValidationError as e:
                    for _, v in e.message_dict.items():
                        for x in v: errors.add( x )
                    totBe = False
                    
            else:
                totBe = False
                for _ , error in form.__errors.items():
                    errors.add(error)
                
            if totBe:
                missatge = u'Dades actualitzades correctament'                
            else:
                missatge = u'Hi ha hagut errors actualitzant les dades'
    
        for missatge in errors:
            messages.error(request,  missatge )
        if not bool(errors):
            messages.success(request, u"Dades actualitzades correctament")
        if totBe:
            #redirect
            url_next = r"/avaluacioQualitativa/entraQualitativa/{}/{}/{}/".format( qualitativa_pk, assignatura_pk, grup_pk  )
            return HttpResponseRedirect( url_next )
    
    #--- Això sempre --------------------------------------------------
    formF=modelform_factory( Assignatura, fields=[ 'nom_assignatura' ]  )
    
    form = formF( instance = assignatura , prefix = str( assignatura.pk ) )
    formset.append( form )

    form.fields['nom_assignatura'].label = assignatura_label

    for alumne in alumnes:
        q1 = q2 = q3 = None
        qo = ""
        respostes = list(  alumne
                      .respostaavaluacioqualitativa_set
                      .filter( aquestaQualitativa  )
                      .filter( frase_oberta = "" ) 
                    )
        nRespostes = len( respostes )
        if nRespostes > 0: q1 = respostes[0].item
        if nRespostes > 1: q2 = respostes[1].item
        if nRespostes > 2: q3 = respostes[2].item
        #if nRespostes > 3: q4 = respostes[3].item

        respostes = ( alumne
                     .respostaavaluacioqualitativa_set
                     .filter( aquestaQualitativa  )
                     .exclude( frase_oberta = "" ) 
                    )
        if respostes.exists():
            qo = respostes[0].frase_oberta
        
        form=qualitativaItemsForm(
                                prefix=str( alumne.pk ),
                                initial={ 'alumne':  alumne ,
                                         'q1': q1,
                                         'q2': q2,
                                         'q3': q3,
                                         'qo': qo
                                         } ,
                                itemsQualitativa = itemsQualitativa)   
        
        if not obertaLaQualitativa:
            form.fields['q1'].widget.attrs['disabled']="True"
            form.fields['q2'].widget.attrs['disabled']="True"
            form.fields['q3'].widget.attrs['disabled']="True"
            form.fields['qo'].widget.attrs['disabled']="True"
            tipusForm = "formset.html"
        #else:
        form.fields['alumne'].widget.attrs['style']="width: 400px"
        form.fields['q1'].widget.attrs['style']="width: 450px"
        form.fields['q2'].widget.attrs['style']="width: 450px"
        form.fields['q3'].widget.attrs['style']="width: 450px"
        form.fields['qo'].widget.attrs['style']="width: 450px"    
        #tipusForm = "formsetgrid.html"
                    
        formset.append( form )
        #TODO: cal posar en mode readonly en cas d'estat tancat el periode de qualitativa.
        
    if assignatura.codi_assignatura == assignatura.nom_assignatura:
        msg=u"""En l'avaluació qualitativa, al canviar el codi de la matèria o optatives (ESO i Batxillerat) 
        o Mòdul Formatiu (Cicles) us demanaríem que escrigueu el nom en forma de Títol (no en majúscules) 
        per  unificar la visualització de matèries a l'horari quan el mirin els pares des del Djau.<br><br>

        Exemples:<br>
        <ul>
        <li>Matèria comuna: Nom de la matèria. P.ex.   Tecnologia</li>
        <li>Optatives ESO:  OPT Nom de la matèria. Pex,  OPT Dibuix Geomètric</li>
        <li>Modalitat BTX: Nom de la matèria P.ex Biologia</li>
        <li>Mòduls CFGM: codi Nom del mòdul.  P. ex. MP10 Empresa i administració</li>
        </ul>
        """
        messages.warning(request,  SafeText(msg ) )
        
    return render(
                  request,
                  tipusForm, 
                  { "formset": formset,
                    "head": u"Respostes avaluació qualitativa grup {0}".format( grup ),
                   "missatge": missatge,
                   "errors": errors
                   },
                )

@login_required
@group_required(['direcció'])
def resultats( request ):

    (user, l4) = tools.getImpersonateUser(request)
    professor = User2Professor( user )     
    
    report = []
    
 
    taula = tools.classebuida()
    taula.titol = tools.classebuida()
    taula.titol.contingut = ""
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 35
    capcelera.contingut = u'{0}'.format( u'Avaluació qualitativa' )
    taula.capceleres.append(capcelera)
    
    capcelera = tools.classebuida()
    capcelera.amplade = 65
    capcelera.contingut = u'Dades'
    taula.capceleres.append(capcelera)
    
    taula.fileres = []    
    for qualitativa in AvaluacioQualitativa.objects.all():
        filera = []
        camp = tools.classebuida()
        camp.contingut = u'{0}'.format(unicode( qualitativa ) )
        filera.append(camp)
        
        camp = tools.classebuida()
        obertaLaQualitativa =  qualitativa.data_obrir_avaluacio <=  date.today() <= qualitativa.data_tancar_avaluacio
        estat = '(Oberta)' if obertaLaQualitativa else '(Tancada)'
        camp.contingut = u'del {0} al {1} {2}'.format( qualitativa.data_obrir_avaluacio, qualitativa.data_tancar_avaluacio, estat)
        camp.enllac = '/avaluacioQualitativa/report/{0}'.format( qualitativa.pk )
        filera.append(camp)
        
        taula.fileres.append( filera )

        report.append(taula)
        
    return render(
                request,
                'report.html',
                    {'report': report,
                     'head': u'Avaluacions Qualitatives' ,
                    },
                )
    
@login_required
@group_required(['direcció'])        
def report(request, pk ):
    
    formset = []
    totBe = True
    head = u"Tria alumnes"
    
    qualitativa = AvaluacioQualitativa.objects.get( pk = pk )

    if request.method == 'POST':
        
        form = triaQualitativaForm( request.POST, prefix = 'qua' )
        formset.append( form )
        
        alumnes = []
        grups = []
        for grup in qualitativa.grups.all():
            form=alumnesGrupForm(
                                    request.POST,
                                    prefix=str( grup.pk ),
                                    queryset = grup.alumne_set.all()  ,       
                                    etiqueta = unicode(grup)                             
                                     )
            if form.is_valid():  
                alumnes += form.cleaned_data['alumnes']
                if form.cleaned_data['totElGrup']: grups.append( grup )
            else:
                totBe = False
                
                
        if totBe:            
            from . import reports
            return reports.reportQualitativa(qualitativa, alumnes, grups, request)
    else:
        form = triaQualitativaForm( initial = {'qualitativa': qualitativa }, prefix = 'qua' )
        formset.append( form )
        
        for grup in qualitativa.grups.all():
            #http://www.ibm.com/developerworks/opensource/library/os-django-models/index.html?S_TACT=105AGX44&S_CMP=EDU
            form=alumnesGrupForm(
                                    prefix=str( grup.pk ),
                                    queryset =  grup.alumne_set.all()  ,                                    
                                    etiqueta = unicode( grup )                             
                                     )
            formset.append( form )
        
    return render(
                  request,
                  "formset.html", 
                  {"formset": formset,
                   "head": head,
                   "formSetDelimited": True,
                   },
                 )
    
    
@login_required
def blanc( request ):
    return render(
                request,
                'blanc.html',
                    {},
                )

