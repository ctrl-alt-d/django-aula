from aula.apps.tutoria.models import TutorIndividualitzat
from aula.apps.usuaris.models import Professor
from aula.utils import tools
from aula.utils.tools import unicode
from aula.apps.alumnes.models import Alumne

def reportLlistaTutorsIndividualitzats(  ):

    tutors_ids = TutorIndividualitzat.objects.all().values_list( 'pk' )
    
    report = []
    
    #--sense alumnes.................
    taula = tools.classebuida()
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 30
    capcelera.contingut = u'{0}'.format('Professor')
    taula.capceleres.append( capcelera ) 
    
    capcelera = tools.classebuida()
    capcelera.amplade = 50
    capcelera.contingut = u'{0}'.format('Alumnes amb tutoria individualitzada')
    taula.capceleres.append( capcelera )
        
    capcelera = tools.classebuida()
    capcelera.amplade = 20
    capcelera.contingut = u'{0}'.format('Accions')
    taula.capceleres.append( capcelera ) 
        
    taula.fileres = []  
    for tutor in Professor.objects.all():
            filera = []
        
            #-nom--------------------------------------------
            camp = tools.classebuida()
            camp.enllac = ''
            camp.contingut = unicode(tutor) 
            filera.append(camp)

            #-alumnes....................
            camp = tools.classebuida()
            camp.multipleContingut = []
            for alumne in Alumne.objects.filter( tutorindividualitzat__professor = tutor ):
                
                camp.enllac = ''
                camp.multipleContingut.append( (unicode(alumne) + ' (' + unicode(alumne.grup) + ')', None,) )
            filera.append(camp)            

            #-accions--------------------------------------------
            camp = tools.classebuida()
            camp.enllac = '/alumnes/gestionaAlumnesTutor/{0}'.format( tutor.pk )
            camp.contingut = unicode(u"Gestiona Alumnes") 
            filera.append(camp)
            taula.fileres.append( filera )

    report.append(taula)
    
    return report
        
    
