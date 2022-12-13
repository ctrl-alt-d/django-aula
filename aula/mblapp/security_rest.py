# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals
from rest_framework import permissions


class EsUsuariDeLaAPI(permissions.BasePermission):
    """
    Custom permission to only allow usuaris vinculats a un estudiant.
    """

    def has_permission(self, request, view):
        return (bool(request.user) and
                request.user.is_authenticated and
                request.user.alumne_app_set.exists() and
                request.user.groups.filter(name="API").exists()
                )