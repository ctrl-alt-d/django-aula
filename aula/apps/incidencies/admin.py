from django.contrib import admin

from aula.apps.incidencies.models import (
    FrassesIncidenciaAula,
    TipusIncidencia,
    TipusSancio,
)


class FraseInline(admin.TabularInline):
    model = FrassesIncidenciaAula
    extra = 3


class TipusIncidenciaAdmin(admin.ModelAdmin):
    inlines = [FraseInline]


admin.site.register(TipusIncidencia, TipusIncidenciaAdmin)

admin.site.register(TipusSancio)
