# This Python file uses the following encoding: utf-8

from django.contrib import admin

from aula.apps.horaris.models import DiaDeLaSetmana, Festiu, FranjaHoraria, Horari


# nivell---
class HorariInline(admin.TabularInline):
    model = Horari


class DiaDeLaSetmanaAdmin(admin.ModelAdmin):
    inlines = [
        # HorariInline,
    ]


class HorariAdmin(admin.ModelAdmin):
    list_filter = ("professor__username",)  # TODO: Revisar


admin.site.register(FranjaHoraria)
admin.site.register(DiaDeLaSetmana, DiaDeLaSetmanaAdmin)
admin.site.register(Festiu)
admin.site.register(Horari, HorariAdmin)
