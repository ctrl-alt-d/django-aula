# This Python file uses the following encoding: utf-8
from aula.utils import tools
from datetime import date
from aula.utils.menu import calcula_menu
from aula.utils.tools import calculate_my_time_off


def dades_basiques(request):

    (user, l4) = tools.getImpersonateUser(request)
    sessioImpersonada = tools.sessioImpersonada(request)

    my_timeoff = calculate_my_time_off(request.user)
    return {
            'data': date.today(),
            'user': user,
            'l4': l4,
            'sessioImpersonada': sessioImpersonada,
            'menu': calcula_menu( user, request.path_info, sessioImpersonada, request ),
            'my_timeoff': my_timeoff,
            'my_safe_timeoff': my_timeoff - 10 if bool(my_timeoff) else my_timeoff,
            'es_direccio_o_impersonat': sessioImpersonada or user.groups.filter( name=u"direcció" ),
             }
    

        
        
