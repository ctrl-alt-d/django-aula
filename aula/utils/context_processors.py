# This Python file uses the following encoding: utf-8
from aula.utils import tools
from django.utils.datetime_safe import date
from aula.utils.menu import calcula_menu

def dades_basiques(request):

    (user, l4) = tools.getImpersonateUser(request)
    sessioImpersonada = tools.sessioImpersonada(request)
        
    return {
            'data': date.today(),
            'user': user,
            'l4': l4,
            'sessioImpersonada': sessioImpersonada,
            'menu': calcula_menu( user, request.path_info ),
             }
    

        
        
