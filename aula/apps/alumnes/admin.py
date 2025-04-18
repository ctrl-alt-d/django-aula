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
    fields = ('nom', 'cognoms','correu','telefons','tutors')
    extra = 0
    def delete(self):
        return "No es poden esborrar alumnes manualment"



class GrupAdmin(admin.ModelAdmin):
    inlines = [
        AlumnesInLine,
    ]
    def delete(self):
        return "No es poden esborrar alumnes manualment"

#alumne ----

class AlumneAdmin(admin.ModelAdmin):
    model = Alumne
    list_filter = ['grup']
    list_display= ['cognoms', 'nom', 'grup']
    search_fields = ['cognoms', 'nom']
    #DEPRECATED vvv
    exclude = ['correu_tutors',
               'correu_relacio_familia_pare',
               'correu_relacio_familia_mare',
               'tutors_volen_rebre_correu',
               'telefons',
               'tutors',
               'rp1_nom','rp1_telefon','rp1_mobil','rp1_correu',
               'rp2_nom','rp2_telefon','rp2_mobil','rp2_correu',
               'primer_responsable',
               'relacio_familia_darrera_notificacio',
               ]
    #DEPRECATED ^^^

admin.site.register(Nivell,NivellAdmin)
admin.site.register(Curs,CursAdmin)
admin.site.register(Grup,GrupAdmin)
admin.site.register(Alumne,AlumneAdmin)


