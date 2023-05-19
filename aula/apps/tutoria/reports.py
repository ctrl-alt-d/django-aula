# This Python file uses the following encoding: utf-8

from aula.apps.alumnes.models import  Nivell
from django.db.models import Q
from aula.utils import tools
from aula.apps.alumnes.models import  Grup
from aula.apps.presencia.models import ControlAssistencia
from aula.apps.assignatures.models import Assignatura
from aula.utils.tools import unicode
from django.conf import settings

def reportCalendariCursEscolarTutor( professor ):

    reports = []    
    for grup in Grup.objects.filter( pk__in = [ t.grup.pk for t in professor.tutor_set.all() ]  ):
        q_alumnes = Q( alumne__grup = grup )
        dies = ControlAssistencia.objects.filter( q_alumnes ).values_list('impartir__dia_impartir', flat=True).distinct()
        assignatures = Assignatura.objects.filter( 
                                horari__impartir__controlassistencia__alumne__grup = grup  
                        ).distinct().values( 'codi_assignatura', 'curs__nom_curs' )
        report = tools.classebuida()
        report.dies = sorted( dies )
        report.assignatures = [ u'{0}({1})'.format(a["codi_assignatura"], a["curs__nom_curs"] ) for a in assignatures ]
        reports.append(report)
        
    return reports

                     

def reportFaltesIncidencies( dataInici, dataFi , alumnes_informe = [], alumnes_recordatori = [], grups = [], request = None):

    import locale
    locale.setlocale(locale.LC_TIME, 'ca_ES.utf8')
        
    reports = []
    
    for nivell in Nivell.objects.all():
        for curs in nivell.curs_set.all():
            for grup in curs.grup_set.all():
                q_alumneTriat =  Q(pk__in = [a.pk for a in alumnes_informe ] + [a.pk for a in alumnes_recordatori ])
                q_grupTriat = Q( grup__in = grups )
                q_filtre_alumn = ( q_alumneTriat & q_grupTriat )
                               
                for alumne in grup.alumne_set.filter( q_filtre_alumn ).distinct(): 

                    report = tools.classebuida()

                    report.informe = alumne in alumnes_informe
                    report.recordatori = alumne in alumnes_recordatori
                    
                    report.resum = []
                    report.assistencia = []
                    report.observacions = []
                    report.incidencies = []
                    report.expulsions = []
                    report.correus = u', '.join( alumne.get_correus_relacio_familia() )
                    
                    report.data_inici = dataInici.strftime( '%d/%m/%Y' )
                    report.data_fi =  dataFi.strftime( '%d/%m/%Y' )  
                    
                    report.data = dataFi.strftime( '%d %B de %Y' )
                    
                    report.alumne = alumne
                    
                    q_desde = Q( impartir__dia_impartir__gte = dataInici )
                    q_finsa = Q( impartir__dia_impartir__lte = dataFi )
                    if settings.CUSTOM_NO_CONTROL_ES_PRESENCIA:
                        q_presencia = Q( estat__codi_estat__in = ['P','O'] ) | Q( estat__codi_estat__isnull=True )
                    else:
                        q_presencia = Q( estat__codi_estat__in = ['P','O'] )
                    q_null = Q( estat__isnull = True )
                    
                    n_faltes = 0
                    n_retards = 0
                    n_justificades = 0
                    for ca in alumne.controlassistencia_set.filter( q_desde & q_finsa & ~q_presencia & ~q_null ).order_by( 'impartir__dia_impartir', 'impartir__horari')  :
                        
                        itemAssitencia = tools.classebuida()
                        itemAssitencia.tipus = ca.estat
                        itemAssitencia.dia = ca.impartir.dia_impartir.strftime( '%d/%m/%Y' )
                        itemAssitencia.hora = ca.impartir.horari.hora
                        itemAssitencia.assignatura =  ca.impartir.horari.assignatura.getLongName()
                        if ca.estat.codi_estat == 'R':
                            n_retards += 1
                        elif ca.estat.codi_estat == 'F':
                            n_faltes += 1
                        elif ca.estat.codi_estat == 'J':
                            n_justificades += 1
                            
                        report.assistencia.append( itemAssitencia )
                    
                    item = tools.classebuida()
                    item.item = u'Faltes No Justificades'
                    item.valor = n_faltes
                    report.resum.append( item )
                                        
                    item = tools.classebuida()
                    item.item = u'Faltes Justificades'
                    item.valor = n_justificades
                    report.resum.append( item )
                                        
                    item = tools.classebuida()
                    item.item = u'Retards'
                    item.valor = n_retards
                    report.resum.append( item )

                    q_informativa = Q( tipus__es_informativa = True )
                    q_desde = Q( dia_incidencia__gte = dataInici )
                    q_finsa = Q( dia_incidencia__lte = dataFi )
                    
                    n_informatives = 0
                    for incidencia in alumne.incidencia_set.filter(q_informativa & q_desde & q_finsa):
                        NomAssignatura = ''
                        try:
                            NomAssignatura = incidencia.control_assistencia.impartir.horari.assignatura.getLongName() \
                                                         if incidencia.es_incidencia_d_aula() else ''
                        except:
                            pass
                        
                        item = tools.classebuida()
                        item.dia = incidencia.dia_incidencia.strftime( '%d/%m/%Y' )
                        item.hora = incidencia.franja_incidencia.hora_inici.strftime('%H:%M') 
                        item.assignatura = NomAssignatura
                        item.professor = incidencia.professional 
                        item.observacio = incidencia.descripcio_incidencia
                        
                        n_informatives += 1
                        
                        report.observacions.append(item)

                    item = tools.classebuida()
                    item.item = u'Observacions'
                    item.valor = n_informatives
                    report.resum.append( item )
                    
                    n_incidencies = 0
                    for incidencia in alumne.incidencia_set.filter( ~q_informativa & q_desde & q_finsa ):
                        NomAssignatura = ''
                        try:
                            NomAssignatura = incidencia.control_assistencia.impartir.horari.assignatura.getLongName() \
                                                         if incidencia.es_incidencia_d_aula() else ''
                        except:
                            pass
                        
                        item = tools.classebuida()
                        item.dia = incidencia.dia_incidencia.strftime( '%d/%m/%Y' )
                        item.hora = incidencia.franja_incidencia.hora_inici.strftime('%H:%M') 
                        item.assignatura = NomAssignatura
                        item.professor = incidencia.professional 
                        item.incidencia = incidencia.descripcio_incidencia
                        
                        n_incidencies += 1
                        
                        report.incidencies.append(item)
                    
                    item = tools.classebuida()
                    item.item = u'Incidències'
                    item.valor = n_incidencies
                    report.resum.append( item )
                    
                    q_desde = Q( dia_expulsio__gte = dataInici )
                    q_finsa = Q( dia_expulsio__lte = dataFi )
                    q_esborrany = Q(estat = 'ES' )
                    
                    n_expulsions = 0
                    for expulsio in alumne.expulsio_set.filter( q_desde & q_finsa & ~q_esborrany ):
                        NomAssignatura =  ''
                        try:
                            NomAssignatura = expulsio.control_assistencia.impartir.horari.assignatura.getLongName() \
                                                         if expulsio.es_incidencia_d_aula() else ''
                        except:
                            pass
                        
                        item = tools.classebuida()
                        item.dia = expulsio.dia_expulsio.strftime( '%d/%m/%Y' )
                        item.hora = expulsio.franja_expulsio.hora_inici.strftime('%H:%M') 
                        item.assignatura = NomAssignatura
                        item.professor = expulsio.professor 
                        item.motiu = expulsio.motiu
                        
                        n_expulsions += 1
                        
                        report.expulsions.append(item)

                    item = tools.classebuida()
                    item.item = u'Expulsions'
                    item.valor = n_expulsions
                    report.resum.append( item )
                    
                    report.detall = report.informe and ( n_expulsions + n_incidencies + n_informatives + n_faltes + n_justificades + n_retards > 0 )
                                            
                    if report: reports.append( report )      
                    
                #endfor alumne   
                            
                       
    #from django.template import Context                              
    from appy.pod.renderer import Renderer
    import html
    import os
    from django import http
    import time
    
    excepcio = None
    contingut = None
    try:
        
        #resultat = StringIO.StringIO( )
        resultat = "/tmp/DjangoAula-temp-{0}-{1}.odt".format( time.time(), request.session.session_key )
        #context = Context( {'reports' : reports, } )
        try:
            path = os.path.join( settings.PROJECT_DIR,  '../customising/docs/faltesIncidencies.odt' )
        except: 
            path = os.path.join(os.path.dirname(__file__), 'templates/faltesIncidencies.odt')
                    
        renderer = Renderer(path, {'reports' : reports, }, resultat)  
        renderer.run()
        docFile = open(resultat, 'rb')
        contingut = docFile.read()
        docFile.close()
        os.remove(resultat)
        
    except Exception as e:
        excepcio = unicode( e )
        
    if not excepcio:
        response = http.HttpResponse( contingut, content_type='application/vnd.oasis.opendocument.text')
        response['Content-Disposition'] = 'attachment; filename=assistencia_i_incidencies.odt'
    else:
        response = http.HttpResponse('''Els Gremlins odien el teu llistat! %s''' % html.escape(excepcio))

    
    return response                       








  
