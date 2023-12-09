# This Python file uses the following encoding: utf-8
from aula.apps.presencia.models import Impartir, EstatControlAssistencia
from aula.apps.alumnes.models import Alumne
from aula.apps.tutoria.models import ResumAnualAlumne, SeguimentTutorial

def calculaResumAnualProcess():
    linia = '\n-----------------------------------------------------\n'
    curs = Impartir.objects.order_by( 'dia_impartir' )[0].dia_impartir.year
    for a in Alumne.objects.all():
        seguiment = a.get_seguiment_tutorial()

            
        resum, _ = ResumAnualAlumne.objects.get_or_create( seguiment_tutorial = seguiment, curs_any_inici = curs )
        #incidències
        txt_incidencies = u'Núm. Incidències: {0}\n'.format( a.incidencia_set.filter(tipus__es_informativa = False).count() )
        
        #expulsions
        txt_expulsions = u"Núm. Expulsions: {0}\nNúm. Expulsions per acumulació d'incidències {1}\n".format( 
                                                          a.expulsio_set.filter(  ).count() ,
                                                          a.expulsio_set.filter( es_expulsio_per_acumulacio_incidencies = False ).count()
                                                          )
        
        #sancions
        txt_sancions = u"Núm. Sancions: {0}\n".format( a.sancio_set.count() )
        
        #presencia        
        absent = EstatControlAssistencia.objects.filter( codi_estat__in = ['F'] )
        justificades = EstatControlAssistencia.objects.filter( codi_estat__in = ['J'] )
        faltes_no_justificades = a.controlassistencia_set.filter( estat__in = absent).count() 
        numero_de_controls = a.controlassistencia_set.filter( estat__isnull = False).count()
        
        txt_presencia  = u'Total classes: {0}\n'.format( numero_de_controls )
        txt_presencia += u'Total faltes no justificades: {0}\n'.format( faltes_no_justificades )
        txt_presencia += u'Total faltes justificades: {0}\n'.format( a.controlassistencia_set.filter( estat__in = justificades).count() )
        txt_presencia += u'Percentatge assistència: {0:.2f}%\n'.format( 
                                                            (100 - faltes_no_justificades * 100.0 /  numero_de_controls  ) if numero_de_controls !=0 
                                                            else 0
                                                                 )
        
        #actuacions
        txt_actuacions = '\n'        
        txt_actuacions += linia.join( [u"""
        Data: {0}
        Assumpte: {1}
        Professional: {2}
        Actuació amb: {3}
        En Concepte de: {4}
        Text: {5}
        
        """.format(   act.moment_actuacio,
                      act.get_assumpte_display(),
                      act.professional,
                      act.get_qui_fa_actuacio_display(),
                      act.get_amb_qui_es_actuacio_display(),
                      act.actuacio
                      ) for act in a.actuacio_set.all() ]
                   )
                    
        #qualitativa
        txt_qualitativa = '\n' + linia        
        txt_qualitativa += '\n'.join( [u"""Assignatura: {0}, Professor: {1} - {2}""".format(   r.assignatura,
                      r.professor,
                      r.item
                      ) for r in a.respostaavaluacioqualitativa_set.order_by( 'assignatura')]
                   )

        
        resum.text_resum = txt_presencia + txt_incidencies + txt_expulsions + txt_sancions + txt_actuacions + txt_qualitativa
        resum.save()

    
    