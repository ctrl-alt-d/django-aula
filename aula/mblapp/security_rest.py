# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
from rest_framework import permissions
from django.conf import settings


class EsUsuariDeLaAPI(permissions.BasePermission):
    """
    Custom permission to only allow usuaris vinculats a un estudiant.
    """

    def has_permission(self, request, view):
        sense_restriccions_acces = settings.ACCES_RESTRINGIT_A_GRUPS is None
        api_pot_entrar = ( sense_restriccions_acces
                           or ( not sense_restriccions_acces and "API" in settings.ACCES_RESTRINGIT_A_GRUPS )
                         )
        return (bool(request.user) and
                request.user.is_authenticated and
                request.user.alumne_app_set.exists() and
                request.user.groups.filter(name="API").exists() and
                api_pot_entrar
                )