# This Python file uses the following encoding: utf-8

from aula.apps.matricula.models import Peticio, Dades
from django.contrib import admin

class PeticioAdmin(admin.ModelAdmin):
    model = Peticio
    list_filter = ['curs']
    list_display= ['idAlumne', 'email', 'curs']
    search_fields = ['idAlumne', 'curs']
    
class DadesAdmin(admin.ModelAdmin):
    model = Dades
    list_display= ['cognoms', 'nom']
    search_fields = ['cognoms', 'nom']

admin.site.register(Peticio, PeticioAdmin)
admin.site.register(Dades, DadesAdmin)
