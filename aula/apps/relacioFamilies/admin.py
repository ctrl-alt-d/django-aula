# This Python file uses the following encoding: utf-8

from django.contrib import admin

from aula.apps.relacioFamilies.models import Responsable


class ResponsableAdmin(admin.ModelAdmin):
    model = Responsable
    list_display = ["cognoms", "nom", "dni"]
    search_fields = ["cognoms", "nom", "dni"]
    readonly_fields = ["user_associat", "alumnes_associats"]


admin.site.register(Responsable, ResponsableAdmin)
