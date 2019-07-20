# This Python file uses the following encoding: utf-8
from aula.utils import tools
from aula.utils.tools import unicode
from aula.apps.alumnes.models import Alumne
from aula.apps.presencia.models import ControlAssistencia
from django.db.models import Q


def faltesAssistenciaEntreDatesProfessorRpt( 
                    professor,
                    grup ,
                    assignatures ,
                    dataDesDe ,
                    horaDesDe ,
                    dataFinsA ,
                    horaFinsA ):

    q_grup = Q(impartir__horari__grup = grup)
    
    q_assignatures = Q(impartir__horari__assignatura__in = assignatures)
    
    q_professor = Q(impartir__horari__professor = professor)
    
    q_primer_dia = Q(impartir__dia_impartir = dataDesDe ) & Q(impartir__horari__hora__hora_inici__gte = horaDesDe.hora_inici)
    q_mig = Q(impartir__dia_impartir__gt = dataDesDe ) & Q(impartir__dia_impartir__lt = dataFinsA)
    q_darrer_dia = Q(impartir__dia_impartir = dataFinsA ) & Q(impartir__horari__hora__hora_fi__lte = horaFinsA.hora_fi)
    q_hores = q_primer_dia | q_mig | q_darrer_dia
    
    controls = ControlAssistencia.objects.filter( q_grup & q_assignatures & q_hores & q_professor )
    
    alumnes = Alumne.objects.filter( controlassistencia__pk__in = controls.values_list('pk', flat=True)
                                      ).distinct()
    
    report = []

    nTaula = 0
    
    #RESUM-------------------------------------------------------------------------------------------------
    taula = tools.classebuida()
    taula.codi = nTaula; nTaula+=1
    taula.tabTitle = 'Resum'
        
    taula.titol = tools.classebuida()
    taula.titol.contingut = u'Resum assistència de {0} de {1} entre {2} {3}h i {4} {5}h'.format( 
                                    grup, 
                                    ', '.join([ unicode(a) for a in assignatures ]),
                                    dataDesDe.strftime( '%d/%m/%Y' )  ,
                                    horaDesDe.hora_inici.strftime( '%H:%M' ),
                                    dataFinsA.strftime( '%d/%m/%Y' )  ,
                                    horaFinsA.hora_fi.strftime( '%H:%M' )
                                     )
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 25
    capcelera.contingut = u'Alumne'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 18
    capcelera.contingut = u'hores absent no justificat'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 12
    capcelera.contingut = u'hores docència'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 5
    capcelera.contingut = u'%assist.'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'hores present'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade =15
    capcelera.contingut = u'hores absènc. justif.'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'hores retard'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 5
    capcelera.contingut = u'%injustif.'
    taula.capceleres.append( capcelera )

    taula.fileres = []
    
    for alumne in  alumnes:
                
        filera = []
        
        #-nom--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = ''
        camp.contingut = unicode(alumne) + ' (' + unicode(alumne.grup) + ')'
        filera.append(camp)

        #-faltes--------------------------------------------
        f = controls.filter( alumne = alumne, estat__codi_estat = 'F' ).distinct().count()
        j = controls.filter( alumne = alumne, estat__codi_estat = 'J' ).distinct().count()        
        camp = tools.classebuida()
        camp.contingut = unicode(f) 
        filera.append(camp)

        #-controls--------------------------------------------
        ca = controls.filter( alumne = alumne, estat__codi_estat__isnull = False ).distinct().count()
        camp = tools.classebuida()
        camp.contingut = unicode(ca) 
        filera.append(camp)

        #-% assistència --------------------------------------------
        tpc = 1.0 - (1.0*( f + j ) ) / (1.0*ca) if ca != 0 else 'N/A'   
        camp = tools.classebuida()
        camp.contingut =u'{0:.2f}%'.format(tpc * 100) if isinstance( tpc, float ) else 'N/A'
        filera.append(camp)
        
        #-present--------------------------------------------
        p = controls.filter( alumne = alumne, estat__codi_estat = 'P' ).distinct().count()
        camp = tools.classebuida()
        camp.contingut = unicode(p) 
        filera.append(camp)

        #-justif--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = unicode(j)
        filera.append(camp)

        #-retard--------------------------------------------
        j = controls.filter( alumne = alumne, estat__codi_estat = 'R' ).distinct().count()
        camp = tools.classebuida()
        camp.contingut = unicode(j)
        filera.append(camp)

        #-% insjustif --------------------------------------------
        tpc = (1.0 * f  ) / (1.0*ca) if ca != 0 else 'N/A'   
        camp = tools.classebuida()
        camp.contingut =u'{0:.2f}%'.format(tpc * 100) if isinstance( tpc, float ) else 'N/A'
        filera.append(camp)
        


        taula.fileres.append( filera )

    report.append(taula)


    #DETALL-------------------------------------------------------------------------------------------------
    taula = tools.classebuida()
    taula.codi = nTaula; nTaula+=1
    taula.tabTitle = 'Detall'
    
    taula.titol = tools.classebuida()
    taula.titol.contingut = u'Detall assistència de {0} de {1} entre {2} {3}h i {4} {5}h'.format( 
                                    grup, 
                                    ', '.join([ unicode(a) for a in assignatures ]),
                                    dataDesDe.strftime( '%d/%m/%Y' )  ,
                                    horaDesDe.hora_inici.strftime( '%H:%M' ),
                                    dataFinsA.strftime( '%d/%m/%Y' )  ,
                                    horaFinsA.hora_fi.strftime( '%H:%M' )
                                     )
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 40
    capcelera.contingut = u'Alumne'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 30
    capcelera.contingut = u'hores absent no justificat'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 30
    capcelera.contingut = u'hores absènc. justif.'
    taula.capceleres.append( capcelera )


    taula.fileres = []
    

    for alumne in  alumnes:
                
        filera = []
        
        #-nom--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = ''
        camp.contingut = unicode(alumne) + ' (' + unicode(alumne.grup) + ')'
        filera.append(camp)

        #-faltes--------------------------------------------
        f = controls.filter( alumne = alumne, estat__codi_estat = 'F' ).distinct().select_related('impartir','impartir__horari__hora', 'impartir__horari__assignatura')

        camp = tools.classebuida()
        camp.contingut = unicode( 
                           u' | '.join( 
                                 [ u'{0} {1} {2}'.format(x.impartir.dia_impartir.strftime( '%d/%m/%Y' )  , x.impartir.horari.hora, x.impartir.horari.assignatura) 
                                   for x in f ] 
                                     )
                                 ) 
        filera.append(camp)

        #-justif--------------------------------------------
        j = controls.filter( alumne = alumne, estat__codi_estat = 'J' ).distinct()
        camp = tools.classebuida()
        contingut = [ u'{0} {1} {2}'.format(x.impartir.dia_impartir.strftime( '%d/%m/%Y' )  , x.impartir.horari.hora, x.impartir.horari.assignatura) 
                                   for x in j ] 
        camp.multipleContingut =  [ ( c, None,) for c in contingut ]
                                 
                                  
        filera.append(camp)



        taula.fileres.append( filera )

    report.append(taula)
    
    return report
        
    


def alertaAssitenciaReport( data_inici, data_fi, nivell, tpc ):
    report = []

    taula = tools.classebuida()
    
    taula.titol = tools.classebuida()
    taula.titol.contingut = u'Ranking absència alumnes nivell {0}'.format( nivell )
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 40
    capcelera.contingut = u'Alumne'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 15
    capcelera.contingut = u'hores absent no justificat'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'hores docència'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'%absència no justificada (absènc.no.justif./docència)'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 10
    capcelera.contingut = u'hores present'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 15
    capcelera.contingut = u'hores absènc. justif.'
    taula.capceleres.append( capcelera )


    taula.fileres = []


    sql = u'''select                                    TODO!!! PASSAR A QUERY API!!!!!!
                   a.id_alumne, 
                   coalesce ( count( ca.id_control_assistencia ), 0 ) as ca,
                   coalesce ( count( p.id_control_assistencia ), 0 ) as p,
                   coalesce ( count( j.id_control_assistencia ), 0 ) as j,
                   coalesce ( count( f.id_control_assistencia ), 0 ) as f,
                   1.0 * coalesce ( count( f.id_control_assistencia ), 0 ) /
                      ( coalesce ( count( ca.id_control_assistencia ), 0 ) ) as tpc                   
                from 
                   alumne a 

                   inner join
                   grup g
                       on (g.id_grup = a.id_grup )

                   inner join
                   curs c
                       on (c.id_curs = g.id_curs)
                
                   inner join
                   nivell n
                       on (n.id_nivell = c.id_nivell)

                   inner join 
                   control_assistencia ca 
                       on (ca.id_estat is not null and 
                           ca.id_alumne = a.id_alumne )

                   inner join
                   impartir i
                       on ( i.id_impartir = ca.id_impartir )
                   
                   left outer join 
                   control_assistencia p
                       on ( 
                           p.id_estat in ( select id_estat from estat_control_assistencia where codi_estat in ('P','R' ) ) and
                           p.id_control_assistencia = ca.id_control_assistencia )

                   left outer join 
                   control_assistencia j
                       on ( 
                           j.id_estat = ( select id_estat from estat_control_assistencia where codi_estat = 'J' ) and
                           j.id_control_assistencia = ca.id_control_assistencia )

                   left outer join 
                   control_assistencia f
                       on ( 
                           f.id_estat = ( select id_estat from estat_control_assistencia where codi_estat = 'F' ) and
                           f.id_control_assistencia = ca.id_control_assistencia )

                where 
                    n.id_nivell = {0} and
                    i.dia_impartir >= '{1}' and
                    i.dia_impartir <= '{2}'

                group by 
                   a.id_alumne
                     
                having
                   1.0 * coalesce ( count( f.id_control_assistencia ), 0 ) /
                     coalesce ( count( ca.id_control_assistencia ), 0 ) 
                   > ( 1.0 * {3} / 100)
                order by
                   1.0 * coalesce ( count( f.id_control_assistencia ), 0 ) /
                    coalesce ( count( ca.id_control_assistencia ), 0 ) 
                   desc   
                '''.format( nivell.pk, data_inici, data_fi, tpc   )
    
    
    for alumne in  Alumne.objects.raw( sql ):
            
                
        filera = []
        
        #-nom--------------------------------------------
        camp = tools.classebuida()
        camp.enllac = '/tutoria/detallTutoriaAlumne/{0}/all'.format(alumne.pk )
        camp.contingut = unicode(alumne) + ' (' + unicode(alumne.grup) + ')'
        filera.append(camp)

        #-docència--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = unicode(alumne.f) 
        filera.append(camp)

        #-present--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = unicode(alumne.ca) 
        filera.append(camp)

        #-%--------------------------------------------
        camp = tools.classebuida()
        camp.contingut =u'{0:.2f}%'.format(alumne.tpc * 100) 
        filera.append(camp)
        
        #-absent--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = unicode(alumne.p) 
        filera.append(camp)

        #-justif--------------------------------------------
        camp = tools.classebuida()
        camp.contingut = unicode(alumne.j) 
        filera.append(camp)



        taula.fileres.append( filera )

    report.append(taula)

    return report