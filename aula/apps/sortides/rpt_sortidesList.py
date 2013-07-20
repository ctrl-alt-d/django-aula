# This Python file uses the following encoding: utf-8
from aula.apps.tutoria.models import Tutor, SeguimentTutorialRespostes, ResumAnualAlumne
from aula.utils import tools
from django.db.models import Min, Max, Q
from django.utils.datetime_safe import  date, datetime
from aula.apps.alumnes.models import Alumne, Grup
from django.shortcuts import get_object_or_404
from aula.apps.sortides.models import Sortida
from django.core.urlresolvers import reverse

def sortidesListRpt(  ):    
    
    report = []
        
    taula = tools.classebuida()

    taula.titol = tools.classebuida()
    taula.titol.contingut = ''
    taula.titol.enllac = None

    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 100
    capcelera.contingut = 'Sortida'
    capcelera.enllac = ""
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'Dades Generals'
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'Opcions'
    taula.capceleres.append(capcelera)
    
  
    
    taula.fileres = []
        
       
        
    for sortida in Sortida.objects.all():
            
        filera = []
        
        #-Sortida--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = reverse( 'sortidaEditByPk' , kwargs={'pk': sortida.pk ,})
        camp.contingut = unicode(sortida.titol_de_la_sortida)
        filera.append(camp)

        #-Dades Gernerals--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = unicode(sortida)
        filera.append(camp)

        #-Opcions--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u'opcions'
        camp.enllac = None
        filera.append(camp)

        
        #--
        taula.fileres.append( filera )            
    report.append(taula)
    
    return report
    
    
        
        