# This Python file uses the following encoding: utf-8
from aula.utils import tools
from aula.apps.alumnes.models import Alumne


def alertaAssitenciaReport( data_inici, data_fi, nivell, tpc , ordenacio ):
    report = []

    
    taula = tools.classebuida()
    
    taula.titol = tools.classebuida()
    taula.titol.contingut = u'Ranking absència alumnes nivell {0}'.format( nivell )
    taula.capceleres = []
    
    capcelera = tools.classebuida()
    capcelera.amplade = 300
    capcelera.contingut = u'Alumne'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'hores absent no justificat'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'hores docència'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 100
    capcelera.contingut = u'%absència no justificada (absènc.no.justif./docència)'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'hores present'
    taula.capceleres.append( capcelera )

    capcelera = tools.classebuida()
    capcelera.amplade = 70
    capcelera.contingut = u'hores absènc. justif.'
    taula.capceleres.append( capcelera )


    taula.fileres = []
    
    #----------------------
    #choices = ( ('a', u'Nom alumne',), ('ca', u'Curs i alumne',),('n',u'Per % Assistència',), ('cn',u'Per Curs i % Assistència',),

    order_a = '''   a.cognoms,a.nom '''

    order_ca = '''   1.0 * coalesce ( count( f.id_control_assistencia ), 0 ) /
                    coalesce ( count( ca.id_control_assistencia ), 0 ) 
                   desc '''
 
    order_ca = ''' c.nom_curs, g.nom_grup, a.cognoms ,a.nom '''
 
    order_n = '''   tpc desc '''

    order_cn = '''   c.nom_curs, g.nom_grup, tpc desc '''

    order = order_ca if ordenacio == 'ca' else order_n if ordenacio == 'n' else order_cn if ordenacio == 'cn' else order_a

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
                  {4}
                '''.format( nivell.pk, data_inici, data_fi, tpc, order   )
    
    
    #for alumne in  Alumne.objects.raw( sql ):        TODO
    for alumne in  Alumne.objects.all()[:100]:   
            
                
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