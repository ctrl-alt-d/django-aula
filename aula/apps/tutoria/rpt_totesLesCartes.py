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
    capcelera.amplade = 20
    capcelera.contingut = u'Data'
    taula.capceleres.append(capcelera)
    
    capcelera = tools.classebuida()
    capcelera.amplade = 60
    capcelera.contingut = u'Alumne'
    capcelera.enllac = ""
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = u'Cartes nº.'
    taula.capceleres.append(capcelera)
    
    taula.fileres = []    
    
    for carta in CartaAbsentisme.objects.filter(data_carta__isnull=False).order_by( '-data_carta'):
            
        filera = []
        
        #-data--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = date( carta.data_carta , 'j N Y')
        filera.append(camp)

        #-alumne--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        
        from aula.apps.alumnes.named_instances import curs_any_fi
        te_mes_de_16 = ( u", Més de 16 anys (durant el curs)" 
                         if (carta.alumne.cursa_obligatoria() and
                            (curs_any_fi() - carta.alumne.data_neixement.year) > 16)
                         else ""
                        )
        camp.contingut = u"{0} - {1} {2}".format( carta.alumne, carta.alumne.grup, te_mes_de_16 )
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
    
    