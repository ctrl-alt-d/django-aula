# This Python file uses the following encoding: utf-8

from aula.utils import tools
from aula.utils.tools import unicode
from aula.apps.baixes.models import Feina
from aula.apps.usuaris.models import User2Professor
from aula.apps.presencia.models import Impartir
from django.template.defaultfilters import date
from appy.pod.renderer import Renderer
from django.conf import settings

#http://xhtml2pdf.appspot.com/static/pisa-en.html
def reportBaixaCarpeta( request, dia, professors ):
    
    credentials = tools.getImpersonateUser(request) 
    (user, _ ) = credentials
    
    professor = User2Professor( user ) 
    
    reports = []
    
    for professor in professors:
        report = tools.classebuida()
        report.professor = professor     
        report.data = date( dia, "l, d M \d\e Y"  )
        
        imparticions = ( Impartir
                        .objects.filter( dia_impartir = dia, 
                                                 horari__professor = professor   )
                        .order_by( 'horari__hora__hora_inici' )
                              )
        
        report.imparticions = []
        
        for i in imparticions:
            Feina.objects.get_or_create( impartir = i , 
                                         defaults = {'professor_darrera_modificacio':professor, } )
            
            impartir = tools.classebuida()
            impartir.hora = i.horari.hora
            impartir.grup = i.horari.grup
            impartir.assignatura = i.horari.assignatura
            impartir.aula= i.horari.nom_aula
            impartir.profguard = i.feina.professor_fa_guardia
            impartir.comments = i.feina.comentaris_per_al_professor_guardia
            impartir.feina = i.feina.feina_a_fer
            impartir.comments2 = i.feina.comentaris_professor_guardia
            report.imparticions.append( impartir )


                    
        reports.append( report )      
                    
                       
    #from django.template import Context                              
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
        try:
            path = os.path.join( settings.PROJECT_DIR,  '../customising/docs/carpetaBaixes.odt' )
        except: 
            path = os.path.join(os.path.dirname(__file__), 'templates/carpetaBaixes.odt')
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
        response['Content-Disposition'] = 'attachment; filename=professor-baixa.odt'
    else:
        response = http.HttpResponse('''Gremlin's ate your pdf! %s''' % html.escape(excepcio))

    
    return response
     
            


