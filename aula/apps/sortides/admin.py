# This Python file uses the following encoding: utf-8

from aula.apps.sortides.models import Quota, TPV, TipusQuota
from django.contrib import admin

admin.site.register(TipusQuota)
admin.site.register(Quota)
admin.site.register(TPV)
