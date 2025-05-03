# This Python file uses the following encoding: utf-8
from aula.utils import tools
from aula.apps.alumnes.models import Alumne
from django.db.models import Q
from itertools import chain

def duplicats_rpt():
    
    report = []
    
    taula = tools.classebuida()
    
    taula.tabTitle = 'Duplicacions detectades'
        
    taula.titol = tools.classebuida()
    taula.titol.contingut = u'Duplicacions detectades '
                                     
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 30
    capcelera.contingut = u'Grup duplicat'
    taula.capceleres.append( capcelera )
    
    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'Opcions'
    taula.capceleres.append( capcelera )    
    

    taula.fileres = []    
    
    for a in Alumne.objects.filter( data_baixa__isnull = True ):

        q_mateix_cognom = Q(                             
                        cognoms = a.cognoms )
        q_mateix_nom = Q( 
                        nom = a.nom,
                          )            
        q_mateix_neixement = Q(
                        data_neixement = a.data_neixement
                            )
        q_mateixa_altres = Q(
                        adreca = a.adreca,
                        #telefons = a.telefons,
                        localitat = a.localitat,
                        centre_de_procedencia = a.centre_de_procedencia,
                        adreca__gte= u""                             
                            )
        
        condicio1 = q_mateix_nom & q_mateix_cognom & q_mateix_neixement
        condicio2 = q_mateix_nom & q_mateix_cognom & q_mateixa_altres
        condicio3 = q_mateix_nom & q_mateixa_altres & q_mateix_neixement
        
        
        alumne_grup = Alumne.objects.filter(  
                                        condicio1 | condicio2 | condicio3
                                           )
        
        if alumne_grup.count() > 1:
            filera = []
            
            #-grup--------------------------------------------
            camp = tools.classebuida()
            camp.multipleContingut =  [ (u'{0} {1}'.format(ag, ag.grup.nom_grup ), None )  for ag in alumne_grup ]                                                                           
            filera.append(camp)              

            #-opcions--------------------------------------------
            camp = tools.classebuida()
            camp.esMenu = True
            primer_alumne = a #list( chain( alumne_grup.filter( data_baixa__isnull = False).order_by( u'data_baixa'  ) , alumne_grup.filter( data_baixa__isnull = True) ) )[0]
            camp.multipleContingut =  [ (u'Fusionar', u'/alumnes/fusiona/{0}'.format( primer_alumne.pk )) , ]                                                                           
            filera.append(camp)              

            taula.fileres.append( filera )

    report.append(taula)
    
    return report                
            