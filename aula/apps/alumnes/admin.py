# This Python file uses the following encoding: utf-8

from aula.apps.alumnes.models import Nivell, Curs, Grup, Alumne
from django.contrib import admin

#nivell---
class CursInline(admin.TabularInline):
    model = Curs

class NivellAdmin(admin.ModelAdmin):
    inlines = [
        CursInline,
    ]

#curs---
class GrupsInline(admin.TabularInline):
    model = Grup


class CursAdmin(admin.ModelAdmin):
    inlines = [
        GrupsInline,
    ]

#grup ----

class AlumnesInLine(admin.TabularInline):
    model = Alumne
    fields = ('nom', 'cognoms','tutors_volen_rebre_correu','telefons','tutors')
    extra = 0
    def delete(self):
        return "No es poden esborrar alumnes manualment"



class GrupAdmin(admin.ModelAdmin):
    inlines = [
        AlumnesInLine,
    ]
    def delete(self):
        return "No es poden esborrar alumnes manualment"



admin.site.register(Nivell,NivellAdmin)
admin.site.register(Curs,CursAdmin)
admin.site.register(Grup,GrupAdmin)
admin.site.register(Alumne)


