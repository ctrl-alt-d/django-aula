from aula.apps.assignatures.models import TipusDAssignatura, Assignatura
from django.contrib import admin

class AssignaturaAdmin(admin.ModelAdmin):
    model = Assignatura
    list_display= ['codi_assignatura', 'nom_assignatura', 'curs', 'tipus_assignatura']
    list_filter = ['curs', 'tipus_assignatura']

admin.site.register(TipusDAssignatura)
admin.site.register(Assignatura, AssignaturaAdmin)