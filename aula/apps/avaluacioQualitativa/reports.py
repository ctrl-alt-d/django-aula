# This Python file uses the following encoding: utf-8

from aula.apps.alumnes.models import  Nivell
from aula.apps.avaluacioQualitativa.models import  RespostaAvaluacioQualitativa
from django.db.models import Q
from aula.utils import tools
from aula.apps.assignatures.models import Assignatura
from aula.utils.tools import unicode
from django.conf import settings 

#http://xhtml2pdf.appspot.com/static/pisa-en.html
def reportQualitativa( qualitativa , alumnes = [], grups = [], request = None):

    import locale
    locale.setlocale(locale.LC_TIME, 'ca_ES.utf8')
    
    reports = []
    
    for nivell in Nivell.objects.all():
        for curs in nivell.curs_set.all():
            for grup in curs.grup_set.all():
                q_teRespostes = Q(respostaavaluacioqualitativa__isnull = False) 
                q_alumneTriat =  Q(pk__in = [a.pk for a in alumnes ])
                q_grupTriat = Q( grup__in = grups )
                q_filtre_alumn = q_teRespostes & ( q_alumneTriat | q_grupTriat )
                               
                for alumne in grup.alumne_set.filter( q_filtre_alumn ).distinct(): 
                    report = tools.classebuida()
                    
                    report.alumne = alumne
                    capceleres_materies = set()
                    report.respostes = []
                    report.data = qualitativa.data_tancar_avaluacio.strftime( '%d %B de %Y' )
                    
                    report.tutors = u', '.join( [u'Sr(a) ' + unicode(t) for t in alumne.tutorsDeLAlumne() ] )
                    
                    for assignatura in Assignatura.objects.filter( 
                                        respostaavaluacioqualitativa__qualitativa = qualitativa,
                                        respostaavaluacioqualitativa__alumne = alumne  
                                        ).distinct():
                        resposta = tools.classebuida()
                        resposta.assignatura = assignatura.getLongName()
                        
                        te_tipus_assignatura = hasattr(resposta.assignatura, 'tipus_assignatura') 
                        cacelera_txt = resposta.assignatura.tipus_assignatura.capcelera if te_tipus_assignatura else u"Matèria" 
                        capceleres_materies.add( cacelera_txt )
                        
                        resposta.frases = []
                        for respostaQualitativa in RespostaAvaluacioQualitativa.objects.filter(
                                         alumne = alumne,
                                         assignatura = assignatura ):
                            
                            if respostaQualitativa.frase_oberta:
                                resposta.frases.append(respostaQualitativa.frase_oberta ) 
                            else:
                                resposta.frases.append(respostaQualitativa.item ) 
                        
                        report.respostes.append( resposta )

                        #endfor resposta
                    
                    report.materia = u" / ".join( capceleres_materies )
                    
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
        path = None
        path = os.path.join( settings.PROJECT_DIR,  '../customising/docs/qualitativa.odt' )
        if not os.path.isfile(path): 
            path = os.path.join(os.path.dirname(__file__), 'templates/qualitativa.odt')
            
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
        response['Content-Disposition'] = 'attachment; filename=qualitativa.odt'
    else:
        response = http.HttpResponse('''Gremlin's ate your pdf! %s''' % html.escape(excepcio))

    
    return response
