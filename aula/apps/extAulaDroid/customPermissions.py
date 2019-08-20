from rest_framework import permissions
from django.http import HttpRequest
from django.contrib.auth.models import User, Group
from django.core.exceptions import ObjectDoesNotExist

class ProfesAccessPermission(permissions.BasePermission):
    message = 'No pots accedir si no pertanys al grup professors.'

    def has_permission(self, request: HttpRequest, view):
        user: User = User.objects.get(pk=request.user.pk)
        try:
            group: Group = user.groups.get(name='professors')
            return True
        except ObjectDoesNotExist:
            return False
        