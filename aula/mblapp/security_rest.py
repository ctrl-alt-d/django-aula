# This Python file uses the following encoding: utf-8
from __future__ import unicode_literals

from django.conf import settings
from rest_framework import permissions
from aula.apps.alumnes.models import Alumne


class EsUsuariDeLaAPI(permissions.BasePermission):
    """
    Només permet responsables vinculats a un alumne/a o alumnes majors de 18 anys.
    """

    def has_permission(self, request, view):
        alumne_id = view.kwargs.get('alumne_id')
        # comprovar si l'alumne pertany al responsable
        alumnes_del_responsable = request.user.responsable.alumnes_associats.values_list('id', flat=True)
        alumne_pertany_a_responsable = alumne_id is not None and int(alumne_id) in alumnes_del_responsable
        
        #comprovar si l'alumne és major de 18 anys
        alumne = Alumne.objects.get(id=alumne_id) if alumne_id else None
        edad = alumne.edat() if alumne else None
        alumne_es_major_de_18 = edad is not None and edad >= 18
        
        return (
            bool(request.user)
            and request.user.is_authenticated
            and (alumne_pertany_a_responsable or alumne_es_major_de_18)
        )
