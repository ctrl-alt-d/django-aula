# This Python file uses the following encoding: utf-8

from aula.apps.alumnes.models import  Nivell
from aula.apps.avaluacioQualitativa.models import  RespostaAvaluacioQualitativa
from django.db.models import Q
from aula.utils import tools
from django.template.context import RequestContext
from django.conf import settings
import os

def report_cartaAbsentisme( request, carta ):

                       
    #from django.template import Context                              
    from appy.pod.renderer import Renderer
    import cgi
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
                        }
        
        
        renderer = Renderer(path, dades_report, resultat)  
        renderer.run()
        docFile = open(resultat, 'rb')
        contingut = docFile.read()
        docFile.close()
        os.remove(resultat)
        
    except Exception, e:
        excepcio = unicode( e )
        
    if not excepcio:
        response = http.HttpResponse( contingut, content_type='application/vnd.oasis.opendocument.text')
        response['Content-Disposition'] = 'attachment; filename=cartaAbsencies.odt'
    else:
        response = http.HttpResponse('''Gremlin's ate you! %s''' % cgi.escape(excepcio))

    
    return response
     
            
    