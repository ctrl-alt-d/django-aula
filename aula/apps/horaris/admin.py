# This Python file uses the following encoding: utf-8

from aula.apps.horaris.models import FranjaHoraria, DiaDeLaSetmana, Festiu, Horari

from django.contrib import admin

#nivell---
class HorariInline(admin.TabularInline):
    model = Horari

class DiaDeLaSetmanaAdmin(admin.ModelAdmin):
    inlines = [
        #HorariInline,
    ]

class HorariAdmin(admin.ModelAdmin):
    list_filter = ( 'professor__username', )   #TODO: Revisar

admin.site.register(FranjaHoraria)
admin.site.register(DiaDeLaSetmana,DiaDeLaSetmanaAdmin)
admin.site.register(Festiu)
admin.site.register(Horari,HorariAdmin)


