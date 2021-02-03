# This Python file uses the following encoding: utf-8
from aula.utils import tools
from aula.utils.tools import unicode
from aula.apps.alumnes.models import Alumne
from django.db.models.aggregates import Count
from django.db.models import Q, F, Case, When, IntegerField
from itertools import chain
from aula.apps.presencia.models import ControlAssistencia
#amorilla@xtec.cat
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.conf import settings
import csv
from django.http import HttpResponse

def alertaAssitenciaReport( data_inici, data_fi, nivell, tpc , ordenacio ):
    report = []

    
    taula = tools.classebuida()
    
    taula.titol = tools.classebuida()
    taula.titol.contingut = u'Ranking absència alumnes nivell {0}'.format( nivell )
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 30
    capcelera.contingut = u'Alumne'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 15
    capcelera.contingut = u'hores absent no justificat'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'hores docència'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = u'%absència no justificada (absènc.no.justif./docència)'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 5
    capcelera.contingut = u'hores present'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'hores absènc. justif.'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'% assistència'
    taula.capceleres.append( capcelera )


    taula.fileres = []
    

#     q_nivell = Q( grup__curs__nivell = nivell )
#     q_data_inici = Q(  controlassistencia__impartir__dia_impartir__gte = data_inici  )
#     q_data_fi = Q(  controlassistencia__impartir__dia_impartir__lte = data_fi  )
#     q_filte = q_nivell & q_data_inici & q_data_fi
#     q_alumnes = Alumne.objects.filter( q_filte )
# 
#     q_p = q_alumnes.filter( controlassistencia__estat__codi_estat__in = ('P','R' ) ).order_by().distinct().annotate( x=Count('controlassistencia__estat') ).values_list( 'id', 'x' )
#     q_j = q_alumnes.filter( controlassistencia__estat__codi_estat = 'J' ).order_by().distinct().annotate( x=Count('controlassistencia__estat') ).order_by().distinct().values_list( 'id', 'x' )
#     q_f = q_alumnes.filter( controlassistencia__estat__codi_estat = 'F' ).order_by().distinct().annotate( x=Count('controlassistencia__estat') ).values_list( 'id', 'x' )

#     dict_p, dict_j, dict_f = dict( q_p ), dict( q_j ), dict( q_f )


    q_alumnes = Alumne.objects.filter( grup__curs__nivell = nivell )    
    
    q_data_inici = Q( impartir__dia_impartir__gte = data_inici  )
    q_data_fi = Q( impartir__dia_impartir__lte = data_fi  )
    q_filtre = q_data_inici & q_data_fi
    q_controls = ControlAssistencia.objects.filter(  alumne__in = q_alumnes ).filter( q_filtre )

    #amorilla@xtec.cat
    if settings.CUSTOM_NO_CONTROL_ES_PRESENCIA:
        # té en compte tots els dies encara que no s'hagi passat llista
        q_p = q_controls.order_by().values_list( 'id','alumne__id' ).distinct()
    else:
        q_p = q_controls.filter( estat__codi_estat__in = ('P','R','O' ) ).order_by().values_list( 'id','alumne__id' ).distinct()

    q_j = q_controls.filter( estat__codi_estat = 'J' ).order_by().values_list( 'id','alumne__id' ).distinct()
    q_f = q_controls.filter( estat__codi_estat = 'F' ).order_by().values_list( 'id','alumne__id' ).distinct()
    
    from itertools import groupby
    dict_p = {}
    data = sorted(q_p, key=lambda x: x[1])
    for k, g in groupby( data, lambda x: x[1] ):
        dict_p[k] = len( list(g) )
    
    dict_j = {}
    data = sorted(q_j, key=lambda x: x[1])
    for k, g in groupby( data, lambda x: x[1] ):
        dict_j[k] = len( list(g) )

    dict_f = {}
    data = sorted(q_f, key=lambda x: x[1])
    for k, g in groupby( data, lambda x: x[1] ):
        dict_f[k] = len( list(g) )
    
    #ajuntar dades diferents fonts
    alumnes = []
    for alumne in q_alumnes.select_related( 'grup', 'grup__curs' ).order_by().distinct():
        alumne.p = dict_p.get( alumne.id, 0)
        alumne.j = dict_j.get( alumne.id, 0)
        alumne.f = dict_f.get( alumne.id, 0)
        alumne.ca = alumne.p + alumne.j + alumne.f or 0.0
        alumne.tpc = ( float( alumne.f ) / float( alumne.ca ) ) * 100.0 if alumne.ca > 0 else 0
        alumne.tpc_assist =  ( float( alumne.p )  / float( alumne.ca ) ) * 100.0 if alumne.ca > 0 else 0
        alumnes.append(alumne)
    #----------------------
    #choices = ( ('a', u'Nom alumne',), ('ca', u'Curs i alumne',),('n',u'Per % Assistència',), ('cn',u'Per Curs i % Assistència',),
    order_a = lambda a: ( a.cognoms,  a.nom)
    order_ca = lambda a: ( a.grup.curs.nom_curs, a.grup.nom_grup, a.cognoms, a.nom )
    order_n = lambda a: ( -1 * a.tpc, -1 * a.f )
    order_cn = lambda a: ( a.grup.curs.nom_curs, a.grup.nom_grup  , -1 * a.tpc)
    order = order_ca if ordenacio == 'ca' else order_n if ordenacio == 'n' else order_cn if ordenacio == 'cn' else order_a
    
    
    for alumne in  sorted( [ a for a in alumnes if a.tpc > tpc ] , key=order  ):   
                
        filera = []
        
        #-nom--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = '/tutoria/detallTutoriaAlumne/{0}/all'.format(alumne.pk )
        camp.contingut = unicode(alumne) + ' (' + unicode(alumne.grup) + ')'
        filera.append(camp)

        #-docència--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = unicode(alumne.f) 
        filera.append(camp)

        #-present--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = unicode(alumne.ca) 
        filera.append(camp)

        #-%--------------------------------------------
        camp = tools.classebuida()
        camp.contingut =u'{0:.2f}%'.format(alumne.tpc ) 
        filera.append(camp)
        
        #-absent--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = unicode(alumne.p) 
        filera.append(camp)

        #-justif--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = unicode(alumne.j) 
        filera.append(camp)

        #-assist--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = u'{0:.2f}%'.format(alumne.tpc_assist) 
        filera.append(camp)



        taula.fileres.append( filera )

    report.append(taula)

    return report

#amorilla@xtec.cat
# Calcula l'indicador d'absentisme, segons el nivell, percentatge i dates.
def indicadorAbsentisme( data_inici, data_fi, nivell, tpc, recerca):

    # Selecciona alumnes del nivell i que no siguin baixa
    q_alumnes = Alumne.objects.filter( grup__curs__nivell__nom_nivell__in = settings.CUSTOM_NIVELLS[nivell]).filter(data_baixa__isnull=True )    
    # Selecciona en les dates indicades
    q_data_inici = Q( impartir__dia_impartir__gte = data_inici  )
    q_data_fi = Q( impartir__dia_impartir__lte = data_fi  )
    q_filtre = q_data_inici & q_data_fi
    q_controls = ControlAssistencia.objects.filter(  alumne__in = q_alumnes ).filter( q_filtre )
    
    if recerca==None:
        recerca=('J','F')  # Per defecte compta les 'F' i les 'J'
    
    # calcula el 'total' de dies per alumne i les 'faltes' per alumne.
    if settings.CUSTOM_NO_CONTROL_ES_PRESENCIA:
        # té en compte tots els dies encara que no s'hagi passat llista
        q_p = q_controls.values('alumne__id').annotate(total=Count('id'), faltes=Count(Case(When(estat__codi_estat__in = recerca, then=1),output_field=IntegerField())))
    else:
        q_p = q_controls.values('alumne__id').annotate(total=Count(Case(When(estat__codi_estat__in = ('J','F','P','R','O' ), then=1),output_field=IntegerField())), faltes=Count(Case(When(estat__codi_estat__in = recerca, then=1),output_field=IntegerField())))

    quantitat=q_p.count()
    # Calcula el percentatge d'absentisme per alumne i compta els que superen el límit indicat
    superen = q_p.annotate(per=F('faltes')*100.0/F('total')).filter(per__gt=tpc).count() if quantitat > 0 else 0

    # Percentatge d'alumnes que superen el límit
    IND=float(superen)/float(quantitat) * 100.0 if quantitat > 0 else 0

    return (IND, superen, quantitat)

#amorilla@xtec.cat
# mostra el report de tots els indicadors de CUSTOM_INDICADORS
def indicadorsReport():

    report = []

    taula = tools.classebuida()
    
    taula.titol = tools.classebuida()
    taula.titol.contingut = u'Indicadors Absentisme'
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'Curs'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'Nivell'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 8
    capcelera.contingut = u'% ind.'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 8
    capcelera.contingut = u'1rTrim'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 8
    capcelera.contingut = u'2nTrim'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 8
    capcelera.contingut = u'3rTrim'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 8
    capcelera.contingut = u'Curs'
    taula.capceleres.append( capcelera )

    if len(settings.CUSTOM_INDICADORS)==0:
        # Report per defecte si no n'hi ha cap indicador
        taula.fileres = []
        filera = []
        camp = tools.classebuida()
        camp.contingut="No n'hi ha indicadors definits"
        filera.append(camp)
        taula.fileres.append( filera )
        filera = []
        camp = tools.classebuida()
        camp.contingut="S'han de definir a CUSTOM_INDICADORS"
        filera.append(camp)
        taula.fileres.append( filera )
        report.append(taula)
        return (report, None)

    taula.fileres = []

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="indicadors.csv"'
    writer = csv.writer(response)
    writer.writerow(['Curs', 'Nivell', '%', 
                     'ini1rT', 'fi1rT', 'sup1rT', 'tot1rT', 'ind1rT', 
                     'ini2nT', 'fi2nT', 'sup2nT', 'tot2nT', 'ind2nT', 
                     'ini3rT', 'fi3rT', 'sup3rT', 'tot3rT', 'ind3rT', 
                     'inicurs', 'ficurs', 'supc', 'totc', 'indc'
                     ])

    for ind in settings.CUSTOM_INDICADORS:
        data = date.today()
        data = datetime(year=data.year, month=data.month, day=data.day)
        dtrim0=datetime.strptime(ind[0], '%d/%m/%Y')
        dtrim1=datetime.strptime(ind[1], '%d/%m/%Y')
        dtrim2=datetime.strptime(ind[2], '%d/%m/%Y')
        dtrim3=datetime.strptime(ind[3], '%d/%m/%Y')
        undia=relativedelta(days=+1)
        nivell = ind[4]
        tpc = ind[5]
        # Tipus de controls és opcional
        if (len(ind)>=7):
            recerca=ind[6]
            # Assegura que s'obtingui una tupla, això permet que es pugui
            # fer servir 'F' o ('F') o ('F',) ... sense que provoqui error
            if len(recerca)==1:
                recerca=tuple(recerca[0])
        else:
            recerca=None
        trim1=0
        trim2=0
        trim3=0
        curs=0
        sup1=sup2=sup3=quan1=quan2=quan3=0
        if data>dtrim1:
            (trim1, sup1, quan1)=indicadorAbsentisme( dtrim0, dtrim1, nivell, tpc, recerca)

        if data>dtrim2:
            # Suma un dia per evitar que compti dos cops el final de trimestre
            (trim2, sup2, quan2)=indicadorAbsentisme( dtrim1+undia, dtrim2, nivell, tpc, recerca)

        if data>dtrim3:
            # Suma un dia per evitar que compti dos cops el final de trimestre
            (trim3, sup3, quan3)=indicadorAbsentisme( dtrim2+undia, dtrim3, nivell, tpc, recerca)
        
        (curs, supc, quanc)=indicadorAbsentisme( dtrim0, dtrim3, nivell, tpc, recerca)

    
        filera = []
        
        #-Curs--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = dtrim0.strftime("%Y") + "/" + dtrim3.strftime("%Y")
        filera.append(camp)

        #-nivell--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = unicode(nivell)
        filera.append(camp)

        #-% ind--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = u'{0:.2f}%'.format(tpc)
        filera.append(camp)

        #-%1rTrim--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = u'{0:.2f}%'.format(trim1)
        filera.append(camp)

        #-%2nTrim--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = u'{0:.2f}%'.format(trim2)
        filera.append(camp)
        
        #-%3rTrim--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = u'{0:.2f}%'.format(trim3)
        filera.append(camp)

        #-%Curs--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = u'{0:.2f}%'.format(curs)
        filera.append(camp)

        writer.writerow([filera[0].contingut, filera[1].contingut, filera[2].contingut,
                         ind[0], ind[1], sup1, quan1, trim1,
                         (dtrim1+undia).strftime('%d/%m/%Y'), ind[2], sup2, quan2, trim2,
                         (dtrim2+undia).strftime('%d/%m/%Y'), ind[3], sup3, quan3, trim3,
                         ind[0], ind[3], supc, quanc, curs
                         ])

        taula.fileres.append( filera )

    report.append(taula)

    return (report, response)

