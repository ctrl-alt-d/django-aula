#This Python file uses the following encoding: utf-8
from django.contrib.auth.models import Group
from django.http import Http404

def group_required(groups=[]):
    def decorator(func):
        def inner_decorator(request,*args, **kwargs):
            
            for group in groups:
                if Group.objects.get(name=group) in request.user.groups.all():
                    return func(request, *args, **kwargs)
            
            
            raise Http404()
        
        from django.utils.functional import wraps        
        return wraps(func)(inner_decorator)
    
    return decorator

