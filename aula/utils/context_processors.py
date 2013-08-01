# This Python file uses the following encoding: utf-8
from aula.utils import tools
from django.utils.datetime_safe import date
from django.db.models import Count
from aula.utils.menu import calcula_menu

def dades_basiques(request):

    (user, l4) = tools.getImpersonateUser(request)
    sessioImpersonada = tools.sessioImpersonada(request)
    
    nMissatges= None
    try:
        nMissatges = user.destinatari_set.filter( moment_lectura__isnull = True ).count()
    except:
        pass

    teExpulsionsSenseTramitar= False
    try:
        from aula.apps.usuaris.models import User2Professor
        professor = User2Professor( user )
        teExpulsionsSenseTramitar = professor.expulsio_set.exclude( tramitacio_finalitzada = True ).count() > 0
    except:
        pass
   
    if not teExpulsionsSenseTramitar:
        try:
            from aula.apps.usuaris.models import User2Professional
            from aula.apps.alumnes.models import Alumne
            professional = User2Professional( user )
            teExpulsionsSenseTramitar = ( Alumne
                                          .objects
                                          .order_by()
                                          .filter( incidencia__professional = professional, 
                                                   incidencia__es_informativa = False, 
                                                   incidencia__es_vigent = True )
                                          .annotate( n = Count( 'incidencia' ) )
                                          .filter( n__gte = 3 )
                                          .exists()
                                        )
        except:
            pass      
    
    hiHaUnaQualitativaOberta = False
    try:
        from aula.apps.avaluacioQualitativa.models import AvaluacioQualitativa
        hiHaUnaQualitativaOberta = AvaluacioQualitativa.objects.filter(  data_obrir_avaluacio__lte =  date.today(),
                                                                         data_tancar_avaluacio__gte = date.today() ).exists()
    except:
        pass
        
    return {
            'data': date.today(),
            'user': user,
            'l4': l4,
            'sessioImpersonada': sessioImpersonada,
            'missatgesSenseLlegir': nMissatges,
            'teExpulsionsSenseTramitar': teExpulsionsSenseTramitar,
            'hiHaUnaQualitativaOberta': hiHaUnaQualitativaOberta,
            'menu': calcula_menu( user, request.path_info ),
             }
    

        
        
