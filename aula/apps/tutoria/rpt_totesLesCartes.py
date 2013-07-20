# This Python file uses the following encoding: utf-8
from aula.apps.tutoria.models import CartaAbsentisme
from aula.utils import tools

from django.template.defaultfilters import date

def totesLesCartesRpt( ):
    
    report = []

    #--- Grups ----------------------------------------------------------------------------

    taula = tools.classebuida()

    taula.titol = tools.classebuida()
    taula.titol.contingut = ''
    taula.titol.enllac = None

    taula.capceleres = []

    capcelera = tools.classebuida()
    capcelera.amplade = 100
    capcelera.contingut = u'Data'
    taula.capceleres.append(capcelera)
    
    capcelera = tools.classebuida()
    capcelera.amplade = 200
    capcelera.contingut = u'Alumne'
    capcelera.enllac = ""
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 100
    capcelera.contingut = u'Cartes nº.'
    taula.capceleres.append(capcelera)
    
    taula.fileres = []    
    
    for carta in CartaAbsentisme.objects.all().order_by( '-data_carta'):
            
        filera = []
        
        #-data--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = date( carta.data_carta , 'j N Y')
        filera.append(camp)

        #-alumne--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = carta.alumne
        filera.append(camp)

        #-carta num--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = r'/tutoria/imprimirCartaNoFlag/{0}'.format( carta.pk )
        camp.contingut = '{0}'.format( carta.carta_numero)
        filera.append(camp)
        
        #--
        taula.fileres.append( filera )    
                
    report.append(taula)
        
    return report
    
    