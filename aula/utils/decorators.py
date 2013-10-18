#This Python file uses the following encoding: utf-8
from django.contrib.auth.models import Group
from django.http import Http404

def group_required(groups=[]):
    def decorator(func):
        def inner_decorator(request,*args, **kwargs):
            
            for group in groups:
                #per millorar aquest codi,
                #un dia, quan estigui de caxondeo, cal fer dos conjunts:
                # c1 = grups de l'usuari
                # c2 = grups que poden entrar
                #i retornar cert si la intersecció no es buida.
                try:
                    if Group.objects.get(name=group) in request.user.groups.all():
                        return func(request, *args, **kwargs)
                except Group.DoesNotExist:
                    raise Exception(u"{0} no existeix".format( group ) )
            
            raise Http404()
        
        from django.utils.functional import wraps        
        return wraps(func)(inner_decorator)
    
    return decorator

