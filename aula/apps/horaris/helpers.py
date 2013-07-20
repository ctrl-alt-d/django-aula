# This Python file uses the following encoding: utf-8

#comprova si un dia és festiu. Funciona encara que no li passem curs.    
from aula.apps.horaris.models import Festiu

def esFestiu( curs, dia, hora ):
    #festiu per tots:
    from django.db.models import Q

    #
    #comprovo si es festa:
    #
    q_festiu_curs_o_tots =   Q( curs__isnull = True) 
    if curs:
        q_festiu_curs_o_tots |=Q( curs = curs ) 
    
    q_ini = Q(data_inici_festiu__lt = dia) | ( Q(data_inici_festiu = dia) &Q(franja_horaria_inici__hora_inici__lte = hora.hora_inici) )
    q_fin = Q(data_fi_festiu__gt = dia) | ( Q(data_fi_festiu = dia) &Q(franja_horaria_fi__hora_inici__gte = hora.hora_inici) )

    
    if Festiu.objects.filter( q_ini & q_fin & q_festiu_curs_o_tots ).count() > 0: return True
    
    #
    #comprovo si és fora del curs
    #
    if curs and curs.data_inici_curs and curs.data_fi_curs:
        data_inici_curs = curs.data_inici_curs
        data_fi_curs   = curs.data_fi_curs
        
        mig = data_inici_curs <= dia <= data_fi_curs
        return not mig     

    return False