# This Python file uses the following encoding: utf-8

from aula.apps.alumnes.models import  Nivell
from aula.apps.avaluacioQualitativa.models import  RespostaAvaluacioQualitativa
from django.db.models import Q
from aula.utils.tools import unicode
from django.template.context import RequestContext
from django.conf import settings
import os

def report_cartaAbsentisme( request, carta ):

                       
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
        path = None
        path = os.path.join( settings.PROJECT_DIR,  '../customising/docs/cartesFaltesAssistencia.odt' )
        if not os.path.isfile(path):
            path = os.path.join(os.path.dirname(__file__), 'templates/cartesFaltesAssistencia.odt')

        # amorilla@xtec.cat  
        try:
            datafmt = settings.CUSTOM_DATE_FORMAT
            carta_data=carta.data_carta.strftime( datafmt )
        except:
            datafmt = "%-d %B de %Y"
            carta_data=carta.data_carta.strftime( datafmt )

        try:
            des_de_data = carta.faltes_des_de_data.strftime( '%d/%m/%Y' )
        except:
            des_de_data = ''

        dades_report = {'professor':carta.professor,
                        'alumne': unicode(carta.alumne),
                        'grup':unicode(carta.alumne.grup),
                        'nfaltes':carta.nfaltes,
                        'year':carta.data_carta.year,
                        'fins_a_data': carta.faltes_fins_a_data.strftime( '%d/%m/%Y' ),
                        'tipus1': carta.tipus_carta == 'tipus1',
                        'tipus2': carta.tipus_carta == 'tipus2',
                        'tipus3A': carta.tipus_carta == 'tipus3A',
                        'tipus3B': carta.tipus_carta == 'tipus3B',
                        'tipus3C': carta.tipus_carta == 'tipus3C',
                        'tipus3D': carta.tipus_carta == 'tipus3D',
                        # amorilla@xtec.cat  
                        # nous elements per personalitzar la carta
                        'data': carta_data,
                        'des_de_data': des_de_data,
                        'adreca': carta.alumne.adreca,
                        'cp': carta.alumne.cp,
                        'localitat': carta.alumne.localitat,
                        'municipi': carta.alumne.municipi,
                        'cognoms': carta.alumne.cognoms,
                        'nivell': carta.alumne.getNivellCustom(),  # nivell de CUSTOM_NIVELLS
                        'edat': carta.alumne.edat(carta.data_carta),
                        'numcarta': carta.carta_numero,
                        }
        
        
        renderer = Renderer(path, dades_report, resultat)  
        renderer.run()
        docFile = open(resultat, 'rb')
        contingut = docFile.read()
        docFile.close()
        os.remove(resultat)
        
    except Exception as e:
        excepcio = unicode( e )
        
    if not excepcio:
        response = http.HttpResponse( contingut, content_type='application/vnd.oasis.opendocument.text')
        response['Content-Disposition'] = 'attachment; filename=cartaAbsencies.odt'
    else:
        response = http.HttpResponse('''Gremlin's ate you! %s''' % html.escape(excepcio))

    
    return response
     
            
    
