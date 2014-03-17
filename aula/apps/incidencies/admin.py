from aula.apps.incidencies.models import FrassesIncidenciaAula
#tipusIncidencia
from aula.apps.incidencies.abstract_models import TipusIncidencia 
from django.contrib import admin

#tipusIncidencia

#admin.site.register(FrassesIncidenciaAula)

class FraseInline(admin.TabularInline):
    model = FrassesIncidenciaAula
    extra = 3

class TipusIncidenciaAdmin(admin.ModelAdmin):
    inlines = [FraseInline]

admin.site.register(TipusIncidencia, TipusIncidenciaAdmin)


