# This Python file uses the following encoding: utf-8

from aula.apps.alumnes.models import  Nivell
from aula.apps.avaluacioQualitativa.models import  RespostaAvaluacioQualitativa
from django.db.models import Q
from aula.utils import tools
from aula.apps.assignatures.models import Assignatura
from django.shortcuts import render
from django.template.context import RequestContext
from aula.utils.tools import write_pdf, unicode
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
     
            





#http://xhtml2pdf.appspot.com/static/pisa-en.html
def reportQualitativa2( qualitativa , alumnes = [], grups = [], request = None):

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
                    report = []
                    taula = tools.classebuida()
                    taula.titol = tools.classebuida()
                    taula.titol.contingut = ""
                    taula.classe = 'titol'
                    taula.capceleres = []
                    taula.printIfEmpty = True
                    
                    capcelera = tools.classebuida()
                    capcelera.amplade = 100
                    capcelera.contingut = u'''Butlletí de qualificacions de l'avaluació qualitativa.'''.upper()
                    taula.capceleres.append(capcelera)
                    taula.fileres = []

                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u'Benvolguts tutors/res'
                    filera.append(camp)      
                    taula.fileres.append(filera)              
                    
                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u'''L’equip de professors de l’alumne/a {0} que cursa {1} us fem arribar un full de seguiment 
                    de començament de curs. En aquest butlletí us notifiquem algunes observacions que ens semblen significatives en 
                    aquest inici del curs. Esperem que us sigui d’utilitat per prendre les decisions correctes pel normal 
                    desenvolupament del curs.'''.format( alumne, alumne.grup )
                    filera.append(camp)      
                    taula.fileres.append(filera)              
                    
                    report.append(taula)
        
                    taula = tools.classebuida()
                    taula.titol = tools.classebuida()
                    taula.titol.contingut = ""
                    taula.capceleres = []
                    taula.classe = 'pijama'
                    
                    capcelera = tools.classebuida()
                    capcelera.amplade = 25
                    capcelera.contingut = u'''Matèria'''
                    taula.capceleres.append(capcelera)

                    capcelera = tools.classebuida()
                    capcelera.amplade = 75
                    capcelera.contingut = u'''Comentaris'''
                    taula.capceleres.append(capcelera)   
                    
                    taula.fileres = []                 
                    
                    for assignatura in Assignatura.objects.filter( 
                                        respostaavaluacioqualitativa__qualitativa = qualitativa,
                                        respostaavaluacioqualitativa__alumne = alumne  
                                        ).distinct():
                        
                        esPrimeraResposta = True
                        for resposta in RespostaAvaluacioQualitativa.objects.filter(
                                         alumne = alumne,
                                         assignatura = assignatura ):
                            
                            filera = []
                            
                            camp = tools.classebuida()
                            camp.contingut = u'{0}'.format( assignatura.nom_assignatura if esPrimeraResposta else '' )
                            filera.append(camp)

                            camp = tools.classebuida()
                            camp.contingut = u'{0}'.format( resposta.item  )
                            filera.append(camp)   
                                                                                 
                            taula.fileres.append( filera )
                            
                            esPrimeraResposta = False
                        #endfor resposta
                        
                    #endfor assignatura
                    report.append(taula) #------------------------------------------------------------------------------
                    
                    taula = tools.classebuida()
                    taula.titol = tools.classebuida()
                    taula.titol.contingut = ""
                    taula.classe = 'pijama'
                    taula.capceleres = []
                    
                    capcelera = tools.classebuida()
                    capcelera.amplade = 80
                    capcelera.contingut = u'''Comentari del tutor/a'''
                    taula.capceleres.append(capcelera)
                    taula.fileres = []

                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u''
                    filera.append(camp)      
                    taula.fileres.append(filera)  

                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u'_____________________________________________________________________________________'
                    filera.append(camp)      
                    taula.fileres.append(filera)  
                    taula.fileres.append(filera)  
                    taula.fileres.append(filera)  
                    report.append(taula) #------------------------------------------------------------------------------

                    taula = tools.classebuida()
                    taula.titol = tools.classebuida()
                    taula.titol.contingut = ""
                    taula.classe = 'pijama'
                    taula.capceleres = []
                    taula.fileres = []
                                        
                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u'Atentament,'
                    filera.append(camp)      
                    taula.fileres.append(filera)  

                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u'{0}'.format( u','.join( [u'Sr(a) ' + unicode(t.professor) for t in alumne.tutorsDeLAlumne() ] ) )  
                    filera.append(camp)      
                    taula.fileres.append(filera)

                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = settings.LOCALITAT+ u', a {0}'.format( qualitativa.data_tancar_avaluacio.strftime( '%d %B de %Y' ) )  
                    filera.append(camp)      
                    taula.fileres.append(filera)

                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u'''................................................................................
                    .......................................................................................'''
                    filera.append(camp)      
                    taula.fileres.append(filera)
                    report.append(taula) #------------------------------------------------------------------------------
                    
                    taula = tools.classebuida()
                    taula.titol = tools.classebuida()
                    taula.titol.contingut = ""
                    taula.classe = 'pijama'
                    taula.capceleres = []
                    taula.fileres = []
                                        
                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u'''El/la Sr/a ______________________________________ com a pare / mare / tutor/a de l'alumne
                    {0} de {1}, he rebut el butlletí de qualificacions de l'avaluació qualitativa.'''.format( alumne, alumne.grup )
                    filera.append(camp)      
                    taula.fileres.append(filera)  
                    
                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u'Signat:'
                    filera.append(camp)      
                    taula.fileres.append(filera)  

                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u'DNI núm:'
                    filera.append(camp)      
                    taula.fileres.append(filera)  

                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u''
                    filera.append(camp)      
                    taula.fileres.append(filera)  
                    taula.fileres.append(filera)  

                    filera = []
                    camp = tools.classebuida()
                    camp.contingut = u'_________________, ____ de _______________ de {0}'.format( qualitativa.data_tancar_avaluacio.year )
                    filera.append(camp)      
                    taula.fileres.append(filera)  
                    report.append(taula) #------------------------------------------------------------------------------

                    
                    if report: reports.append( report )      
                    
                #endfor alumne   
                            
                       
                              
    formatPDF = True
    if formatPDF:
        return write_pdf('pdfReport.html',{
            'pagesize' : 'A4',
            'reports' : reports,
            })
    else:
        return render(
            request,
            'report.html',
                {'report': report,
                 'head': u'Avaluacions Qualitatives' ,
                },
            )



