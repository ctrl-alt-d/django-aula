# This Python file uses the following encoding: utf-8

from django.contrib import admin

from aula.apps.sortides.models import TPV, Quota, TipusQuota


class QuotaAdmin(admin.ModelAdmin):
    model = Quota
    list_filter = ["curs", "any", "tipus", "tpv"]
    search_fields = [
        "descripcio",
    ]


admin.site.register(TipusQuota)
admin.site.register(Quota, QuotaAdmin)
admin.site.register(TPV)
