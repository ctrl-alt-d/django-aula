# This Python file uses the following encoding: utf-8

from aula.apps.matricula.models import Matricula, Document
from django.contrib import admin

class DocumentInLine(admin.TabularInline):
    model = Document
    fields = ('fitxer',)
    extra = 0

class MatriculaAdmin(admin.ModelAdmin):
    inlines = [
        DocumentInLine,
    ]
    model = Matricula
    list_filter = ['curs', 'any',]
    list_display= ['idAlumne', 'cognoms', 'nom', 'curs', 'any',]
    search_fields = ['idAlumne', 'cognoms', 'nom',]
    
class DocumentAdmin(admin.ModelAdmin):
    model=Document
    list_display= ['fitxer',]
    search_fields = ['fitxer',]
    
admin.site.register(Matricula, MatriculaAdmin)
admin.site.register(Document, DocumentAdmin)
