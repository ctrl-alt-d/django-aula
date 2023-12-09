# This Python file uses the following encoding: utf-8
from aula.apps.tutoria.models import Tutor, SeguimentTutorialRespostes, ResumAnualAlumne
from aula.utils import tools
from django.db.models import Min, Max, Q
from aula.apps.alumnes.models import Alumne, Grup
from django.shortcuts import get_object_or_404
from aula.apps.sortides.models import Sortida
from django.urls import reverse
from django.contrib.auth.models import User

def sortidesListRpt( user ):    
    
    report = []
        
    taula = tools.classebuida()

    taula.titol = tools.classebuida()
    taula.titol.contingut = ''
    taula.titol.enllac = None

    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 40
    capcelera.contingut = 'Sortida'
    capcelera.enllac = ""
    taula.capceleres.append(capcelera)

    capcelera = tools.classebuida()
    capcelera.amplade = 60
    capcelera.contingut = u'Dades Generals'
    taula.capceleres.append(capcelera)
    
    taula.fileres = []
    
    q = Q( professor_que_proposa__pk = user.pk )
    if User.objects.filter( pk=user.pk, groups__name__in = [ 'sortides', 'direcció' ] ).exists():
        q |=  ~Q( estat = 'E' )
        
    for sortida in Sortida.objects.filter(q).order_by( '-data_inici' ):
            
        filera = []
        
        #-Sortida--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = reverse( 'sortides__sortides__edit_by_pk' , kwargs={'pk': sortida.pk ,})
        camp.contingut = u"{0} ({1})".format(sortida.titol_de_la_sortida, sortida.get_estat_display() )
        filera.append(camp)

        #-Dades Gernerals--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = None
        camp.contingut = u"{dpt} ( {datainici} )".format( dpt = sortida.departament_que_organitza, datainici = sortida.data_inici.strftime( '%d/%m/%Y' ) )
        filera.append(camp)
        
        #--
        taula.fileres.append( filera )            
    report.append(taula)
    
    return report
    
    
        
        