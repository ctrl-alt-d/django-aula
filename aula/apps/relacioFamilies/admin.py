# This Python file uses the following encoding: utf-8

from aula.apps.relacioFamilies.models import Responsable
from django.contrib import admin

class ResponsableAdmin(admin.ModelAdmin):
    model = Responsable
    search_fields = ['dni', 'nom', 'cognoms']
    readonly_fields = ['user_associat', 'alumnes_associats']

admin.site.register(Responsable, ResponsableAdmin)
