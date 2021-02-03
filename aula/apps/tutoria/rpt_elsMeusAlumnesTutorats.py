# This Python file uses the following encoding: utf-8
from aula.apps.tutoria.models import Tutor, SeguimentTutorialRespostes, ResumAnualAlumne
from aula.utils import tools
from aula.utils.tools import unicode
from django.db.models import Min, Max, Q
from django.utils.datetime_safe import  date, datetime
from aula.apps.alumnes.models import Alumne, Grup
from django.shortcuts import get_object_or_404
from django.conf import settings

def elsMeusAlumnesTutoratsRpt( professor = None, grup = None  , dataDesDe = None , dataFinsA = date.today() ):    
    
    report = []

    if professor:
        grups = [ t.grup for t in  Tutor.objects.filter( professor = professor )]
        grups.append( 'Altres' )
    else:
        grup =  get_object_or_404( Grup, pk = grup )
        grups = [ grup ]
    
    for grup in grups:
        
        taula = tools.classebuida()

        taula.titol = tools.classebuida()
        taula.titol.contingut = ''
        taula.titol.enllac = None

        taula.capceleres = []
        
        capcelera = tools.classebuida()
        capcelera.amplade = 30
        capcelera.contingut = grup if grup == u'Altres' else u'{0} ({1})'.format( grup  ,  grup.curs  ) 
        capcelera.enllac = ""
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Faltes.'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 10
        capcelera.contingut = u'Disciplina'
        taula.capceleres.append(capcelera)
        
        capcelera = tools.classebuida()
        capcelera.amplade = 5
        capcelera.contingut = u'Actuacions'
        taula.capceleres.append(capcelera)
        
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Familia'
        taula.capceleres.append(capcelera)
                    
        capcelera = tools.classebuida()
        capcelera.amplade = 10
        capcelera.contingut = u'Seguiment'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 10
        capcelera.contingut = u'Històric'
        taula.capceleres.append(capcelera)
                
        capcelera = tools.classebuida()
        capcelera.amplade = 15
        capcelera.contingut = u'Qualitativa'
        taula.capceleres.append(capcelera)

        capcelera = tools.classebuida()
        capcelera.amplade = 5
        capcelera.contingut = u'Tot'
        taula.capceleres.append(capcelera)
        
        taula.fileres = []
        
        if grup == 'Altres':
            consulta_alumnes = Q( pk__in = [ti.alumne.pk for ti in professor.tutorindividualitzat_set.all() ]  )
        else:
            consulta_alumnes = Q( grup =  grup )           
        
        for alumne in Alumne.objects.filter(consulta_alumnes ):
            
            filera = []
            
            #-moment--------------------------------------------
            camp = tools.classebuida()
            camp.enllac = None
            camp.contingut = unicode(alumne)
            camp.enllac = "/tutoria/detallTutoriaAlumne/{0}/dades".format( alumne.pk )
            filera.append(camp)

            q_hores =  Q(impartir__dia_impartir__lte = dataFinsA)
            if dataDesDe:
                q_hores &=  Q(impartir__dia_impartir__gte = dataDesDe)

            controls = alumne.controlassistencia_set.filter( q_hores )

                #-faltes--------------------------------------------
            f = controls.filter( alumne = alumne, estat__codi_estat = 'F' ).distinct().count() 
            r = controls.filter( alumne = alumne, estat__codi_estat = 'R' ).distinct().count() 
            if settings.CUSTOM_NO_CONTROL_ES_PRESENCIA:
                p = controls.filter( alumne = alumne).filter( Q(estat__codi_estat__in = ['P','O']) | Q(estat__codi_estat__isnull=True) ).distinct().count()
            else:
                p = controls.filter( alumne = alumne, estat__codi_estat__in = ['P','O'] ).distinct().count()
            j = controls.filter( alumne = alumne, estat__codi_estat = 'J' ).distinct().count() 
            #ca = controls.filter(q_hores).filter(estat__codi_estat__isnull = False).filter( alumne = alumne ).distinct().count()
    
                #-%--------------------------------------------
            tpc_injust = (1.0*f) * 100.0 / (0.0+f+r+p+j)  if (f+r+p+j) > 0 else 0
            tpc_assist = (0.0 + p + r ) * 100.0 / (0.0+f+r+p+j)  if (f+r+p+j) > 0 else 0
            
            camp = tools.classebuida()
            camp.enllac = None
            accio_list = [ (u'f: {0}'.format( f ), "/tutoria/detallTutoriaAlumne/{0}/assistencia".format( alumne.pk ) if f else None ), 
                           (u'j: {0}'.format( j ) , "/tutoria/detallTutoriaAlumne/{0}/assistencia".format( alumne.pk ) if j else None  ),  
                           (u'r: {0}'.format( r ) , "/tutoria/detallTutoriaAlumne/{0}/assistencia".format( alumne.pk ) if r else None  ),  
                           (u'p: {0}'.format( p ) , None ),  
                           (u'{0:.2f}%Injust'.format( tpc_injust ) , "/tutoria/detallTutoriaAlumne/{0}/assistencia".format( alumne.pk ) if f or j or r else None  ),
                           (u'{0:.2f}%Assist'.format( tpc_assist ) , "/tutoria/detallTutoriaAlumne/{0}/assistencia".format( alumne.pk ) if tpc_assist else None  ),
                         ] 
            camp.multipleContingut = accio_list
            filera.append(camp)


            #-disciplina--------------------------------------------
            nIncidencies = alumne.incidencia_set.filter( tipus__es_informativa = False).count()
            nIncidenciesInform = alumne.incidencia_set.filter( tipus__es_informativa = True).count()
            nExpulsions = alumne.expulsio_set.exclude( estat = 'ES').exclude( es_expulsio_per_acumulacio_incidencies = True  ).count()                
            nExpulsionsAcu = alumne.expulsio_set.exclude( estat = 'ES').filter( es_expulsio_per_acumulacio_incidencies = True  ).count()                
            camp = tools.classebuida()
            camp.enllac = "/tutoria/detallTutoriaAlumne/{0}/incidencies".format( alumne.pk ) if (nExpulsions + nExpulsionsAcu + nIncidencies+nIncidenciesInform)>0 else ''
            camp.multipleContingut = [ (u'''Exp:{0}(+{1}acu)'''.format( nExpulsions, nExpulsionsAcu), None ),
                                       (u'Inc:{0}'.format(nIncidencies), None ),
                                       (u'Obs:{0}'.format(nIncidenciesInform), None ),
                                     ]
            filera.append(camp)

            #-Actuacions--------------------------------------------
            nActuacions = alumne.actuacio_set.all().count()
            camp = tools.classebuida()
            camp.enllac = "/tutoria/detallTutoriaAlumne/{0}/actuacions".format( alumne.pk ) if nActuacions > 0 else ''
            camp.contingut = u'Act:{0}'.format(nActuacions)
            filera.append(camp)

            #-Familia--------------------------------------------
            nConnexions = 0
            try:
                nConnexions = alumne.user_associat.LoginUsuari.filter(exitos=True).count()
            except:
                pass  
            camp = tools.classebuida()
            camp.enllac = "/tutoria/detallTutoriaAlumne/{0}/families".format( alumne.pk ) if nConnexions > 0 else ''
            camp.contingut = u'Actiu:{0} Connexions:{1}'.format(u'Sí' if alumne.esta_relacio_familia_actiu() else u'No', nConnexions)
            filera.append(camp)

            #-Seguiment--------------------------------------------
            camp = tools.classebuida()
            anys_seguiment_tutorial =  []
            try:
                anys_seguiment_tutorial = SeguimentTutorialRespostes.objects.filter( 
                                                        seguiment_tutorial__alumne = alumne  ).values_list('any_curs_academic', flat=True).distinct()     
            except:
                pass
            if anys_seguiment_tutorial:
                camp.enllac = "/tutoria/detallTutoriaAlumne/{0}/seguiment".format( alumne.pk )
                camp.contingut = u'{0}'.format( u', '.join( [unicode(x) for x in  anys_seguiment_tutorial ]) )
            filera.append(camp)
            
            #-Històric--------------------------------------------
            camp = tools.classebuida()
            anys_seguiment_tutorial =  []
            try:
                anys_historic = ResumAnualAlumne.objects.filter( 
                                                        seguiment_tutorial__alumne = alumne  ).values_list('curs_any_inici', flat=True).distinct()     
            except:
                pass
            if anys_historic:
                camp.enllac = "/tutoria/detallTutoriaAlumne/{0}/historic".format( alumne.pk )
                camp.contingut = u'{0}'.format( u', '.join( [unicode(x) for x in  anys_historic ]) )
            filera.append(camp)
            
            #-Qualitativa---------------
            camp = tools.classebuida()
            teDadesDeQualitativa = alumne.respostaavaluacioqualitativa_set.count() > 0

            if teDadesDeQualitativa:
                camp.enllac = "/tutoria/detallTutoriaAlumne/{0}/qualitativa".format( alumne.pk )
                camp.contingut = u'2010'
            llistaDates = [ r.qualitativa.data_tancar_avaluacio.strftime( '%d/%m/%Y' ) 
                                           for r in alumne.respostaavaluacioqualitativa_set.all() ] 
            camp.contingut =u','.join( list( set(  llistaDates ) ) )
            filera.append( camp )
            
            #-All---------------
            camp = tools.classebuida()
           
            camp.enllac = "/tutoria/detallTutoriaAlumne/{0}/all".format( alumne.pk )
            camp.contingut = u'Informe'

            filera.append(camp)
            
            #--
            taula.fileres.append( filera )            
        report.append(taula)
        
    return report
    
    
        
        
